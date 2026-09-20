import re
from datetime import datetime, timezone

import streamlit as st

from auth.login import current_user, is_admin, is_authenticated, logout_user, render_login
from auth.signup import render_signup
from database.mongodb import movies_collection
from ui.design import inject_design_system, render_footer, render_nav
from ui.home import render_home
from ui.movie_details import render_movie_details
from ui.profile import render_edit_profile, render_profile
from ui.analytics import render_analytics
from rag.bootstrap import ensure_vector_store


st.set_page_config(
    page_title="CineAI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def initialize_vector_store():
    return ensure_vector_store()


initialize_vector_store()

inject_design_system()

st.markdown("""
<style>
div[data-testid="stTextArea"] textarea {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

for key, value in {"selected_movie": None, "logged_out": False, "auth_page": "login", "view": "home", "logout_requested": False}.items():
    st.session_state.setdefault(key, value)


def render_auth_screen():
    st.markdown('<div class="rr-auth-shell">', unsafe_allow_html=True)

    brand_col, form_col = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )

    with brand_col:
        st.markdown(
            '<div class="rr-auth-card rr-auth-brand">'
            '<div class="rr-brand">Cine<span>AI</span></div>'
            "<h1>Your next favourite is waiting.</h1>"
            "<p>Sign in to explore Our reviews and ask about the films that stayed with him.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    with form_col:
        left, right = st.columns(2)

        with left:
            if st.button(
                "Sign in",
                type="primary" if st.session_state.auth_page == "login" else "secondary",
                use_container_width=True,
            ):
                st.session_state.auth_page = "login"
                st.rerun()

        with right:
            if st.button(
                "Sign up",
                type="primary" if st.session_state.auth_page == "signup" else "secondary",
                use_container_width=True,
            ):
                st.session_state.auth_page = "signup"
                st.rerun()

        if st.session_state.auth_page == "login":
            render_login()
        else:
            render_signup()

    st.markdown("</div>", unsafe_allow_html=True)

def render_admin_dashboard(user):
    render_nav(user)
    try:
        total = movies_collection.count_documents({})
        confirmed = movies_collection.count_documents({"review_status": "CONFIRMED"})
        pending = movies_collection.count_documents({"review_status": {"$ne": "CONFIRMED"}})
        ingested = movies_collection.count_documents({"ingest_to_rag": True})
    except Exception as error:
        print(f"[Admin MongoDB Stats Error] {type(error).__name__}: {error}")
        st.error("Admin data is temporarily unavailable. Please try again shortly.")
        return
    st.markdown('<div class="rr-section-head"><div><div class="rr-kicker">Admin dashboard</div><h2>Review operations</h2><p>Add, confirm, and track Roy\'s notes.</p></div></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (label, value) in zip(cols, [("Total movies", total), ("Confirmed", confirmed), ("Needs approval", pending), ("RAG documents", ingested)]):
        with col: st.markdown(f'<div class="rr-stat-card"><label>{label}</label><strong>{value}</strong></div>', unsafe_allow_html=True)
    operations_tab, analytics_tab = st.tabs(["Review operations", "Analytics"])
    with operations_tab:
        st.markdown('<div class="rr-section-head"><div><h2>Add new review</h2></div></div>', unsafe_allow_html=True)
        with st.form("admin_add_review_form", clear_on_submit=True):
            first, second = st.columns(2)
            with first:
                title = st.text_input("Movie title", placeholder="Enter movie title")
                year = st.number_input("Release year", min_value=1900, max_value=2100, value=2026)
                genre = st.text_input("Genre", placeholder="Drama, thriller, romance...")
                rating = st.selectbox("Our rating", [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1])
            with second:
                zone = st.selectbox("Zone", ["Bollywood", "Tollywood", "Hollywood", "South Indian", "Bengali", "Other"])
                verdict = st.selectbox("Verdict", ["Must Watch", "Good Watch", "Don't Watch"])
                poster_url = st.text_input("Poster URL", placeholder="Optional")
                review = st.text_area("Our review", max_chars=4000, placeholder="Write your personal review...")
            submitted = st.form_submit_button("Save review", type="primary", use_container_width=True)
        if submitted:
            if not title.strip() or not review.strip():
                st.error("Movie title and Our review are required.")
            else:
                movie_id = f"{re.sub(r'[^a-z0-9]+', '-', title.lower().strip()).strip('-')}-{int(year)}"
                document = {"movie_id": movie_id, "title": title.strip(), "year": int(year), "zone": zone, "genre": genre.strip(), "poster_url": poster_url.strip(), "roy_rating": float(rating), "verdict": verdict, "review_text": review.strip(), "review_status": "CONFIRMED", "ingest_to_rag": False, "created_by": user.get("username", "admin"), "updated_at": datetime.now(timezone.utc)}
                try:
                    movies_collection.update_one({"movie_id": movie_id}, {"$set": document}, upsert=True)
                    st.toast(f"{title.strip()} saved as confirmed.")
                except Exception as error:
                    print(f"[Admin Save Review Error] {type(error).__name__}: {error}")
                    st.error("The review could not be saved. Please try again.")
        st.markdown('<div class="rr-section-head"><div><h2>Recent reviews</h2><p>Confirmed reviews are ready for RAG ingestion.</p></div></div>', unsafe_allow_html=True)
        try:
            recent = list(movies_collection.find({}, {"_id": 0, "title": 1, "verdict": 1, "review_status": 1, "ingest_to_rag": 1}).sort("updated_at", -1).limit(8))
        except Exception as error:
            print(f"[Admin Recent Reviews Error] {type(error).__name__}: {error}")
            recent = []
        if recent:
            st.dataframe(recent, use_container_width=True, hide_index=True)
    with analytics_tab:
        render_analytics(movies_collection)


def signed_out():
    st.markdown('<div class="rr-auth-shell rr-auth-shell-single"><div class="rr-auth-card"><div class="rr-brand">Cine<span>AI</span></div><h1>See you next time.</h1><p>Your place in Roy\'s collection will be right here.</p></div></div>', unsafe_allow_html=True)
    if st.button("Back to CineAI", type="primary"):
        logout_user(); st.session_state.logged_out = False; st.rerun()


if st.session_state.logout_requested:
    logout_user(); st.session_state.logout_requested = False; st.session_state.logged_out = True; st.session_state.selected_movie = None; st.rerun()

if st.session_state.logged_out:
    signed_out()
elif not is_authenticated():
    render_auth_screen()
elif is_admin():
    render_admin_dashboard(current_user() or {})
elif st.session_state.view == "profile":
    render_profile(current_user() or {})
elif st.session_state.view == "edit_profile":
    render_edit_profile(current_user() or {})
elif st.session_state.selected_movie:
    render_movie_details(st.session_state.selected_movie, current_user() or {})
else:
    render_home(movies_collection, current_user() or {})

render_footer()
