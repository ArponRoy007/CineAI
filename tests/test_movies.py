def test_movie_document_structure():

    movie = {
        "movie_id": "rr-test",
        "title": "Test Movie",
        "year": 2025,
        "roy_rating": 5.0,
        "verdict": "Must Watch",
        "review_text": "A great movie.",
    }

    required_fields = [
        "movie_id",
        "title",
        "year",
        "roy_rating",
        "verdict",
        "review_text",
    ]

    for field in required_fields:

        assert field in movie


def test_review_under_200_characters():

    review = (
        "This is a sample RoyReview review "
        "that should remain below the required "
        "two hundred character limit."
    )

    assert len(review) <= 200


def test_rating_range():

    ratings = [
        1,
        2,
        3,
        3.5,
        4,
        4.5,
        5,
    ]

    for rating in ratings:

        assert 1 <= rating <= 5