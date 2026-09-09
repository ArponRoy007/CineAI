import streamlit as st

from database.mongodb import movies_collection
from ui.home import render_home
from ui.movie_details import render_movie_details

from movies.tmdb import enrich_movie
from rag.ingest import ingest_movie_review

from auth.login import (
    current_user,
    is_authenticated,
    is_admin,
    logout_user,
    render_login,
)
from auth.signup import render_signup


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RoyReview",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700'
        '&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap'
    );

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    html,
    body,
    [class*="css"] {
        font-family: "DM Sans", sans-serif;
    }

    .stApp {
        background: #F4F4F4;
        color: #17181C;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .main .block-container {
        max-width: 1180px;
        padding-top: 24px;
        padding-bottom: 80px;
        padding-left: 32px;
        padding-right: 32px;
    }


    /* ============================================================
       ASK ROY — CUSTOM QUESTION INPUT
    ============================================================ */

    div[data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        color: #17181C !important;
        border: 1px solid #C2C9CC !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #7B8285 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTextInput"] input:focus {
        background-color: #FFFFFF !important;
        color: #17181C !important;
        border-color: #F89344 !important;
        box-shadow: 0 0 0 1px #F89344 !important;
    }


    /* --------------------------------------------------------
   BUTTONS — WHITE NORMAL / BLUE HOVER
-------------------------------------------------------- */

/* Normal buttons */
div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 12px !important;
    border: 1px solid #393A3A !important;
    background: #FFFFFF !important;
    color: #17181C !important;
    font-family: "DM Sans", sans-serif !important;
    font-weight: 600 !important;
    min-height: 44px !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}

/* Primary buttons — override Streamlit's dark primary style */
div.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"],
button[kind="primary"],
button[kind="primaryFormSubmit"] {
    background: #FFFFFF !important;
    color: #17181C !important;
    border: 1px solid #393A3A !important;
}

/* Hover */
div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
button[kind="primary"]:hover,
button[kind="primaryFormSubmit"]:hover {
    background: #B8D5E5 !important;
    color: #17181C !important;
    border-color: #393A3A !important;
    box-shadow: none !important;
}

/* Keep text/icon inside buttons dark */
div.stButton > button *,
div[data-testid="stFormSubmitButton"] > button * {
    color: #17181C !important;
}

/* Keep text/icon dark on hover */
div.stButton > button:hover *,
div[data-testid="stFormSubmitButton"] > button:hover * {
    color: #17181C !important;
}

    /* --------------------------------------------------------
       INPUT
    -------------------------------------------------------- */

    div[data-testid="stTextInput"] input {
        font-family: "DM Sans", sans-serif !important;
        color: #17181C !important;
    }

    div[data-baseweb="input"] {
        border-radius: 14px !important;
        background: #FFFFFF !important;
    }


    /* --------------------------------------------------------
       FORM
    -------------------------------------------------------- */

    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }


    /* --------------------------------------------------------
       SCROLLBAR
    -------------------------------------------------------- */

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #F4F4F4;
    }

    ::-webkit-scrollbar-thumb {
        background: #B8D5E5;
        border-radius: 10px;
    }


    /* --------------------------------------------------------
       LOGGED OUT SCREEN
    -------------------------------------------------------- */

    .rr-logout-card {
        max-width: 420px;
        margin: 120px auto;
        text-align: center;
        background: #FFFFFF;
        border: 1px solid #E2E4E5;
        border-radius: 26px;
        padding: 48px 32px;
        box-shadow: 0 18px 50px rgba(57, 58, 58, 0.08);
    }

    .rr-logout-icon {
        font-size: 34px;
        margin-bottom: 14px;
    }

    .rr-logout-title {
        font-family: "Plus Jakarta Sans", sans-serif;
        font-size: 22px;
        font-weight: 800;
        color: #393A3A;
        margin-bottom: 8px;
    }

    .rr-logout-text {
        color: #73777A;
        font-size: 14px;
    }


    /* --------------------------------------------------------
       AUTHENTICATION
    -------------------------------------------------------- */

    .rr-auth-card {
        max-width: 520px;
        margin: 80px auto 30px auto;
        background: #FFFFFF;
        border: 1px solid #E0E2E3;
        border-radius: 28px;
        padding: 42px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.06);
        text-align: center;
    }

    .rr-auth-logo {
        font-family: "Plus Jakarta Sans", sans-serif;
        font-size: 34px;
        font-weight: 800;
        color: #393A3A;
        letter-spacing: -1.5px;
    }

    .rr-auth-logo span {
        color: #F89344;
    }

    .rr-auth-subtitle {
        margin-top: 8px;
        color: #7B8285;
        font-size: 14px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-weight: 700;
    }

    .rr-auth-description {
        margin-top: 24px;
        color: #575959;
        font-size: 15px;
        line-height: 1.6;
    }


    /* --------------------------------------------------------
       ADMIN
    -------------------------------------------------------- */

    .rr-admin-header {
        background: #FFFFFF;
        border: 1px solid #E0E2E3;
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 25px;
    }

    .rr-admin-label {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #F89344;
    }

    .rr-admin-title {
        font-family: "Plus Jakarta Sans", sans-serif;
        font-size: 36px;
        font-weight: 800;
        color: #393A3A;
        margin-top: 8px;
    }

    .rr-admin-description {
        color: #7B8285;
        margin-top: 8px;
    }

    /* ============================================================
   ADMIN / AUTH CONTROLS
   WHITE FRONT + BLUE HOVER
============================================================ */

