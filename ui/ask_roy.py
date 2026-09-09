import html

import streamlit as st

from rag.qa import answer_question


# ============================================================
# ROYREVIEW — ASK ROY
# ============================================================

QUESTION_CHIPS = [
    "Why did Roy give this rating?",
    "What does Roy like about this movie?",
    "What does Roy say about the performances?",
    "What makes this movie worth watching?",
]


# ============================================================
# HELPERS
# ============================================================

def _safe_value(movie, key, default=""):
    """Safely read a value from the movie dictionary."""
    if not isinstance(movie, dict):
        return default

    value = movie.get(key, default)

    if value is None:
        return default

    return value


def _escape(value):
    """Escape text before inserting it into HTML."""
    if value is None:
        return ""

    return html.escape(str(value))


def _movie_state_key(movie):
    """
    Create a stable session-state key for the current movie.

    movie_id is preferred because titles can theoretically repeat.
    """
    movie_id = movie.get("movie_id")

    if movie_id:
        return str(movie_id)

    tmdb_id = movie.get("tmdb_id")

    if tmdb_id:
        return f"tmdb_{tmdb_id}"

    title = movie.get("title")

    if title:
        return str(title).strip().lower()

    return "unknown_movie"


# ============================================================
# ASK ROY BACKEND
# ============================================================

def ask_roy(movie, question):
    """
    Send the user's question to the real RoyReview
    Hybrid Search + RAG pipeline.

    The movie title is explicitly passed to answer_question()
    so movie-detail questions remain grounded in that movie's
    confirmed RoyReview notes.
    """

    title = _safe_value(
        movie,
        "title",
        "this movie",
    )

    question = (question or "").strip()

    if not question:
        return {
            "movie_title": title,
            "question": "",
            "answer": "Please ask a movie question.",
            "sources": [],
            "error": None,
        }

    try:
        result = answer_question(
            question=question,
            top_k=5,
            movie_title=title,
        )

        return {
            "movie_title": title,
            "question": question,
            "answer": result.get(
                "answer",
                "I couldn't find that in Roy's movie notes.",
            ),
            "sources": result.get(
                "sources",
                [],
            ),
            "error": None,
        }

    except Exception as error:
        # Keep the complete error in the terminal for debugging.
        print(
            f"[Ask Roy Error] "
            f"{type(error).__name__}: {error}"
        )

        return {
            "movie_title": title,
            "question": question,
            "answer": (
                "Ask Roy encountered a technical error "
                "while processing this question."
            ),
            "sources": [],
            "error": (
                f"{type(error).__name__}: {error}"
            ),
        }


# ============================================================
# SESSION STATE
# ============================================================

def _initialize_state():
    """Initialize Ask Roy session-state values."""

    if "ask_roy_answer" not in st.session_state:
        st.session_state["ask_roy_answer"] = None

    if "ask_roy_movie_key" not in st.session_state:
        st.session_state["ask_roy_movie_key"] = None

    if "ask_roy_custom_question" not in st.session_state:
        st.session_state["ask_roy_custom_question"] = ""


def _clear_answer():
    """Clear the previous Ask Roy response."""

    st.session_state["ask_roy_answer"] = None
    st.session_state["ask_roy_movie_key"] = None


# ============================================================
# ANSWER HANDLER
# ============================================================

def _run_question(movie, question, movie_key):
    """
    Execute a question and store the result in session state.
    """

    question = (question or "").strip()

    if not question:
        return

    # Remove the previous answer while the new answer is generated.
    st.session_state["ask_roy_answer"] = None

    with st.spinner("Ask Roy is thinking..."):

        result = ask_roy(
            movie=movie,
            question=question,
        )

    st.session_state["ask_roy_answer"] = result
    st.session_state["ask_roy_movie_key"] = movie_key

    # Force a clean render with the newly generated answer.
    st.rerun()


# ============================================================
# RENDER ASK ROY
# ============================================================

