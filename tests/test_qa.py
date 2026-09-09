from rag.qa import (
    _is_exact_fact_question,
    _detect_filters,
)


def test_exact_question_detection():

    assert _is_exact_fact_question(
        "Which movies does Roy rate 5 out of 5?"
    )

    assert _is_exact_fact_question(
        "Show Roy's Don't Watch movies"
    )


def test_semantic_question_detection():

    assert not _is_exact_fact_question(
        "Why does Roy like Darr?"
    )

    assert not _is_exact_fact_question(
        "What does Roy think about the performances?"
    )


def test_detect_five_star_rating():

    rating, minimum, verdict = _detect_filters(
        "Which movies does Roy rate 5 out of 5?"
    )

    assert rating == 5
    assert minimum is None
    assert verdict is None


def test_detect_minimum_rating():

    rating, minimum, verdict = _detect_filters(
        "Which movies did Roy rate 4 or higher?"
    )

    assert rating is None
    assert minimum == 4
    assert verdict is None


def test_detect_must_watch():

    rating, minimum, verdict = _detect_filters(
        "Show Roy's Must Watch movies"
    )

    assert verdict == "Must Watch"


def test_detect_dont_watch():

    rating, minimum, verdict = _detect_filters(
        "Which movies should I avoid? Show Don't Watch movies."
    )

    assert verdict == "Don't Watch"