import html

import streamlit as st

from rag.qa import answer_question

QUESTIONS = ["Why did Roy give this rating?", "What does Roy like about this movie?", "What does Roy say about the performances?", "What makes this movie worth watching?"]


def _key(movie):
    return str(movie.get("movie_id") or movie.get("tmdb_id") or movie.get("title") or "movie")


def _ask(movie, question):
    question = (question or "").strip()
    if not question:
        st.toast("Write a question for Roy first.")
        return
    with st.spinner("Ask Roy is reading his notes..."):
        try:
            result = answer_question(question=question, top_k=5, movie_title=movie.get("title", ""))
            st.session_state["ask_roy_answer"] = {"movie": _key(movie), "question": question, "answer": result.get("answer", "I couldn't find that in Roy's movie notes."), "sources": result.get("sources", [])}
        except Exception as error:
            print(f"[Ask Roy] {type(error).__name__}: {error}")
            st.session_state["ask_roy_answer"] = {"movie": _key(movie), "question": question, "answer": "I couldn't find that in Roy's movie notes.", "sources": []}
    st.rerun()


def render_ask_roy(movie):
    movie_key = _key(movie)
    if (st.session_state.get("ask_roy_answer") or {}).get("movie") not in (None, movie_key):
        st.session_state["ask_roy_answer"] = None
    st.markdown(f'''<section class="rr-ask"><div class="rr-kicker">Ask Roy</div><h2>Curious about {html.escape(str(movie.get("title", "this film"))) }?</h2><p>Roy answers from his own movie notes, so the conversation stays grounded in the review.</p>''', unsafe_allow_html=True)
    choices = st.columns(2)
    for index, question in enumerate(QUESTIONS):
        with choices[index % 2]:
            if st.button(question, key=f"ask_chip_{movie_key}_{index}", use_container_width=True):
                _ask(movie, question)
    composer, send = st.columns([5, 1])
    with composer:
        custom = st.text_input("Ask your own question", placeholder="Ask Roy about this film", key=f"ask_input_{movie_key}")
    with send:
        st.markdown("<br>", unsafe_allow_html=True)
        send_clicked = st.button("Ask", key=f"ask_send_{movie_key}", type="primary", use_container_width=True)
    st.markdown("</section>", unsafe_allow_html=True)
    if send_clicked:
        _ask(movie, custom)

    answer = st.session_state.get("ask_roy_answer")
    if not answer or answer.get("movie") != movie_key:
        return
    text = html.escape(str(answer.get("answer", ""))).replace("\n", "<br>")
    question = html.escape(str(answer.get("question", "")))
    st.markdown(f'<div class="rr-answer"><div class="rr-kicker">Ask Roy · just now</div><div class="rr-answer-q">{question}</div><div>{text}</div></div>', unsafe_allow_html=True)
    source_titles = []
    for source in answer.get("sources", []):
        title = source.get("metadata", {}).get("title") if isinstance(source, dict) else None
        if title and title not in source_titles:
            source_titles.append(str(title))
    if source_titles:
        st.markdown(f'<div class="rr-source">Based on Roy\'s notes: {html.escape(", ".join(source_titles))}</div>', unsafe_allow_html=True)
