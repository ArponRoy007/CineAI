"""Deterministic metrics for RoyReview's manually labeled RAG evaluation set."""

import re


FALLBACK_ANSWER = "I couldn't find that in Roy's movie notes."
STOPWORDS = {"a", "an", "and", "about", "as", "at", "by", "for", "from", "in", "is", "it", "of", "on", "or", "roy", "says", "that", "the", "this", "to", "with"}


def _tokens(text):
    return {word for word in re.findall(r"[a-z0-9]{2,}", str(text or "").lower()) if word not in STOPWORDS}


def _source_titles(sources):
    return {str(source.get("metadata", {}).get("title", "")).lower() for source in sources if isinstance(source, dict)}


def retrieval_precision(sources, expected_movie):
    """Share of retrieved documents that match the labeled target movie."""
    if not expected_movie or not sources:
        return 0.0
    expected = expected_movie.lower()
    return sum(title == expected for title in _source_titles(sources)) / len(sources)


def retrieval_recall(sources, expected_movie):
    """Whether the labeled target review appears in the retrieval set."""
    return float(bool(expected_movie and expected_movie.lower() in _source_titles(sources)))


def context_relevance(context, expected_movie):
    """Whether the assembled context contains the labeled movie title."""
    return float(bool(expected_movie and expected_movie.lower() in str(context or "").lower()))


def answer_faithfulness(answer, context):
    """Simple fact-overlap proxy: meaningful answer terms should occur in context."""
    if str(answer or "").strip() == FALLBACK_ANSWER:
        return 1.0
    answer_terms = _tokens(answer)
    if not answer_terms:
        return 0.0
    context_terms = _tokens(context)
    return len(answer_terms & context_terms) / len(answer_terms)


def answer_correctness(answer, expected_answer):
    """Keyword-overlap F1 for answerable labels; exact match for fallbacks."""
    if expected_answer == FALLBACK_ANSWER:
        return float(str(answer or "").strip() == FALLBACK_ANSWER)
    actual = _tokens(answer)
    expected = _tokens(expected_answer)
    if not actual or not expected:
        return 0.0
    overlap = len(actual & expected)
    return (2 * overlap) / (len(actual) + len(expected))


def hallucination_rate(results):
    """Fraction of unsupported cases that did not return the grounding fallback."""
    unsupported = [result for result in results if result.get("expect_fallback")]
    if not unsupported:
        return 0.0
    hallucinations = sum(result.get("answer", "").strip() != FALLBACK_ANSWER for result in unsupported)
    return hallucinations / len(unsupported)


def evaluate_case(case, context, sources, answer):
    """Score one labeled case using precomputed retrieval and answer outputs."""
    expected_movie = case.get("expected_movie")
    return {
        "id": case["id"],
        "expect_fallback": bool(case.get("expect_fallback")),
        "answer": answer,
        "retrieval_precision": retrieval_precision(sources, expected_movie),
        "retrieval_recall": retrieval_recall(sources, expected_movie),
        "context_relevance": context_relevance(context, expected_movie),
        "answer_faithfulness": answer_faithfulness(answer, context),
        "answer_correctness": answer_correctness(answer, case["expected_answer"]),
    }
