from rag.prompts import SYSTEM_PROMPT, build_user_prompt
from rag.retriever import build_context
from rag.hybrid import get_exact_movies, format_exact_movies


def _is_exact_fact_question(question: str) -> bool:
    q = question.lower()

    exact_patterns = [
        "which movies",
        "what movies",
        "list movies",
        "show movies",
        "movies did roy rate",
        "movies rated",
        "movies with a rating",
        "don't watch movies",
        "dont watch movies",
        "must watch movies",
        "good watch movies",
    ]

    return any(pattern in q for pattern in exact_patterns)


def _detect_filters(question: str):
    q = question.lower()

    rating = None
    min_rating = None
    verdict = None

    # Exact ratings
    for value in [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1]:
        if (
            f"{value}/5" in q
            or f"{value} out of 5" in q
            or f"rated {value}" in q
            or f"rating {value}" in q
        ):
            rating = value
            break

    # Minimum rating
    if (
        "4 or higher" in q
        or "4+" in q
        or "above 4" in q
        or "at least 4" in q
    ):
        min_rating = 4

    if (
        "must watch" in q
        or "must-watch" in q
    ):
        verdict = "Must Watch"

    elif (
        "good watch" in q
        or "good-watch" in q
    ):
        verdict = "Good Watch"

    elif (
        "don't watch" in q
        or "dont watch" in q
        or "do not watch" in q
    ):
        verdict = "Don't Watch"

    return rating, min_rating, verdict


def _answer_exact_question(question: str):
    rating, min_rating, verdict = _detect_filters(question)

    movies = get_exact_movies(
        rating=rating,
        min_rating=min_rating,
        verdict=verdict,
    )

    if not movies:
        return {
            "answer": (
                "I couldn't find matching movies in Roy's "
                "confirmed movie notes."
            ),
            "sources": [],
        }

    movie_list = format_exact_movies(movies)

    answer = (
        f"Here are the matching movies from Roy's confirmed notes:\n\n"
        f"{movie_list}"
    )

    sources = [
        {
            "metadata": movie,
            "document": movie.get("review_text", ""),
            "distance": 0,
        }
        for movie in movies
    ]

    return {
        "answer": answer,
        "sources": sources,
    }


def answer_question(
    question: str,
    top_k: int = 5,
    movie_title: str | None = None,
) -> dict:

    question = (question or "").strip()

    if not question:
        return {
            "answer": "Please ask a movie question.",
            "sources": [],
        }

    # --------------------------------------------------
    # HYBRID ROUTING
    # --------------------------------------------------

    if _is_exact_fact_question(question):
        try:
            return _answer_exact_question(question)
        except Exception as error:
            print(f"[Ask Roy Exact Search Error] {type(error).__name__}: {error}")
            return _grounding_fallback()

    # --------------------------------------------------
    # NORMAL RAG
    # --------------------------------------------------

    try:
        context, sources = build_context(
            question=question,
            top_k=top_k,
            movie_title=movie_title,
        )
    except Exception as error:
        print(f"[Ask Roy Retrieval Error] {type(error).__name__}: {error}")
        return _grounding_fallback()

    if not context:
        return _grounding_fallback()

    from ai.llm import generate_answer

    prompt = build_user_prompt(
        question=question,
        context=context,
    )

    try:
        answer = generate_answer(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
        )
    except Exception as error:
        print(f"[Ask Roy Groq Error] {type(error).__name__}: {error}")
        return _grounding_fallback()

    return {
        "answer": answer,
        "sources": sources,
    }


def _grounding_fallback() -> dict:
    return {
        "answer": "I couldn't find that in Roy's movie notes.",
        "sources": [],
    }
