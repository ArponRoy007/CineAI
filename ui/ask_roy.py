import html

import streamlit as st

from ai.agent import answer_with_agent
from ai.personalization import log_interaction
from database.mongodb import get_movies_collection


QUESTIONS = [
    "Why did Roy give this rating?",
    "What does Roy like about this movie?",
    "What does Roy say about the performances?",
    "What makes this movie worth watching?",
]


def _resolve_movie_id(movie):
    """
    Return the canonical RoyReview movie_id.

    RoyReview tools use the internal movie_id such as:
        rr-015-tamasha

    The UI may sometimes only have a TMDB ID such as:
        339274

    Resolve the TMDB ID back to the RoyReview movie document when needed.
    """
    movie_id = str(movie.get("movie_id") or "").strip()

    if movie_id:
        return movie_id

    tmdb_id = movie.get("tmdb_id")

    if tmdb_id is not None:
        try:
            tmdb_id = int(tmdb_id)
        except (TypeError, ValueError):
            tmdb_id = None

    if tmdb_id is not None:
        try:
            stored_movie = get_movies_collection().find_one(
                {"tmdb_id": tmdb_id},
                {"_id": 0, "movie_id": 1},
            )

            if stored_movie and stored_movie.get("movie_id"):
                return str(stored_movie["movie_id"]).strip()

        except Exception as error:
            print(
                f"[Ask Roy Movie ID Resolution Error] "
                f"{type(error).__name__}: {error}"
            )

    return ""


def _key(movie):
    return str(
        movie.get("movie_id")
        or movie.get("tmdb_id")
        or movie.get("title")
        or "movie"
    )


def _ask(movie, question, user=None):
    question = (question or "").strip()

    if not question:
        st.toast("Write a question for Roy first.")
        return

    movie_id = _resolve_movie_id(movie)

    with st.spinner("Ask Roy is reading his notes..."):
        try:
            result = answer_with_agent(
                question,
                movie_id=movie_id or None,
            )

            st.session_state["ask_roy_answer"] = {
                "movie": _key(movie),
                "question": question,
                "answer": result.get(
                    "answer",
                    "I couldn't find that in Roy's movie notes.",
                ),
                "sources": result.get("sources", []),
            }

        except Exception as error:
            print(
                f"[Ask Roy] "
                f"{type(error).__name__}: {error}"
            )

            st.session_state["ask_roy_answer"] = {
                "movie": _key(movie),
                "question": question,
                "answer": "I couldn't find that in Roy's movie notes.",
                "sources": [],
            }

    if movie_id:
        log_interaction(
            user,
            movie_id,
            "asked_roy",
        )
    else:
        log_interaction(
            user,
            movie.get("tmdb_id"),
            "asked_roy",
        )

    st.rerun()


def render_ask_roy(movie, user=None):
    movie_key = _key(movie)

    current_answer = st.session_state.get(
        "ask_roy_answer"
    ) or {}

    if current_answer.get("movie") not in (
        None,
        movie_key,
    ):
        st.session_state["ask_roy_answer"] = None

    st.markdown(
        """
        <div class="rr-ask-roy">
            <div class="rr-kicker">ASK ROY</div>
            <h2>Ask anything about this movie</h2>
            <p>
                Roy answers from his own movie notes first.
                General movie facts can come from TMDB when needed.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question_key = f"ask_roy_input_{movie_key}"

    question = st.text_area(
        "Ask Roy",
        placeholder="What does Roy like about this movie?",
        key=question_key,
        label_visibility="collapsed",
    )

    cols = st.columns(2)

    with cols[0]:
        if st.button(
            "Ask Roy",
            type="primary",
            use_container_width=True,
            key=f"ask_roy_submit_{movie_key}",
        ):
            _ask(
                movie,
                question,
                user,
            )

    with cols[1]:
        if st.button(
            "Clear",
            use_container_width=True,
            key=f"ask_roy_clear_{movie_key}",
        ):
            st.session_state["ask_roy_answer"] = None
            st.rerun()

    for index, suggested_question in enumerate(QUESTIONS):
        if st.button(
            suggested_question,
            key=f"ask_roy_question_{movie_key}_{index}",
            use_container_width=True,
        ):
            _ask(
                movie,
                suggested_question,
                user,
            )

    answer = st.session_state.get(
        "ask_roy_answer"
    ) or {}

    if answer.get("movie") == movie_key:
        st.markdown(
            f"""
            <div class="rr-answer-card">
                <div class="rr-kicker">ASK ROY · JUST NOW</div>
                <div class="rr-question">
                    {html.escape(answer.get("question", ""))}
                </div>
                <div class="rr-answer">
                    {html.escape(answer.get("answer", ""))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        source_titles = []
        roy_sources = []
        tmdb_sources = []

        for source in answer.get("sources", []):
            if not isinstance(source, dict):
                continue

            metadata = source.get("metadata") or {}
            title = metadata.get("title")
            source_name = str(
                metadata.get("source") or ""
            ).upper()

            if source_name == "TMDB":
                if title and title not in tmdb_sources:
                    tmdb_sources.append(str(title))
            else:
                if title and title not in source_titles:
                    source_titles.append(str(title))
                    roy_sources.append(str(title))

        if roy_sources:
            st.markdown(
                f"""
                <div class="rr-source">
                    Based on Roy's notes:
                    {html.escape(", ".join(roy_sources))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if tmdb_sources:
            st.markdown(
                f"""
                <div class="rr-source">
                    General movie information from TMDB:
                    {html.escape(", ".join(tmdb_sources))}
                </div>
                """,
                unsafe_allow_html=True,
            )