"""Best-effort interaction logging and Mongo-backed user preference profiles."""

from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from config.settings import MOVIES_COLLECTION_NAME, PERSONALIZATION_MIN_INTERACTIONS


INTERACTION_WEIGHTS = {
    "viewed": 1,
    "searched": 0.25,
    "asked_roy": 2,
    "favorited": 4,
}
VALID_INTERACTIONS = set(INTERACTION_WEIGHTS)
interactions_collection = None
_interaction_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="royreview-interactions")


def _collection():
    global interactions_collection
    if interactions_collection is None:
        from database.mongodb import get_user_interactions_collection

        interactions_collection = get_user_interactions_collection()
    return interactions_collection


def _user_id(user):
    return str((user or {}).get("user_id") or "").strip()


def _write_interaction(document):
    try:
        _collection().insert_one(document)
    except Exception as error:
        print(f"[Interaction Logging Error] {type(error).__name__}: {error}")


def _submit_interaction(document):
    _interaction_executor.submit(_write_interaction, document)


def log_interaction(user, movie_id, interaction_type, query=None):
    """Queue an interaction write without blocking a user-facing request."""
    user_id = _user_id(user)
    if not user_id or interaction_type not in VALID_INTERACTIONS:
        return False
    document = {
        "user_id": user_id,
        "movie_id": str(movie_id or "") or None,
        "interaction_type": interaction_type,
        "timestamp": datetime.now(timezone.utc),
    }
    if query:
        document["query"] = str(query).strip()
    try:
        _submit_interaction(document)
        return True
    except Exception as error:
        print(f"[Interaction Logging Error] {type(error).__name__}: {error}")
        return False


def build_preference_profile(user, minimum_interactions=PERSONALIZATION_MIN_INTERACTIONS):
    """Infer genre and zone preferences in MongoDB from meaningful interactions."""
    user_id = _user_id(user)
    if not user_id:
        return {"ready": False, "interaction_count": 0, "genres": {}, "zones": {}}

    base_match = {
        "user_id": user_id,
        "interaction_type": {"$in": list(VALID_INTERACTIONS)},
    }

    try:
        collection = _collection()

        # 1. Count meaningful interactions.
        interaction_count = collection.count_documents(base_match)

        # 2. Build weighted movie preferences.
        preference_pipeline = [
            {"$match": {
                **base_match,
                "movie_id": {"$ne": None},
            }},
            {
                "$lookup": {
                    "from": MOVIES_COLLECTION_NAME,
                    "localField": "movie_id",
                    "foreignField": "movie_id",
                    "as": "movie",
                }
            },
            {"$unwind": "$movie"},
            {
                "$project": {
                    "genre": "$movie.genre",
                    "zone": "$movie.zone",
                    "weight": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {
                                        "$eq": ["$interaction_type", "favorited"]
                                    },
                                    "then": 4,
                                },
                                {
                                    "case": {
                                        "$eq": ["$interaction_type", "asked_roy"]
                                    },
                                    "then": 2,
                                },
                                {
                                    "case": {
                                        "$eq": ["$interaction_type", "viewed"]
                                    },
                                    "then": 1,
                                },
                            ],
                            "default": 0.25,
                        }
                    },
                }
            },
        ]

        # 3. Aggregate genre preferences separately.
        genre_pipeline = preference_pipeline + [
            {
                "$group": {
                    "_id": "$genre",
                    "score": {"$sum": "$weight"},
                }
            },
            {"$sort": {"score": -1}},
        ]

        # 4. Aggregate zone preferences separately.
        zone_pipeline = preference_pipeline + [
            {
                "$group": {
                    "_id": "$zone",
                    "score": {"$sum": "$weight"},
                }
            },
            {"$sort": {"score": -1}},
        ]

        genre_rows = list(collection.aggregate(genre_pipeline))
        zone_rows = list(collection.aggregate(zone_pipeline))

    except Exception as error:
        print(f"[Preference Profile Error] {type(error).__name__}: {error}")
        return {
            "ready": False,
            "interaction_count": 0,
            "genres": {},
            "zones": {},
        }

    def to_scores(rows):
        return {
            str(row.get("_id")): float(row.get("score", 0))
            for row in rows
            if row.get("_id")
        }

    return {
        "ready": interaction_count >= minimum_interactions,
        "interaction_count": interaction_count,
        "genres": to_scores(genre_rows),
        "zones": to_scores(zone_rows),
    }

def preference_match(movie, profile):
    """Normalize how well a candidate matches the inferred profile."""
    if not profile or not profile.get("ready"):
        return 0.0
    genre_scores = profile.get("genres", {})
    zone_scores = profile.get("zones", {})
    genre_score = float(genre_scores.get(str(movie.get("genre", "")), 0))
    zone_score = float(zone_scores.get(str(movie.get("zone", "")), 0))
    maximum = max([1.0, *genre_scores.values(), *zone_scores.values()])
    return min(1.0, ((genre_score * 0.7) + (zone_score * 0.3)) / maximum)
