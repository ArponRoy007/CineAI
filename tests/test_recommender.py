from ai.recommender import (
    content_similarity,
    embedding_similarity,
    genre_overlap,
    rank_candidates,
    rating_score,
    recommend_similar_movies,
    score_components,
    score_recommendation,
)
from scripts.tune_recommender import SANITY_CASES


def test_scoring_prioritizes_close_same_genre_highly_rated_movie():
    close_thriller = score_recommendation(0.08, "Psychological Thriller", "Crime Thriller", 4.5)
    distant_drama = score_recommendation(0.38, "Psychological Thriller", "Family Drama", 5)
    assert close_thriller > distant_drama
    assert genre_overlap("Crime Thriller", "Psychological Thriller") > 0


def test_content_similarity_component_uses_shared_review_terms():
    assert content_similarity("A tense thriller about obsession", "A tense thriller driven by obsession") > 0.5
    assert content_similarity("A tense thriller", "A gentle musical romance") == 0


def test_embedding_similarity_component_converts_cosine_distance():
    assert embedding_similarity(0.0) == 1.0
    assert embedding_similarity(0.75) == 0.25
    assert embedding_similarity(4) == 0.0


def test_rating_component_normalizes_to_five_point_scale():
    assert rating_score(5) == 1.0
    assert rating_score(2.5) == 0.5
    assert rating_score(None) == 0.0


def test_genre_component_rewards_shared_and_related_genres():
    assert genre_overlap("Crime Thriller", "Psychological Thriller") > genre_overlap("Crime Thriller", "Romance")


def test_score_components_exposes_all_hybrid_inputs():
    components = score_components(0.1, "Tense thriller obsession", "Tense thriller obsession", "Thriller", "Crime Thriller", 4.5)
    assert set(components) == {"content_similarity", "embedding_similarity", "rating_score", "genre_preference_match", "personalization_score"}
    assert components["content_similarity"] == 1.0


def test_tuning_sanity_pairs_keep_expected_recommendation_in_top_three():
    for case in SANITY_CASES:
        ranked = rank_candidates(case["source"], case["candidates"], limit=3)
        assert case["expected_top"] in [movie["title"] for movie in ranked]


class FakeVectors:
    def __init__(self, include_source=True, count=4):
        self.include_source = include_source
        self._count = count

    def get(self, ids, include):
        return {"embeddings": [[0.1, 0.2]]} if self.include_source and ids == ["darr"] else {"embeddings": []}

    def count(self):
        return self._count

    def query(self, **_kwargs):
        return {"ids": [["darr", "baazigar", "dunki", "romance"]], "distances": [[0.0, 0.10, 0.02, 0.28]]}


class FakeMovies:
    def find(self, query, _projection):
        assert query == {"movie_id": {"$in": ["baazigar", "dunki", "romance"]}}
        return [
            {"movie_id": "baazigar", "title": "Baazigar", "genre": "Crime Thriller", "roy_rating": 4.5, "verdict": "Must Watch"},
            {"movie_id": "dunki", "title": "Dunki", "genre": "Drama", "roy_rating": 2.0, "verdict": "Don't Watch"},
            {"movie_id": "romance", "title": "Romance", "genre": "Romance", "roy_rating": 4.0, "verdict": "Good Watch"},
        ]


def test_recommendations_exclude_source_and_dont_watch_when_alternatives_exist(monkeypatch):
    import ai.recommender as recommender

    monkeypatch.setattr(recommender, "get_vector_collection", lambda: FakeVectors())
    monkeypatch.setattr(recommender, "movies_collection", FakeMovies())
    source = {"movie_id": "darr", "title": "Darr", "genre": "Psychological Thriller", "roy_rating": 5.0}

    results = recommend_similar_movies(source, limit=3)

    assert [movie["movie_id"] for movie in results] == ["baazigar", "romance"]
    assert all(movie["movie_id"] != "darr" for movie in results)
    assert all(movie["verdict"] != "Don't Watch" for movie in results)


def test_cold_start_without_source_embedding_returns_empty_list(monkeypatch):
    import ai.recommender as recommender

    monkeypatch.setattr(recommender, "get_vector_collection", lambda: FakeVectors(include_source=False))
    assert recommend_similar_movies({"movie_id": "darr", "genre": "Thriller"}) == []


def test_collection_with_fewer_than_two_movies_returns_empty_list(monkeypatch):
    import ai.recommender as recommender

    monkeypatch.setattr(recommender, "get_vector_collection", lambda: FakeVectors(count=1))
    assert recommend_similar_movies({"movie_id": "darr", "genre": "Thriller"}) == []


def test_numpy_embedding_result_is_supported(monkeypatch):
    import numpy as np
    import ai.recommender as recommender

    class NumpyVectors(FakeVectors):
        def get(self, _ids, _include):
            return {"embeddings": np.array([[0.1, 0.2]])}

    monkeypatch.setattr(recommender, "get_vector_collection", lambda: NumpyVectors(count=1))
    assert recommend_similar_movies({"movie_id": "darr", "genre": "Thriller"}) == []


def test_dont_watch_is_only_used_when_no_other_match_qualifies(monkeypatch):
    import ai.recommender as recommender

    class OnlyDontWatch:
        def find(self, _query, _projection):
            return [{"movie_id": "dunki", "title": "Dunki", "genre": "Drama", "roy_rating": 2.0, "verdict": "Don't Watch"}]

    monkeypatch.setattr(recommender, "get_vector_collection", lambda: FakeVectors())
    monkeypatch.setattr(recommender, "movies_collection", OnlyDontWatch())
    results = recommend_similar_movies({"movie_id": "darr", "genre": "Drama"}, limit=3)

    assert [movie["movie_id"] for movie in results] == ["dunki"]