def render_ask_roy(movie):
    """
    Render the complete Ask Roy section.

    Includes:
        - Ask Roy introduction
        - Quick question chips
        - Custom question input
        - Hybrid Search / RAG answer
        - Source information
    """

    if not isinstance(movie, dict):
        return

    _initialize_state()

    # --------------------------------------------------------
    # CURRENT MOVIE
    # --------------------------------------------------------

    title = _safe_value(
        movie,
        "title",
        "this movie",
    )

    movie_key = _movie_state_key(movie)

    # --------------------------------------------------------
    # CLEAR OLD ANSWER WHEN MOVIE CHANGES
    # --------------------------------------------------------

    previous_movie_key = st.session_state.get(
        "ask_roy_movie_key"
    )

    if (
        previous_movie_key is not None
        and previous_movie_key != movie_key
    ):
        _clear_answer()

        st.session_state[
            "ask_roy_custom_question"
        ] = ""

    # --------------------------------------------------------
    # ASK ROY INTRO PANEL
    # --------------------------------------------------------

    safe_title = _escape(title)

    st.html(
        f"""
        <div class="rr-ask-panel">

            <div class="rr-ask-kicker">
                Ask Roy
            </div>

            <div class="rr-ask-title">
                Have a question about {safe_title}?
            </div>

            <div class="rr-ask-description">
                Ask about Roy's opinion, rating,
                performances and why he recommends
                or doesn't recommend the film.
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # QUICK QUESTIONS
    # --------------------------------------------------------

    chip_cols = st.columns(
        2,
        gap="small",
    )

    for index, question in enumerate(QUESTION_CHIPS):

        with chip_cols[index % 2]:

            if st.button(
                question,
                key=(
                    f"ask_roy_chip_"
                    f"{movie_key}_"
                    f"{index}"
                ),
                use_container_width=True,
            ):

                _run_question(
                    movie=movie,
                    question=question,
                    movie_key=movie_key,
                )

    # --------------------------------------------------------
    # CUSTOM QUESTION HEADING
    # --------------------------------------------------------

    st.html(
        """
        <div class="rr-ask-custom-heading">
            Ask your own question
        </div>
        """
    )

    # --------------------------------------------------------
    # CUSTOM QUESTION INPUT
    # --------------------------------------------------------

    custom_question = st.text_input(
        "Ask Roy anything about this movie or Roy's movie notes",
        key="ask_roy_custom_question",
        placeholder=(
            "e.g. Why does Roy consider this movie worth watching?"
        ),
        label_visibility="collapsed",
    )

    # --------------------------------------------------------
    # ASK BUTTON
    # --------------------------------------------------------

    custom_cols = st.columns(
        [5, 1],
        gap="small",
    )

    with custom_cols[1]:

        ask_button = st.button(
            "Ask Roy",
            key=f"ask_roy_custom_button_{movie_key}",
            use_container_width=True,
        )

    if ask_button:

        if custom_question.strip():

            _run_question(
                movie=movie,
                question=custom_question,
                movie_key=movie_key,
            )

        else:

            st.warning(
                "Please enter a question first."
            )

    # --------------------------------------------------------
    # GET STORED ANSWER
    # --------------------------------------------------------

    answer_data = st.session_state.get(
        "ask_roy_answer"
    )

    if not answer_data:
        return

    # --------------------------------------------------------
    # MAKE SURE ANSWER BELONGS TO CURRENT MOVIE
    # --------------------------------------------------------

    stored_movie_key = st.session_state.get(
        "ask_roy_movie_key"
    )

    if stored_movie_key != movie_key:
        return

    if answer_data.get("movie_title") != title:
        return

    # --------------------------------------------------------
    # READ ANSWER DATA
    # --------------------------------------------------------

    question_text = answer_data.get(
        "question",
        "",
    )

    answer_text = answer_data.get(
        "answer",
        "I couldn't find that in Roy's movie notes.",
    )

    sources = answer_data.get(
        "sources",
        [],
    )

    error_text = answer_data.get(
        "error"
    )

    # --------------------------------------------------------
    # ESCAPE CONTENT
    # --------------------------------------------------------

    safe_question = _escape(
        question_text
    )

    safe_answer = (
        _escape(answer_text)
        .replace("\n", "<br>")
    )

    # --------------------------------------------------------
    # ANSWER CARD
    # --------------------------------------------------------

    st.html(
        f"""
        <div class="rr-ask-answer">

            <div class="rr-ask-answer-label">
                ASK ROY
            </div>

            <div class="rr-ask-question">
                {safe_question}
            </div>

            <div class="rr-ask-answer-text">
                {safe_answer}
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # DEVELOPMENT ERROR
    # --------------------------------------------------------

    # If there is a real backend exception, show the
    # technical detail only while developing locally.
    if error_text:

        st.error(
            f"Development error: {error_text}"
        )

    # --------------------------------------------------------
    # COLLECT SOURCES
    # --------------------------------------------------------

    source_titles = []

    if isinstance(sources, list):

        for source in sources:

            if not isinstance(source, dict):
                continue

            metadata = source.get(
                "metadata",
                {},
            )

            if not isinstance(metadata, dict):
                continue

            source_title = metadata.get(
                "title",
                "",
            )

            if (
                source_title
                and source_title not in source_titles
            ):
                source_titles.append(
                    str(source_title)
                )

    # --------------------------------------------------------
    # SOURCE DISPLAY
    # --------------------------------------------------------

    if source_titles:

        source_text = ", ".join(
            _escape(source_title)
            for source_title in source_titles
        )

        st.html(
            f"""
            <div class="rr-ask-source">
                Based on Roy's notes: {source_text}
            </div>
            """
        )