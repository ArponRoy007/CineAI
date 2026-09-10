from datetime import datetime
from time import perf_counter

from ai.personalization import (
    build_preference_profile,
    log_interaction,
    preference_match,
)
from ai.recommender import recommend_for_user
from ui.home import choose_home_movies


class AggregateCollection:
    def __init__(self, results, count=0):
        self.results = list(results)
        self.count = count
        self.pipelines = []

    def count_documents(self, query):
        return self.count

    def aggregate(self, pipeline):
        self.pipelines.append(pipeline)
        return self.results.pop(0)


def test_interaction_logging_queues_expected_document(monkeypatch):
    import ai.personalization as personalization

    captured = []
    monkeypatch.setattr(
        personalization,
        "_submit_interaction",
        captured.append,
    )

    assert log_interaction(
        {"user_id": "user-7"},
        "movie-3",
        "viewed",
    ) is True

    assert captured[0]["user_id"] == "user-7"
    assert captured[0]["movie_id"] == "movie-3"
    assert captured[0]["interaction_type"] == "viewed"
    assert isinstance(captured[0]["timestamp"], datetime)


def test_interaction_logging_ignores_anonymous_or_invalid_events(monkeypatch):
    import ai.personalization as personalization

    monkeypatch.setattr(
        personalization,
        "_submit_interaction",
        lambda _document: (
            _ for _ in ()
        ).throw(AssertionError()),
    )

    assert log_interaction(
        None,
        "movie-3",
        "viewed",
    ) is False

    assert log_interaction(
        {"user_id": "user-7"},
        "movie-3",
        "unknown",
    ) is False


def test_interaction_logging_returns_without_waiting_for_write(monkeypatch):
    import ai.personalization as personalization

    class SlowExecutor:
        def submit(self, _function, _document):
            return None

    monkeypatch.setattr(
        personalization,
        "_interaction_executor",
        SlowExecutor(),
    )

    started = perf_counter()

    for _ in range(100):
        assert log_interaction(
            {"user_id": "user-7"},
            "movie-3",
            "viewed",
        ) is True

    assert perf_counter() - started < 0.05


def test_preference_profile_aggregates_fixture_history(monkeypatch):
    import ai.personalization as personalization

    collection = AggregateCollection(
        [
            [
                {
                    "_id": "Crime Thriller",
                    "score": 7,
                },
            ],
            [
                {
                    "_id": "Bollywood",
                    "score": 5,
                },
            ],
        ],
        count=5,
    )

    monkeypatch.setattr(
        personalization,
        "interactions_collection",
        collection,
    )

    profile = build_preference_profile(
        {"user_id": "user-7"}
    )

    assert profile == {
        "ready": True,
        "interaction_count": 5,
        "genres": {
            "Crime Thriller": 7.0,
        },
        "zones": {
            "Bollywood": 5.0,
        },
    }

    # Two separate aggregation pipelines:
    # one for genres and one for zones.
    assert len(collection.pipelines) == 2

    # Both pipelines must filter by the correct user.
    assert (
        collection.pipelines[0][0]["$match"]["user_id"]
        == "user-7"
    )

    assert (
        collection.pipelines[1][0]["$match"]["user_id"]
        == "user-7"
    )

    # Both pipelines must join against the movies collection.
    assert (
        collection.pipelines[0][1]["$lookup"]["from"]
        == "movies"
    )

    assert (
        collection.pipelines[1][1]["$lookup"]["from"]
        == "movies"
    )


def test_preference_profile_stays_unready_below_threshold(monkeypatch):
    import ai.personalization as personalization

    collection = AggregateCollection(
        [
            [],
            [],
        ],
        count=4,
    )

    monkeypatch.setattr(
        personalization,
        "interactions_collection",
        collection,
    )

    profile = build_preference_profile(
        {"user_id": "user-7"}
    )

    assert profile["ready"] is False
    assert profile["interaction_count"] == 4
    assert profile["genres"] == {}
    assert profile["zones"] == {}


def test_personalized_recommendations_and_new_user_fallback():
    movies = [
        {
            "movie_id": "crime",
            "title": "Crime",
            "genre": "Crime Thriller",
            "zone": "Bollywood",
            "roy_rating": 4.0,
            "verdict": "Good Watch",
        },
        {
            "movie_id": "drama",
            "title": "Drama",
            "genre": "Drama",
            "zone": "Hollywood",
            "roy_rating": 5.0,
            "verdict": "Must Watch",
        },
        {
            "movie_id": "skip",
            "title": "Skip",
            "genre": "Crime Thriller",
            "zone": "Bollywood",
            "roy_rating": 5.0,
            "verdict": "Don't Watch",
        },
    ]

    profile = {
        "ready": True,
        "interaction_count": 5,
        "genres": {
            "Crime Thriller": 10,
        },
        "zones": {
            "Bollywood": 10,
        },
    }

    ranked = recommend_for_user(
        movies,
        profile,
    )

    assert [
        movie["movie_id"]
        for movie in ranked
    ] == [
        "crime",
        "drama",
    ]

    new_user_profile = {
        "ready": False,
        "interaction_count": 0,
        "genres": {},
        "zones": {},
    }

    assert recommend_for_user(
        movies,
        new_user_profile,
    ) == []

    fallback, personalized = choose_home_movies(
        movies,
        new_user_profile,
    )

    assert personalized is False
    assert fallback == movies[:8]

    assert preference_match(
        movies[0],
        profile,
    ) > preference_match(
        movies[1],
        profile,
    )