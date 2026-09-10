import html

import streamlit as st

from ui.ask_roy import render_ask_roy
from ui.design import esc, inject_design_system, render_nav


def _stars(rating):
    try:
        whole = int(float(rating))
        return "★" * whole + "☆" * (5 - whole)
    except (TypeError, ValueError):
        return "☆☆☆☆☆"


def render_movie_details(movie, user=None):
    inject_design_system()
    render_nav(user)
    if st.button("Back to collection", key="movie_details_back"):
        st.session_state["selected_movie"] = None
        st.session_state["ask_roy_answer"] = None
        st.rerun()

    title = movie.get("title", "Unknown Film")
    rating = movie.get("roy_rating")
    imdb = movie.get("imdb_rating")
    poster_col, content_col = st.columns([.38, .62], gap="large")
    with poster_col:
        if movie.get("poster_url"):
            st.image(movie["poster_url"], use_container_width=True)
        else:
            st.markdown(f'<div class="rr-poster" style="border-radius:14px"><div class="rr-poster-empty">{esc(title)}</div></div>', unsafe_allow_html=True)
    with content_col:
        st.markdown(f'''<div class="rr-verdict">{esc(movie.get("verdict", "Roy's pick"))}</div>
        <h1 class="rr-movie-title">{esc(title)}</h1>
        <div class="rr-card-meta">{esc(movie.get("year", ""))}</div>
        <div class="rr-rating-block"><div class="rr-kicker" style="color:#FFFFFF">Roy's rating</div><div class="rr-rating-stars">{_stars(rating)} <span style="color:#FFFFFF;font-size:18px;letter-spacing:0">{esc(rating)}/5</span></div></div>
        <div class="rr-stats"><div class="rr-stat"><label>Zone</label><b>{esc(movie.get("zone", "Unknown"))}</b></div><div class="rr-stat"><label>Genre</label><b>{esc(movie.get("genre", "Unknown"))}</b></div><div class="rr-stat"><label>IMDb</label><b>{esc(imdb) + '/10' if imdb else 'Not available'}</b></div><div class="rr-stat"><label>Year</label><b>{esc(movie.get("year", ""))}</b></div></div>
        <div class="rr-kicker">Roy's review</div><div class="rr-quote">{esc(movie.get("review_text", "Roy hasn't written a review for this film yet."))}</div>''', unsafe_allow_html=True)
    render_ask_roy(movie)
