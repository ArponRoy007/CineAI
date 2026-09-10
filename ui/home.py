import html
import re

import streamlit as st

from movies.tmdb import enrich_movie
from ui.design import esc, inject_design_system, render_nav


PROJECTION = {"_id": 0, "movie_id": 1, "title": 1, "year": 1, "zone": 1,
              "genre": 1, "roy_rating": 1, "verdict": 1, "review_text": 1,
              "imdb_rating": 1, "tmdb_id": 1, "poster_url": 1}
VERDICTS = ["Must Watch", "Good Watch", "Don't Watch"]


def _stars(rating):
    try:
        return "★" * int(float(rating)) + "☆" * (5 - int(float(rating)))
    except (TypeError, ValueError):
        return "☆☆☆☆☆"


def _movies(collection, query=None):
    return list(collection.find(query or {}, PROJECTION).sort("roy_rating", -1))


def _search(collection, query):
    if not query.strip():
        return []
    return _movies(collection, {"title": {"$regex": re.escape(query.strip()), "$options": "i"}})


def _ensure_poster(collection, movie):
    if movie.get("poster_url"):
        return movie
    try:
        data = enrich_movie(movie.get("title", ""), movie.get("year"))
        poster = data.get("poster_url")
        if poster and movie.get("movie_id"):
            collection.update_one({"movie_id": movie["movie_id"]}, {"$set": {"poster_url": poster}})
            movie["poster_url"] = poster
    except Exception as error:
        print(f"[Poster enrichment] {type(error).__name__}: {error}")
    return movie


def _open_movie(movie):
    st.session_state["selected_movie"] = movie
    st.session_state["ask_roy_answer"] = None
    st.rerun()


def render_movie_card(collection, movie, key):
    movie = _ensure_poster(collection, movie)
    poster = movie.get("poster_url")
    title = esc(movie.get("title", "Untitled"))
    genre = esc(movie.get("genre", "Film"))
    verdict = esc(movie.get("verdict", "Roy's pick"))
    with st.container():
        if poster:
            poster_html = f'<img src="{esc(poster)}" alt="{title} poster">'
        else:
            poster_html = f'<div class="rr-poster-empty">{title}</div>'
        st.markdown(f'''<div class="rr-card"><div class="rr-poster">{poster_html}</div><div class="rr-card-copy">
          <span class="rr-pill">{verdict}</span><span class="rr-rating">{_stars(movie.get("roy_rating"))} {esc(movie.get("roy_rating", "-"))}/5</span>
          <div class="rr-card-title">{title}</div><div class="rr-card-meta">{esc(movie.get("year", ""))} · {esc(movie.get("zone", ""))}</div><span class="rr-tag">{genre}</span></div></div>''', unsafe_allow_html=True)
        if st.button("View review", key=f"open_{key}"):
            _open_movie(movie)


def _render_results(collection, movies, title, subtitle, empty_query=""):
    st.markdown(f'<div class="rr-section-head"><div><h2>{esc(title)}</h2><p>{esc(subtitle)}</p></div></div>', unsafe_allow_html=True)
    if not movies:
        copy = f'Nothing in Roy\'s notes matches “{esc(empty_query)}”.' if empty_query else "Try another corner of Roy's collection."
        st.markdown(f'<div class="rr-empty"><strong>No films here yet</strong>{copy}</div>', unsafe_allow_html=True)
        return
    grid = st.columns(4, gap="medium")
    for index, movie in enumerate(movies):
        with grid[index % 4]:
            render_movie_card(collection, movie, f"{movie.get('movie_id', index)}_{index}")


def render_home(collection, user=None):
    inject_design_system()
    render_nav(user)
    st.markdown('''<section class="rr-hero"><div class="rr-kicker">Roy's personal movie journal</div>
    <h1>Every film has a story.<br><span>Here's mine.</span></h1><p>Honest reviews, personal ratings, and the films that stayed long after the credits.</p></section>''', unsafe_allow_html=True)

    search_col, action_col = st.columns([7, 1])
    with search_col:
        query = st.text_input("Search Roy's collection", placeholder="Search a film", key="movie_search")
    with action_col:
        st.markdown("<br>", unsafe_allow_html=True)
        searched = st.button("Search", type="primary", use_container_width=True)
    if searched or query.strip():
        st.session_state["home_query"] = query
        st.session_state["home_filter"] = None

    st.markdown('<div class="rr-section-head"><div><h2>Explore the collection</h2><p>Find the mood you are after.</p></div></div>', unsafe_allow_html=True)
    with st.container(key="verdict_segment"):
        controls = st.columns(3)
        active = st.session_state.get("home_filter")
        for column, verdict in zip(controls, VERDICTS):
            with column:
                if st.button(verdict, key=f"filter_{verdict}", type="primary" if active == verdict else "secondary", use_container_width=True):
                    st.session_state["home_filter"] = verdict
                    st.session_state["home_query"] = ""
                    st.rerun()

    selected = st.session_state.get("home_filter")
    saved_query = st.session_state.get("home_query", "")
    if selected:
        _render_results(collection, _movies(collection, {"verdict": {"$regex": f"^{re.escape(selected)}$", "$options": "i"}}), selected, "Curated by Roy")
    elif saved_query:
        _render_results(collection, _search(collection, saved_query), "Search results", "Roy's collection", saved_query)
    else:
        _render_results(collection, _movies(collection)[:8], "Fresh from Roy", "A few films worth your time")
