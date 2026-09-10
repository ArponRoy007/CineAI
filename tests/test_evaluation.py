from rag.evaluation import (
    FALLBACK_ANSWER,
    answer_correctness,
    answer_faithfulness,
    context_relevance,
    evaluate_case,
    hallucination_rate,
    retrieval_precision,
    retrieval_recall,
)


SOURCES = [
    {"metadata": {"title": "Tamasha"}, "document": "A story about identity dreams and love."},
    {"metadata": {"title": "PK"}, "document": "Questions about society."},
]
CONTEXT = "SOURCE 1\nMovie: Tamasha\nRoy's Review: A story about identity dreams and love."


def test_retrieval_precision_and_recall_find_the_labeled_movie():
    assert retrieval_precision(SOURCES, "Tamasha") == 0.5
    assert retrieval_recall(SOURCES, "Tamasha") == 1.0
    assert retrieval_recall(SOURCES, "Animal") == 0.0


def test_context_relevance_requires_the_expected_movie_title():
    assert context_relevance(CONTEXT, "Tamasha") == 1.0
    assert context_relevance(CONTEXT, "PK") == 0.0


def test_faithfulness_scores_grounded_terms_and_fallbacks():
    assert answer_faithfulness("Roy values identity and love.", CONTEXT) > 0.5
    assert answer_faithfulness(FALLBACK_ANSWER, "") == 1.0
    assert answer_faithfulness("It won eleven Oscars.", CONTEXT) == 0.0


def test_answer_correctness_handles_keyword_match_and_exact_fallback():
    assert answer_correctness("Roy values identity and love.", "Roy says the story is about identity, dreams and love.") > 0.4
    assert answer_correctness(FALLBACK_ANSWER, FALLBACK_ANSWER) == 1.0
    assert answer_correctness("It won an Oscar.", FALLBACK_ANSWER) == 0.0


def test_hallucination_rate_counts_unsupported_inventions():
    results = [
        {"expect_fallback": True, "answer": FALLBACK_ANSWER},
        {"expect_fallback": True, "answer": "Roy says it won an Oscar."},
        {"expect_fallback": False, "answer": "Grounded answer."},
    ]
    assert hallucination_rate(results) == 0.5


def test_evaluate_case_aggregates_all_metrics():
    case = {"id": "tamasha", "expected_movie": "Tamasha", "expected_answer": "Roy values identity and love.", "expect_fallback": False}
    result = evaluate_case(case, CONTEXT, SOURCES, "Roy values identity and love.")
    assert result["id"] == "tamasha"
    assert result["retrieval_recall"] == 1.0
    assert result["answer_correctness"] == 1.0
