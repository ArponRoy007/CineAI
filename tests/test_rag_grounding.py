from rag.qa import answer_question


def test_empty_question():

    result = answer_question("")

    assert result["answer"] == (
        "Please ask a movie question."
    )

    assert result["sources"] == []


def test_no_context_returns_grounding_message(
    monkeypatch,
):

    import rag.qa

    monkeypatch.setattr(
        rag.qa,
        "build_context",
        lambda **kwargs: ("", []),
    )

    result = answer_question(
        "What does Roy think about this?"
    )

    assert result["answer"] == (
        "I couldn't find that in Roy's movie notes."
    )

    assert result["sources"] == []


def test_rag_answer_uses_context(
    monkeypatch,
):

    import rag.qa
    import ai.llm

    fake_context = """
SOURCE 1
Movie: Darr
Year: 1993
Zone: Bollywood
Genre: Psychological Romance/Thriller
Our Rating: 5/5
Verdict: Must Watch
Our Review: A memorable early performance.
"""

    fake_sources = [
        {
            "metadata": {
                "title": "Darr",
                "roy_rating": 5.0,
            },
            "document": fake_context,
            "distance": 0.1,
        }
    ]

    monkeypatch.setattr(
        rag.qa,
        "build_context",
        lambda **kwargs: (
            fake_context,
            fake_sources,
        ),
    )

    monkeypatch.setattr(
        ai.llm,
        "generate_answer",
        lambda **kwargs: (
            "Roy rated Darr 5/5 because of "
            "its memorable performance and "
            "strong character work."
        ),
    )

    result = answer_question(
        "Why did Roy give Darr a 5/5?",
        movie_title="Darr",
    )

    assert "Darr" in result["answer"]
    assert "5/5" in result["answer"]
    assert len(result["sources"]) == 1
    assert (
        result["sources"][0]["metadata"]["title"]
        == "Darr"
    )


def test_movie_specific_context_is_passed(
    monkeypatch,
):

    import rag.qa

    captured = {}

    def fake_build_context(**kwargs):

        captured.update(kwargs)

        return (
            "Darr review context",
            [
                {
                    "metadata": {
                        "title": "Darr"
                    },
                    "document": "Darr review",
                    "distance": 0.1,
                }
            ],
        )

    monkeypatch.setattr(
        rag.qa,
        "build_context",
        fake_build_context,
    )

    import ai.llm

    monkeypatch.setattr(
        ai.llm,
        "generate_answer",
        lambda **kwargs: "Darr answer",
    )

    answer_question(
        "Why did Roy like this movie?",
        movie_title="Darr",
    )

    assert captured["movie_title"] == "Darr"
    assert captured["top_k"] == 5