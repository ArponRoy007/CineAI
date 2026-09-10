"""Hybrid content-based movie recommendations backed by ChromaDB and MongoDB."""

import re

from config.settings import (
    RECOMMENDER_CONTENT_WEIGHT,
    RECOMMENDER_EMBEDDING_WEIGHT,
    RECOMMENDER_GENRE_WEIGHT,
    RECOMMENDER_PERSONALIZATION_WEIGHT,
    RECOMMENDER_RATING_WEIGHT,
)
from ai.personalization import preference_match
from rag.vector_store import get_vector_collection


RELATED_GENRES = (
    {"thriller", "mystery", "crime"},
    {"drama", "romance"},
    {"action", "adventure"},
    {"comedy", "romance"},
    {"horror", "thriller"},
)

STOPWORDS = {"a", "an", "and", "about", "at", "for", "from", "in", "is", "it", "of", "on", "or", "the", "this", "to", "with"}
movies_collection = None


def _movies_collection():
    global movies_collection
    if movies_collection is None:
        from database.mongodb import get_movies_collection

        movies_collection = get_movies_collection()
    return movies_collection


def _genre_tokens(value):
    value = str(value or "").lower()
    for separator in ("/", ",", "&", "-"):
        value = value.replace(separator, " ")
    return {token.strip() for token in value.split() if token.strip()}


def genre_overlap(source_genre, candidate_genre):
    """Return a compact genre affinity score from 0 to 1."""
    source = _genre_tokens(source_genre)
    candidate = _genre_tokens(candidate_genre)
    if not source or not candidate:
        return 0.0
    if source & candidate:
        return len(source & candidate) / len(source | candidate)
    return 0.45 if any((source & family) and (candidate & family) for family in RELATED_GENRES) else 0.0


def content_similarity(source_review, candidate_review):
    """Return lexical review affinity without requiring another model call."""
    source = {word for word in re.findall(r"[a-z]{3,}", str(source_review or "").lower()) if word not in STOPWORDS}
    candidate = {word for word in re.findall(r"[a-z]{3,}", str(candidate_review or "").lower()) if word not in STOPWORDS}
    return len(source & candidate) / len(source | candidate) if source and candidate else 0.0


def embedding_similarity(distance):
    try:
        return max(0.0, min(1.0, 1.0 - float(distance)))
    except (TypeError, ValueError):
        return 0.0


def rating_score(rating):
    try:
        return max(0.0, min(1.0, float(rating) / 5))
    except (TypeError, ValueError):
        return 0.0


def score_components(distance, source_review, candidate_review, source_genre, candidate_genre, rating, candidate=None, profile=None):
    return {
        "content_similarity": content_similarity(source_review, candidate_review),
        "embedding_similarity": embedding_similarity(distance),
        "rating_score": rating_score(rating),
        "genre_preference_match": genre_overlap(source_genre, candidate_genre),
        "personalization_score": preference_match(candidate or {"genre": candidate_genre}, profile),
    }


def score_recommendation(distance, source_genre, candidate_genre, rating, source_review="", candidate_review="", candidate=None, profile=None):
    """Calculate the configured weighted hybrid recommendation score."""
    components = score_components(distance, source_review, candidate_review, source_genre, candidate_genre, rating, candidate, profile)
    return round(
        (RECOMMENDER_CONTENT_WEIGHT * components["content_similarity"])
        + (RECOMMENDER_EMBEDDING_WEIGHT * components["embedding_similarity"])
        + (RECOMMENDER_RATING_WEIGHT * components["rating_score"])
        + (RECOMMENDER_GENRE_WEIGHT * components["genre_preference_match"])
        + (RECOMMENDER_PERSONALIZATION_WEIGHT * components["personalization_score"]),
        4,
    )


def rank_candidates(source_movie, candidates, limit=6, profile=None):
    """Score already-retrieved candidates; useful for tuning and tests."""
    scored = []
    for candidate in candidates:
        score = score_recommendation(
            candidate.get("embedding_distance"),
            source_movie.get("genre"),
            candidate.get("genre"),
            candidate.get("roy_rating"),
            source_movie.get("review_text"),
            candidate.get("review_text"),
            candidate,
            profile,
        )
        if score < 0.38:
            continue
        item = dict(candidate)
        item["recommendation_score"] = score
        scored.append(item)
    preferred = [candidate for candidate in scored if candidate.get("verdict") != "Don't Watch"]
    return sorted(preferred or scored, key=lambda item: (item["recommendation_score"], item.get("roy_rating", 0)), reverse=True)[:max(1, int(limit))]


def _source_embedding(movie):
    movie_id = str(movie.get("movie_id") or movie.get("tmdb_id") or movie.get("title") or "")
    if not movie_id:
        return None
    try:
        stored = get_vector_collection().get(ids=[movie_id], include=["embeddings"])
        embeddings = stored.get("embeddings")
        return embeddings[0] if embeddings is not None and len(embeddings) else None
    except Exception as error:
        print(f"[Recommendation Source Error] {type(error).__name__}: {error}")
        return None


def _candidate_movies(ids):
    if not ids:
        return []
    try:
        return list(_movies_collection().find({"movie_id": {"$in": ids}}, {"_id": 0}))
    except Exception as error:
        print(f"[Recommendation MongoDB Error] {type(error).__name__}: {error}")
        return []


def recommend_similar_movies(movie, limit=6, profile=None):
    """Return up to ``limit`` meaningful content-based recommendations.

    Recommendations require an existing source embedding. "Don't Watch" films
    are excluded whenever any eligible alternative exists; only an otherwise
    empty candidate pool permits that fallback.
    """
    if not isinstance(movie, dict):
        return []
    embedding = _source_embedding(movie)
    if embedding is None:
        return []
    source_id = str(movie.get("movie_id") or movie.get("tmdb_id") or movie.get("title") or "")
    try:
        collection = get_vector_collection()
        count = collection.count()
        if count < 2:
            return []
        results = collection.query(
            query_embeddings=[embedding],
            n_results=min(count, max(int(limit) * 4, 12)),
            include=["metadatas", "distances"],
        )
    except Exception as error:
        print(f"[Recommendation Search Error] {type(error).__name__}: {error}")
        return []

    ids = (results.get("ids") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]
    distance_by_id = {str(candidate_id): distance for candidate_id, distance in zip(ids, distances) if str(candidate_id) != source_id}
    candidates = _candidate_movies(list(distance_by_id))
    candidates_with_distance = []
    for candidate in candidates:
        candidate_id = str(candidate.get("movie_id") or candidate.get("tmdb_id") or "")
        if candidate_id not in distance_by_id or candidate_id == source_id:
            continue
        candidate = dict(candidate)
        candidate["embedding_distance"] = distance_by_id[candidate_id]
        candidates_with_distance.append(candidate)
    return rank_candidates(movie, candidates_with_distance, limit, profile)


def recommend_for_user(movies, profile, limit=8):
    """Rank generic candidates using inferred taste once a profile is ready."""
    if not profile or not profile.get("ready"):
        return []
    candidates = []
    for movie in movies:
        if movie.get("verdict") == "Don't Watch":
            continue
        item = dict(movie)
        item["recommendation_score"] = round(
            (rating_score(item.get("roy_rating")) * RECOMMENDER_RATING_WEIGHT)
            + (preference_match(item, profile) * RECOMMENDER_PERSONALIZATION_WEIGHT),
            4,
        )
        candidates.append(item)
    return sorted(candidates, key=lambda item: (item["recommendation_score"], item.get("roy_rating", 0)), reverse=True)[:max(1, int(limit))]