/* -------------------------
   TEXT INPUTS
------------------------- */

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important;
    color: #17181C !important;
    border: 1px solid #393A3A !important;
    border-radius: 12px !important;
    font-family: "DM Sans", sans-serif !important;
}

div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
    color: #7B8285 !important;
    opacity: 1 !important;
}


/* -------------------------
   NUMBER INPUT
------------------------- */

div[data-testid="stNumberInput"] {
    background: #FFFFFF !important;
    border-radius: 12px !important;
}

div[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    color: #17181C !important;
    border: 1px solid #393A3A !important;
}


/* -------------------------
   SELECTBOX
------------------------- */

div[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    color: #17181C !important;
    border: 1px solid #393A3A !important;
    border-radius: 12px !important;
}

div[data-testid="stSelectbox"] * {
    color: #17181C !important;
}


/* -------------------------
   TEXT AREA
------------------------- */

div[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    color: #17181C !important;
    border: 1px solid #393A3A !important;
}


/* -------------------------
   BUTTONS
------------------------- */

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 12px !important;
    border: 1px solid #393A3A !important;
    background: #FFFFFF !important;
    color: #17181C !important;
    font-family: "DM Sans", sans-serif !important;
    font-weight: 600 !important;
    min-height: 44px !important;
    box-shadow: none !important;
}


/* Primary buttons */
div.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"],
button[kind="primary"],
button[kind="primaryFormSubmit"] {
    background: #FFFFFF !important;
    color: #17181C !important;
    border: 1px solid #393A3A !important;
}


/* Button hover */
div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
button[kind="primary"]:hover,
button[kind="primaryFormSubmit"]:hover {
    background: #B8D5E5 !important;
    color: #17181C !important;
    border-color: #393A3A !important;
}


/* Button text */
div.stButton > button *,
div[data-testid="stFormSubmitButton"] > button * {
    color: #17181C !important;
}


/* Button text on hover */
div.stButton > button:hover *,
div[data-testid="stFormSubmitButton"] > button:hover * {
    color: #17181C !important;
}


/* -------------------------
   FORM LABELS
------------------------- */

