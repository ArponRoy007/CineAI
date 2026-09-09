import pytest

from rag.hybrid import get_exact_movies, format_exact_movies


class FakeCursor:
    def __init__(self, movies):
        self.movies = movies

    def sort(self, *_args, **_kwargs):
        return self


    def __iter__(self):
        return iter(self.movies)


class FakeCollection:
    def __init__(self, movies):
        self.movies = movies

    def find(self, query, projection=None):
        results = []

        for movie in self.movies:

            if query.get("review_status") == "CONFIRMED":
                if movie.get("review_status") != "CONFIRMED":
                    continue

            if query.get("ingest_to_rag") is True:
                if movie.get("ingest_to_rag") is not True:
                    continue

            if "roy_rating" in query:
                condition = query["roy_rating"]

                if isinstance(condition, dict):

                    if movie.get("roy_rating", 0) < condition["$gte"]:
                        continue

                elif movie.get("roy_rating") != condition:
                    continue

            if "verdict" in query:
                if movie.get("verdict") != query["verdict"]:
                    continue

            results.append(movie)

        return FakeCursor(results)


@pytest.fixture
def sample_movies():
    return [
        {
            "title": "Darr",
            "year": 1993,
            "roy_rating": 5.0,
            "verdict": "Must Watch",
            "review_status": "CONFIRMED",
            "ingest_to_rag": True,
            "review_text": "A memorable thriller.",
        },
        {
            "title": "PK",
            "year": 2014,
            "roy_rating": 5.0,
            "verdict": "Must Watch",
            "review_status": "CONFIRMED",
            "ingest_to_rag": True,
            "review_text": "A thoughtful and entertaining film.",
        },
        {
            "title": "Dunki",
            "year": 2023,
            "roy_rating": 2.0,
            "verdict": "Don't Watch",
            "review_status": "CONFIRMED",
            "ingest_to_rag": True,
            "review_text": "A disappointing experience.",
        },
    ]


def test_get_exact_movies_by_rating(
    monkeypatch,
    sample_movies,
):
    import rag.hybrid

    monkeypatch.setattr(
        rag.hybrid,
        "movies_collection",
        FakeCollection(sample_movies),
    )

    movies = get_exact_movies(
        rating=5,
    )

    titles = [
        movie["title"]
        for movie in movies
    ]

    assert "Darr" in titles
    assert "PK" in titles
    assert "Dunki" not in titles


def test_get_exact_movies_by_verdict(
    monkeypatch,
    sample_movies,
):
    import rag.hybrid

    monkeypatch.setattr(
        rag.hybrid,
        "movies_collection",
        FakeCollection(sample_movies),
    )

    movies = get_exact_movies(
        verdict="Don't Watch",
    )

    assert len(movies) == 1
    assert movies[0]["title"] == "Dunki"


def test_get_exact_movies_minimum_rating(
    monkeypatch,
    sample_movies,
):
    import rag.hybrid

    monkeypatch.setattr(
        rag.hybrid,
        "movies_collection",
        FakeCollection(sample_movies),
    )

    movies = get_exact_movies(
        min_rating=4,
    )

    titles = [
        movie["title"]
        for movie in movies
    ]

    assert set(titles) == {
        "Darr",
        "PK",
    }


def test_format_exact_movies(sample_movies):

    result = format_exact_movies(
        sample_movies[:2]
    )

    assert "Darr" in result
    assert "PK" in result
    assert "5.0/5" in result


def test_format_empty_movies():

    result = format_exact_movies([])

    assert (
        "No matching movies were found"
        in result
    )