div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    color: #575959 !important;
    font-weight: 600 !important;
}

    /* --------------------------------------------------------
       MOBILE
    -------------------------------------------------------- */

    @media (max-width: 700px) {

        .main .block-container {
            padding-left: 16px;
            padding-right: 16px;
        }

        .rr-auth-card {
            margin-top: 40px;
            padding: 28px 20px;
        }

        .rr-admin-title {
            font-size: 28px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_movie" not in st.session_state:
    st.session_state["selected_movie"] = None

if "logged_out" not in st.session_state:
    st.session_state["logged_out"] = False

if "show_explore" not in st.session_state:
    st.session_state["show_explore"] = False

if "ask_roy_answer" not in st.session_state:
    st.session_state["ask_roy_answer"] = None

if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "login"


# ============================================================
# AUTHENTICATION SCREEN
# ============================================================

def render_auth_screen():

    st.html(
        """
        <div class="rr-auth-card">

            <div style="
                font-size:42px;
                margin-bottom:14px;
            ">
                🎬
            </div>

            <div class="rr-auth-logo">
                Roy<span>Review</span>
            </div>

            <div class="rr-auth-subtitle">
                Roy's Personal Movie Journal
            </div>

            <div class="rr-auth-description">
                Sign in to explore Roy's movie reviews
                and ask Roy anything about his film notes.
            </div>

        </div>
        """
    )

    left, center, right = st.columns([1, 1.2, 1])

    with center:

        login_tab, signup_tab = st.columns(2)

        with login_tab:

            if st.button(
                "Sign In",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state["auth_page"] == "login"
                    else "secondary"
                ),
            ):

                st.session_state["auth_page"] = "login"
                st.rerun()

        with signup_tab:

            if st.button(
                "Sign Up",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state["auth_page"] == "signup"
                    else "secondary"
                ),
            ):

                st.session_state["auth_page"] = "signup"
                st.rerun()

        st.write("")

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        if st.session_state["auth_page"] == "login":

            render_login()

        # ----------------------------------------------------
        # SIGNUP
        # ----------------------------------------------------

        else:

            render_signup()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def render_admin_dashboard():

    user = current_user() or {}

    admin_name = user.get("name", "Admin")

    st.html(
        f"""
        <div class="rr-admin-header">

            <div class="rr-admin-label">
                ADMIN DASHBOARD
            </div>

            <div class="rr-admin-title">
                Welcome, {admin_name}
            </div>

            <div class="rr-admin-description">
                Manage Roy's movie reviews from here.
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_movies = movies_collection.count_documents({})

    confirmed_reviews = movies_collection.count_documents(
        {
            "review_status": "CONFIRMED"
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Movies",
            total_movies,
        )

    with col2:
        st.metric(
            "Confirmed Reviews",
            confirmed_reviews,
        )

    st.write("")

    # --------------------------------------------------------
    # ADD REVIEW
    # --------------------------------------------------------

    st.html(
        """
        <div style="
            font-family:'Plus Jakarta Sans',sans-serif;
            font-size:24px;
            font-weight:800;
            color:#393A3A;
            margin:20px 0 10px 0;
        ">
            Add New Review
        </div>
        """
    )

    with st.form("admin_add_review_form"):

        title = st.text_input(
            "Movie Title",
            placeholder="Enter movie title",
        )

        year = st.number_input(
            "Release Year",
            min_value=1900,
            max_value=2100,
            value=2026,
            step=1,
        )

        zone = st.selectbox(
            "Zone",
            [
                "Bollywood",
                "Tollywood",
                "Hollywood",
                "South Indian",
                "Bengali",
                "Other",
            ],
        )

        genre = st.text_input(
            "Genre",
            placeholder="Example: Psychological Romance / Thriller",
        )

        poster_url = st.text_input(
            "Poster URL",
            placeholder="Optional",
        )

        roy_rating = st.selectbox(
            "Roy's Rating",
            [
                5,
                4.5,
                4,
                3.5,
                3,
                2.5,
                2,
                1.5,
                1,
            ],
        )

        verdict = st.selectbox(
            "Verdict",
            [
                "Must Watch",
                "Good Watch",
                "Don't Watch",
            ],
        )

        review_text = st.text_area(
            "Roy's Review",
            placeholder="Write Roy's personal review...",
            max_chars=200,
        )

        submitted = st.form_submit_button(
            "Save Review",
            use_container_width=True,
            type="primary",
        )

    # --------------------------------------------------------
    # SAVE REVIEW
    # --------------------------------------------------------

    if submitted:

        if not title.strip():

            st.error(
                "Movie title is required."
            )

        elif not review_text.strip():

            st.error(
                "Review text is required."
            )

        elif len(review_text.strip()) > 200:

            st.error(
                "Roy's review must be 200 characters or less."
            )

        else:

            import re
            from datetime import datetime, timezone

            movie_id = re.sub(
                r"[^a-z0-9]+",
                "-",
                title.lower().strip(),
            ).strip("-")

            movie_id = f"{movie_id}-{int(year)}"

            movie_document = {
                "movie_id": movie_id,
                "title": title.strip(),
                "year": int(year),
                "zone": zone,
                "genre": genre.strip(),
                "poster_url": poster_url.strip(),
                "roy_rating": float(roy_rating),
                "verdict": verdict,
                "review_text": review_text.strip(),

                # ------------------------------------------------
                # IMPORTANT:
                # Only confirmed reviews should enter RAG.
                # New admin review is confirmed but initially
                # marked false until the RAG ingestion step runs.
                # ------------------------------------------------

                "review_status": "CONFIRMED",
                "ingest_to_rag": False,

                "created_by": user.get(
                    "username",
                    "admin",
                ),

                "updated_at": datetime.now(
                    timezone.utc
                ),
            }

            movies_collection.update_one(
                {
                    "movie_id": movie_id
                },
                {
                    "$set": movie_document
                },
                upsert=True,
            )

            st.success(
                f'"{title.strip()}" review saved successfully.'
            )

            st.info(
                "The review is saved as CONFIRMED in MongoDB. "
                "RAG/Chroma ingestion will be connected to this "
                "admin workflow next."
            )


# ============================================================
# ADMIN LOGOUT
# ============================================================

def render_admin_logout():

    left, middle, right = st.columns(
        [1, 1, 0.25]
    )

    with right:

        if st.button(
            "Sign out",
            use_container_width=True,
        ):

            logout_user()

            st.session_state["selected_movie"] = None
            st.session_state["show_explore"] = False
            st.session_state["ask_roy_answer"] = None
            st.session_state["logged_out"] = True
            st.session_state["auth_page"] = "login"

            st.rerun()


# ============================================================
# LOGGED OUT SCREEN
# ============================================================

def render_logged_out():

    st.html(
        """
        <div class="rr-logout-card">

            <div class="rr-logout-icon">
                🎬
            </div>

            <div class="rr-logout-title">
                You've signed out
            </div>

            <div class="rr-logout-text">
                Come back anytime to see Roy's latest reviews.
            </div>

        </div>
        """
    )

    _, middle, _ = st.columns(
        [1, 1, 1]
    )

    with middle:

        if st.button(
            "Back to RoyReview",
            use_container_width=True,
        ):

            # ------------------------------------------------
            # IMPORTANT:
            # Always make sure the session is logged out.
            # ------------------------------------------------

            logout_user()

            st.session_state["logged_out"] = False
            st.session_state["selected_movie"] = None
            st.session_state["show_explore"] = False
            st.session_state["ask_roy_answer"] = None
            st.session_state["auth_page"] = "login"

            st.rerun()


# ============================================================
# MAIN APPLICATION ROUTER
# ============================================================

# ------------------------------------------------------------
# 1. USER HAS JUST SIGNED OUT
# ------------------------------------------------------------

if st.session_state["logged_out"]:

    render_logged_out()


# ------------------------------------------------------------
# 2. USER IS NOT AUTHENTICATED
# ------------------------------------------------------------

elif not is_authenticated():

    render_auth_screen()


# ------------------------------------------------------------
# 3. ADMIN
# ------------------------------------------------------------

elif is_admin():

    render_admin_logout()
    render_admin_dashboard()


# ------------------------------------------------------------
# 4. NORMAL USER — MOVIE DETAILS
# ------------------------------------------------------------

elif st.session_state["selected_movie"]:

    render_movie_details(
        st.session_state["selected_movie"]
    )


# ------------------------------------------------------------
# 5. NORMAL USER — ROYREVIEW HOME
# ------------------------------------------------------------

else:

    render_home(
        movies_collection
    )