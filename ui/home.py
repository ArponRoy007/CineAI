import html
import re

import streamlit as st

from movies.tmdb import enrich_movie


# ============================================================
# ROYREVIEW — PREMIUM HOME / DASHBOARD
# ============================================================

PALETTE = {
    "background": "#F4F4F4",
    "primary": "#393A3A",
    "secondary": "#575959",
    "soft_blue": "#B8D5E5",
    "orange": "#F89344",
    "accent": "#FF642F",
    "text": "#17181C",
    "white": "#FFFFFF",
    "muted": "#73777A",
    "border": "#E2E4E5",
}

VERDICT_FILTERS = ["Must Watch", "Good Watch", "Don't Watch"]

PROJECTION = {
    "_id": 0,
    "movie_id": 1,
    "title": 1,
    "year": 1,
    "zone": 1,
    "genre": 1,
    "roy_rating": 1,
    "verdict": 1,
    "review_text": 1,
    "imdb_rating": 1,
    "tmdb_id": 1,
    "poster_url": 1,
}


# ============================================================
# HELPERS
# ============================================================

def escape(value):
    """Safely escape database values before putting them into HTML."""
    if value is None:
        return ""
    return html.escape(str(value))


def stars(rating):
    """Create a five-star visual rating."""
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        return "☆☆☆☆☆"

    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half

    return "★" * full + ("½" if half else "") + "☆" * empty


def get_movies(collection):
    """Load movies from MongoDB."""
    return list(collection.find({}, PROJECTION))


def search_movies(collection, query):
    """
    Search RoyReview's MongoDB collection by title.

    If a movie does not have a poster_url, automatically try
    TMDB enrichment and save the poster URL back to MongoDB.
    """

    if not query.strip():
        return []

    safe_query = re.escape(query.strip())

    movies = list(
        collection.find(
            {
                "title": {
                    "$regex": safe_query,
                    "$options": "i",
                }
            },
            PROJECTION,
        )
    )

    fixed_movies = []

    for movie in movies:

        poster_url = movie.get("poster_url")

        # ----------------------------------------------------
        # POSTER ALREADY EXISTS
        # ----------------------------------------------------

        if poster_url:
            fixed_movies.append(movie)
            continue

        # ----------------------------------------------------
        # POSTER MISSING → TRY TMDB
        # ----------------------------------------------------

        title = movie.get("title", "")
        year = movie.get("year")

        if title:

            try:

                tmdb_data = enrich_movie(
                    title=title,
                    year=year,
                )

                new_poster_url = tmdb_data.get(
                    "poster_url"
                )

                # ------------------------------------------------
                # SAVE TMDB DATA TO MONGODB
                # ------------------------------------------------

                if new_poster_url:

                    collection.update_one(
                        {
                            "movie_id": movie.get(
                                "movie_id"
                            )
                        },
                        {
                            "$set": {
                                "poster_url": new_poster_url,
                                "tmdb_id": tmdb_data.get(
                                    "tmdb_id"
                                ),
                                "tmdb_title": tmdb_data.get(
                                    "tmdb_title"
                                ),
                                "tmdb_overview": tmdb_data.get(
                                    "tmdb_overview"
                                ),
                                "tmdb_rating": tmdb_data.get(
                                    "tmdb_rating"
                                ),
                                "imdb_id": tmdb_data.get(
                                    "imdb_id"
                                ),
                            }
                        },
                    )

                    # Update current object immediately.
                    movie["poster_url"] = (
                        new_poster_url
                    )

                    movie["tmdb_id"] = (
                        tmdb_data.get("tmdb_id")
                    )

                    movie["tmdb_title"] = (
                        tmdb_data.get("tmdb_title")
                    )

                    movie["tmdb_overview"] = (
                        tmdb_data.get("tmdb_overview")
                    )

                    movie["tmdb_rating"] = (
                        tmdb_data.get("tmdb_rating")
                    )

                    movie["imdb_id"] = (
                        tmdb_data.get("imdb_id")
                    )

            except Exception as error:

                print(
                    f"[TMDB Poster Error] "
                    f"{title}: "
                    f"{type(error).__name__}: {error}"
                )

        fixed_movies.append(movie)

    return fixed_movies

def get_movies_by_verdict(collection, verdict_label):
    """Load movies matching a given verdict, e.g. 'Must Watch'."""
    safe_label = re.escape(verdict_label.strip())

    return list(
        collection.find(
            {"verdict": {"$regex": f"^{safe_label}$", "$options": "i"}},
            PROJECTION,
        )
    )


# ============================================================
# CSS
# ============================================================

def render_css():
    st.html(
        f"""
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700'
    '&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap'
);


/* =========================================================
   GLOBAL
========================================================= */

.stApp {{
    background: {PALETTE["background"]};
    color: {PALETTE["text"]};
    font-family: "DM Sans", sans-serif;
}}

.main .block-container {{
    max-width: 1180px;
    padding-top: 24px;
    padding-bottom: 80px;
    padding-left: 32px;
    padding-right: 32px;
}}

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

div[data-testid="stToolbar"] {{
    display: none;
}}

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}


/* =========================================================
   PROFESSIONAL HOME HEADER
========================================================= */

.st-key-royreview_home_header {{
    width: 100%;
    min-height: 76px;

    background: {PALETTE["white"]};

    border: 1px solid {PALETTE["border"]};
    border-radius: 22px;

    padding: 0 20px;

    box-shadow:
        0 8px 30px rgba(57, 58, 58, 0.05);

    margin-bottom: 28px;

    display: flex;
    align-items: center;

    box-sizing: border-box;
}}


/* ---------------------------------------------------------
   HEADER COLUMNS
--------------------------------------------------------- */

.st-key-royreview_home_header
[data-testid="column"] {{
    display: flex;
    align-items: center;
    justify-content: center;
}}


/* ---------------------------------------------------------
   LEFT SIDE
--------------------------------------------------------- */

.st-key-royreview_home_header
[data-testid="column"]:first-child {{
    justify-content: flex-start;
}}


/* ---------------------------------------------------------
   BRAND
--------------------------------------------------------- */

.rr-home-brand {{
    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: 23px;
    font-weight: 800;

    letter-spacing: -1px;
    line-height: 1;

    color: {PALETTE["primary"]};

    white-space: nowrap;

    padding-left: 2px;
}}

.rr-home-brand span {{
    color: {PALETTE["accent"]};
}}


/* ---------------------------------------------------------
   CENTER LABEL
--------------------------------------------------------- */

.rr-home-journal {{
    width: 100%;

    text-align: center;

    font-family: "DM Sans", sans-serif;

    font-size: 10px;
    font-weight: 800;

    letter-spacing: 1.8px;

    color: {PALETTE["muted"]};

    text-transform: uppercase;

    white-space: nowrap;
}}


/* ---------------------------------------------------------
   PROFILE TEXT
--------------------------------------------------------- */

.rr-home-profile-text {{
    width: 100%;

    text-align: right;

    font-family: "DM Sans", sans-serif;

    font-size: 12px;
    font-weight: 600;

    color: {PALETTE["secondary"]};

    white-space: nowrap;

    padding-right: 8px;
}}


/* ---------------------------------------------------------
   HEADER BUTTON BASE
--------------------------------------------------------- */

.st-key-royreview_home_header
div.stButton {{
    margin: 0 !important;
}}

.st-key-royreview_home_header
div.stButton > button {{
    min-width: 42px !important;
    width: 42px !important;

    min-height: 42px !important;
    height: 42px !important;

    padding: 0 !important;

    border-radius: 13px !important;

    border: 1px solid {PALETTE["border"]} !important;

    background: {PALETTE["background"]} !important;

    color: {PALETTE["primary"]} !important;

    font-family: "DM Sans", sans-serif !important;

    font-size: 17px !important;
    font-weight: 800 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    box-shadow: none !important;

    transition:
        background 0.2s ease,
        color 0.2s ease,
        border-color 0.2s ease,
        transform 0.2s ease !important;
}}


/* ---------------------------------------------------------
   MENU BUTTON
--------------------------------------------------------- */

.st-key-royreview_home_header
div.stButton > button:hover {{
    background: {PALETTE["primary"]} !important;

    color: {PALETTE["white"]} !important;

    border-color: {PALETTE["primary"]} !important;

    transform: translateY(-1px);
}}


/* ---------------------------------------------------------
   PROFILE BUTTON
--------------------------------------------------------- */

/*
   The profile button is the last button inside
   the header container.
*/

.st-key-royreview_home_header
div.stButton:last-child > button {{
    width: 42px !important;
    min-width: 42px !important;

    height: 42px !important;
    min-height: 42px !important;

    border-radius: 50% !important;

    background: {PALETTE["orange"]} !important;

    border: 1px solid {PALETTE["orange"]} !important;

    color: {PALETTE["white"]} !important;

    font-family: "Plus Jakarta Sans", sans-serif !important;

    font-size: 14px !important;

    font-weight: 800 !important;
}}

.st-key-royreview_home_header
div.stButton:last-child > button:hover {{
    background: {PALETTE["accent"]} !important;

    border-color: {PALETTE["accent"]} !important;

    color: {PALETTE["white"]} !important;

    transform: translateY(-1px);
}}


/* =========================================================
   HERO
========================================================= */

.rr-hero {{
    position: relative;

    overflow: hidden;

    margin-top: 0;

    min-height: 390px;

    background: {PALETTE["white"]};

    border: 1px solid {PALETTE["border"]};

    border-radius: 30px;

    box-shadow:
        0 18px 50px rgba(57, 58, 58, 0.07);

    display: flex;

    align-items: center;
    justify-content: center;

    text-align: center;
}}

.rr-hero::before {{
    content: "";

    position: absolute;

    width: 230px;
    height: 230px;

    border-radius: 50%;

    background: {PALETTE["soft_blue"]};

    opacity: 0.55;

    top: -120px;
    right: -70px;
}}

.rr-hero::after {{
    content: "";

    position: absolute;

    width: 190px;
    height: 190px;

    border-radius: 50%;

    background: {PALETTE["orange"]};

    opacity: 0.12;

    bottom: -105px;
    left: -65px;
}}

.rr-hero-content {{
    position: relative;

    z-index: 2;

    max-width: 760px;

    padding: 50px 24px;
}}


/* ---------------------------------------------------------
   HERO KICKER
--------------------------------------------------------- */

.rr-kicker {{
    display: inline-flex;

    align-items: center;

    padding: 8px 13px;

    border-radius: 999px;

    background: #FFF1E8;

    color: {PALETTE["accent"]};

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1.6px;

    margin-bottom: 22px;
}}


/* ---------------------------------------------------------
   HERO TITLE
--------------------------------------------------------- */

.rr-hero-title {{
    margin: 0;

    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: clamp(38px, 5vw, 66px);

    line-height: 1.05;

    letter-spacing: -3px;

    font-weight: 800;

    color: {PALETTE["primary"]};
}}

.rr-hero-title span {{
    color: {PALETTE["accent"]};
}}


/* ---------------------------------------------------------
   HERO DESCRIPTION
--------------------------------------------------------- */

.rr-hero-description {{
    max-width: 590px;

    margin: 22px auto 0 auto;

    color: {PALETTE["muted"]};

    font-size: 16px;

    line-height: 1.7;
}}


/* =========================================================
   SEARCH
========================================================= */

.rr-search-label {{
    margin-top: 34px;

    margin-bottom: 10px;

    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: 12px;

    font-weight: 800;

    letter-spacing: 1.5px;

    color: {PALETTE["secondary"]};

    text-transform: uppercase;
}}

div[data-testid="stTextInput"] {{
    margin-bottom: 0;
}}

div[data-testid="stTextInput"] input {{
    height: 58px;

    border-radius: 17px !important;

    border: 1px solid {PALETTE["border"]} !important;

    background: {PALETTE["white"]} !important;

    color: {PALETTE["text"]} !important;

    font-family: "DM Sans", sans-serif !important;

    font-size: 15px !important;

    padding-left: 18px !important;

    box-shadow:
        0 7px 25px rgba(57, 58, 58, 0.04) !important;
}}

div[data-testid="stTextInput"] input:focus {{
    border-color: {PALETTE["orange"]} !important;

    box-shadow:
        0 0 0 3px rgba(248, 147, 68, 0.12) !important;
}}

div[data-testid="stTextInput"] label {{
    display: none;
}}


/* ---------------------------------------------------------
   SEARCH BUTTON
--------------------------------------------------------- */

.rr-search-button button {{
    height: 58px !important;

    border-radius: 17px !important;

    border: none !important;

    background: {PALETTE["primary"]} !important;

    color: {PALETTE["white"]} !important;

    font-family: "DM Sans", sans-serif !important;

    font-weight: 700 !important;

    transition: all 0.2s ease !important;
}}

.rr-search-button button:hover {{
    background: {PALETTE["accent"]} !important;

    color: {PALETTE["white"]} !important;

    transform: translateY(-1px);
}}


/* =========================================================
   EXPLORE PANEL
========================================================= */

.rr-explore-wrap {{
    margin-top: 22px;

    background: {PALETTE["white"]};

    border: 1px solid {PALETTE["border"]};

    border-radius: 24px;

    padding: 22px 24px;

    box-shadow:
        0 10px 34px rgba(57, 58, 58, 0.05);
}}

.rr-explore-title {{
    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: 16px;

    font-weight: 800;

    color: {PALETTE["primary"]};

    margin-bottom: 14px;
}}

.rr-explore-pill button {{
    border-radius: 999px !important;

    border: 1px solid {PALETTE["border"]} !important;

    background: {PALETTE["background"]} !important;

    color: {PALETTE["secondary"]} !important;

    font-weight: 700 !important;

    font-size: 13px !important;
}}

.rr-explore-pill-active button {{
    border-radius: 999px !important;

    border: 1px solid {PALETTE["accent"]} !important;

    background: {PALETTE["accent"]} !important;

    color: {PALETTE["white"]} !important;

    font-weight: 700 !important;

    font-size: 13px !important;
}}


/* =========================================================
   SECTION HEADER
========================================================= */

.rr-section {{
    margin-top: 42px;
}}

.rr-section-header {{
    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    margin-bottom: 16px;
}}

.rr-section-title {{
    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: 25px;

    font-weight: 800;

    letter-spacing: -1px;

    color: {PALETTE["primary"]};

    margin: 0;
}}

.rr-section-subtitle {{
    color: {PALETTE["muted"]};

    font-size: 13px;
}}


/* =========================================================
   MOVIE CARD
========================================================= */

.rr-card {{
    position: relative;

    background: {PALETTE["white"]};

    border: 1px solid {PALETTE["border"]};

    border-radius: 26px 26px 0 0;

    padding: 20px;

    display: flex;

    gap: 25px;

    min-height: 320px;

    box-shadow:
        0 14px 42px rgba(57, 58, 58, 0.06);

    border-bottom: none;
}}


/* ---------------------------------------------------------
   POSTER
--------------------------------------------------------- */

.rr-poster {{
    width: 190px;

    min-width: 190px;

    height: 280px;

    border-radius: 19px;

    overflow: hidden;

    background: {PALETTE["soft_blue"]};
}}

.rr-poster img {{
    width: 100%;

    height: 100%;

    object-fit: cover;

    display: block;
}}

.rr-poster-empty {{
    width: 100%;

    height: 100%;

    display: flex;

    align-items: center;
    justify-content: center;

    color: {PALETTE["secondary"]};

    font-size: 12px;

    font-weight: 700;

    text-align: center;

    padding: 10px;
}}


/* ---------------------------------------------------------
   RESULT INFO
--------------------------------------------------------- */

.rr-result-info {{
    flex: 1;

    padding: 8px 4px 8px 0;
}}

.rr-topline {{
    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 15px;
}}

.rr-verdict {{
    display: inline-flex;

    align-items: center;

    background: #FFF1E8;

    color: {PALETTE["accent"]};

    border-radius: 999px;

    padding: 7px 11px;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 0.4px;
}}

.rr-rating {{
    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: 14px;

    font-weight: 800;

    color: {PALETTE["orange"]};
}}

.rr-result-title {{
    margin: 15px 0 4px 0;

    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: 31px;

    line-height: 1.1;

    letter-spacing: -1.4px;

    color: {PALETTE["primary"]};
}}

.rr-meta {{
    color: {PALETTE["muted"]};

    font-size: 13px;

    margin-bottom: 19px;
}}


/* ---------------------------------------------------------
   REVIEW
--------------------------------------------------------- */

.rr-review-label {{
    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: 1.4px;

    font-weight: 800;

    color: {PALETTE["secondary"]};

    margin-bottom: 8px;
}}

.rr-review {{
    font-size: 15px;

    line-height: 1.7;

    color: {PALETTE["secondary"]};

    max-width: 650px;
}}


/* ---------------------------------------------------------
   DIVIDER
--------------------------------------------------------- */

.rr-divider {{
    height: 1px;

    background: {PALETTE["border"]};

    margin: 20px 0;
}}


/* ---------------------------------------------------------
   TAGS
--------------------------------------------------------- */

.rr-tags {{
    display: flex;

    flex-wrap: wrap;

    gap: 8px;
}}

.rr-tag {{
    padding: 7px 10px;

    border-radius: 9px;

    background: {PALETTE["background"]};

    color: {PALETTE["secondary"]};

    font-size: 11px;

    font-weight: 700;
}}

.rr-tag-blue {{
    background: #EAF3F8;

    color: #496B7A;
}}


/* =========================================================
   OPEN DETAILS BUTTON
========================================================= */

.rr-open-btn {{
    margin-bottom: 26px;
}}

.rr-open-btn button {{
    width: 100% !important;

    border-radius: 0 0 22px 22px !important;

    border: 1px solid {PALETTE["border"]} !important;

    border-top: none !important;

    background: {PALETTE["primary"]} !important;

    color: {PALETTE["white"]} !important;

    font-family: "Plus Jakarta Sans", sans-serif !important;

    font-weight: 700 !important;

    font-size: 15px !important;

    min-height: 52px !important;

    box-shadow:
        0 14px 30px rgba(57, 58, 58, 0.08) !important;
}}

.rr-open-btn button:hover {{
    background: {PALETTE["accent"]} !important;

    border-color: {PALETTE["accent"]} !important;

    color: {PALETTE["white"]} !important;
}}


/* =========================================================
   EMPTY / SEARCH STATE
========================================================= */

.rr-empty {{
    background: {PALETTE["white"]};

    border: 1px dashed #D3D6D7;

    border-radius: 22px;

    padding: 45px 25px;

    text-align: center;
}}

.rr-empty-icon {{
    font-size: 32px;

    margin-bottom: 12px;
}}

.rr-empty-title {{
    font-family: "Plus Jakarta Sans", sans-serif;

    font-size: 19px;

    font-weight: 800;

    color: {PALETTE["primary"]};
}}

.rr-empty-text {{
    margin-top: 7px;

    color: {PALETTE["muted"]};

    font-size: 13px;
}}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 700px) {{

    .main .block-container {{
        padding-left: 16px;
        padding-right: 16px;
        padding-top: 16px;
    }}


    /* -----------------------------------------------------
       MOBILE HEADER
    ----------------------------------------------------- */

    .st-key-royreview_home_header {{
        min-height: 66px;

        height: 66px;

        border-radius: 18px;

        padding: 0 12px;

        margin-bottom: 20px;
    }}

    .rr-home-brand {{
        font-size: 20px;

        letter-spacing: -0.8px;
    }}

    .rr-home-journal,
    .rr-home-profile-text {{
        display: none;
    }}


    /* -----------------------------------------------------
       MOBILE HERO
    ----------------------------------------------------- */

    .rr-hero {{
        min-height: 330px;

        border-radius: 24px;
    }}

    .rr-hero-title {{
        font-size: 39px;

        letter-spacing: -2px;
    }}

    .rr-hero-description {{
        font-size: 14px;
    }}


    /* -----------------------------------------------------
       MOBILE MOVIE CARD
    ----------------------------------------------------- */

    .rr-card {{
        flex-direction: column;

        padding: 16px;
    }}

    .rr-poster {{
        width: 145px;

        min-width: 145px;

        height: 215px;
    }}

    .rr-result-title {{
        font-size: 25px;
    }}

    .rr-topline {{
        align-items: flex-start;
    }}

}}


/* =========================================================
   VERY SMALL MOBILE
========================================================= */

@media (max-width: 420px) {{

    .st-key-royreview_home_header {{
        padding: 0 9px;
    }}

    .rr-home-brand {{
        font-size: 18px;
    }}

    .st-key-royreview_home_header
    div.stButton > button {{
        width: 38px !important;

        min-width: 38px !important;

        height: 38px !important;

        min-height: 38px !important;
    }}

    .rr-hero-title {{
        font-size: 34px;

        letter-spacing: -1.6px;
    }}

}}


</style>
"""
    )

# ============================================================
# HEADER
# ============================================================

def render_header():

    with st.container(
        key="royreview_home_header"
    ):

        left, center, right = st.columns(
            [0.32, 0.46, 0.22],
            vertical_alignment="center",
        )

        # ----------------------------------------------------
        # LEFT — MENU + LOGO
        # ----------------------------------------------------

        with left:

            menu_col, logo_col = st.columns(
                [0.18, 0.82],
                vertical_alignment="center",
            )

            with menu_col:

                if st.button(
                    "☰",
                    key="rr_menu_toggle",
                    help="Explore Roy's collection",
                ):

                    st.session_state["show_explore"] = not st.session_state.get(
                        "show_explore",
                        False,
                    )

                    st.rerun()

            with logo_col:

                st.html(
                    """
                    <div class="rr-home-brand">
                        Roy<span>Review</span>
                    </div>
                    """
                )

        # ----------------------------------------------------
        # CENTER
        # ----------------------------------------------------

        with center:

            st.html(
                """
                <div class="rr-home-journal">
                    ROY'S PERSONAL MOVIE JOURNAL
                </div>
                """
            )

        # ----------------------------------------------------
        # RIGHT — PROFILE
        # ----------------------------------------------------

        with right:

            profile_col, text_col = st.columns(
                [0.30, 0.70],
                vertical_alignment="center",
            )

            with text_col:

                st.html(
                    """
                    <div class="rr-home-profile-text">
                        Roy's Journal
                    </div>
                    """
                )

            with profile_col:

                if st.button(
                    "R",
                    key="rr_profile_logout",
                    help="Sign out",
                ):

                    st.session_state["logged_out"] = True

                    st.rerun()
# ============================================================
# HERO
# ============================================================

def render_hero():
    st.html(
        """
<div class="rr-hero">

    <div class="rr-hero-content">

        <div class="rr-kicker">
            ROY'S PERSONAL MOVIE JOURNAL
        </div>

        <h1 class="rr-hero-title">
            Every film has a story.<br>
            <span>Here's mine.</span>
        </h1>

        <p class="rr-hero-description">
            Honest reviews, personal ratings and the movies
            that stayed long after the credits.
        </p>

    </div>

</div>
"""
    )


# ============================================================
# EXPLORE PANEL
# ============================================================

def render_explore(collection):
    """Renders the collapsible Explore panel (Must Watch / Good Watch / Don't Watch)."""

    if not st.session_state.get("show_explore", False):
        return None

    st.markdown('<div class="rr-explore-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="rr-explore-title">Explore Roy\'s collection</div>', unsafe_allow_html=True)

    active = st.session_state.get("explore_filter")
    cols = st.columns(len(VERDICT_FILTERS))

    for col, label in zip(cols, VERDICT_FILTERS):
        with col:
            css_class = "rr-explore-pill-active" if active == label else "rr-explore-pill"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"explore_{label}", use_container_width=True):
                st.session_state["explore_filter"] = None if active == label else label
                st.session_state["royreview_search"] = ""
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    active = st.session_state.get("explore_filter")
    if active:
        return get_movies_by_verdict(collection, active)

    return None


# ============================================================
# SEARCH
# ============================================================

def render_search(collection):
    st.html('<div class="rr-search-label">Find a film</div>')

    search_col, button_col = st.columns([8, 1], gap="small")

    with search_col:
        query = st.text_input(
            "movie-search",
            placeholder="Search your film...",
            label_visibility="collapsed",
        )

    with button_col:
        st.html('<div class="rr-search-button">')
        search_clicked = st.button("⌕", use_container_width=True)
        st.html("</div>")

    if query.strip() or search_clicked:
        if query.strip():
            results = search_movies(collection, query)
            st.session_state["royreview_search"] = query
            st.session_state["royreview_results"] = results
            st.session_state["explore_filter"] = None
        else:
            results = st.session_state.get("royreview_results", [])
    else:
        results = st.session_state.get("royreview_results", [])

    return results


# ============================================================
# MOVIE RESULT
# ============================================================

def render_movie_card(movie, key_prefix="card"):
    """
    Render a professional RoyReview movie card.

    Poster priority:
        1. poster_url from MongoDB
        2. TMDB enrichment if poster_url is missing
        3. Clean placeholder if TMDB also fails
    """

    # ========================================================
    # BASIC MOVIE DATA
    # ========================================================

    title_raw = movie.get(
        "title",
        "Untitled",
    )

    year_raw = movie.get(
        "year",
        "",
    )

    zone_raw = movie.get(
        "zone",
        "",
    )

    genre_raw = movie.get(
        "genre",
        "",
    )

    verdict_raw = movie.get(
        "verdict",
        "",
    )

    review_raw = movie.get(
        "review_text",
        "",
    )

    title = escape(title_raw)
    year = escape(year_raw)
    zone = escape(zone_raw)
    genre = escape(genre_raw)
    verdict = escape(verdict_raw)
    review = escape(review_raw)

    # ========================================================
    # RATING
    # ========================================================

    rating = movie.get(
        "roy_rating"
    )

    if rating is not None:

        try:

            rating_value = float(
                rating
            )

            rating_text = (
                f"{rating_value:g}/5"
            )

            star_text = stars(
                rating_value
            )

        except (
            TypeError,
            ValueError,
        ):

            rating_text = "—"
            star_text = "☆☆☆☆☆"

    else:

        rating_text = "Not rated"
        star_text = "☆☆☆☆☆"

    # ========================================================
    # POSTER
    # ========================================================

    poster_url = movie.get(
        "poster_url"
    )

    # --------------------------------------------------------
    # FALLBACK: ENRICH FROM TMDB
    # --------------------------------------------------------

    if not poster_url:

        try:

            tmdb_data = enrich_movie(
                title=title_raw,
                year=year_raw,
            )

            poster_url = tmdb_data.get(
                "poster_url"
            )

            # ------------------------------------------------
            # UPDATE MONGODB
            # ------------------------------------------------

            if poster_url:

                movie_id = movie.get(
                    "movie_id"
                )

                if movie_id:

                    movies_collection.update_one(
                        {
                            "movie_id": movie_id
                        },
                        {
                            "$set": {
                                "poster_url": poster_url,
                                "tmdb_id": tmdb_data.get(
                                    "tmdb_id"
                                ),
                                "tmdb_title": tmdb_data.get(
                                    "tmdb_title"
                                ),
                                "tmdb_overview": tmdb_data.get(
                                    "tmdb_overview"
                                ),
                                "tmdb_rating": tmdb_data.get(
                                    "tmdb_rating"
                                ),
                                "imdb_id": tmdb_data.get(
                                    "imdb_id"
                                ),
                            }
                        },
                    )

        except Exception as error:

            print(
                f"[TMDB Card Poster Error] "
                f"{title_raw}: "
                f"{type(error).__name__}: {error}"
            )

    # ========================================================
    # BUILD POSTER HTML
    # ========================================================

    if poster_url:

        safe_poster = escape(
            poster_url
        )

        poster_html = f"""
        <div class="rr-poster">
            <img
                src="{safe_poster}"
                alt="{title} poster"
                loading="lazy"
            >
        </div>
        """

    else:

        poster_html = f"""
        <div class="rr-poster">
            <div class="rr-poster-empty">
                {title if title else "POSTER UNAVAILABLE"}
            </div>
        </div>
        """

    # ========================================================
    # MOVIE CARD
    # ========================================================

    st.html(
        f"""
        <div class="rr-card">

            {poster_html}

            <div class="rr-result-info">

                <div class="rr-topline">

                    <div class="rr-verdict">
                        {verdict}
                    </div>

                    <div class="rr-rating">
                        {star_text}
                        &nbsp;
                        {rating_text}
                    </div>

                </div>

                <div class="rr-result-title">
                    {title}
                </div>

                <div class="rr-meta">
                    {year}
                    &nbsp;·&nbsp;
                    {zone}
                </div>

                <div class="rr-review-label">
                    Roy's Review
                </div>

                <div class="rr-review">
                    {review}
                </div>

                <div class="rr-divider"></div>

                <div class="rr-tags">

                    <div class="rr-tag rr-tag-blue">
                        {genre}
                    </div>

                    <div class="rr-tag">
                        Roy's Rating
                    </div>

                </div>

            </div>

        </div>
        """
    )

    # ========================================================
    # OPEN DETAILS BUTTON
    # ========================================================

    st.markdown(
        '<div class="rr-open-btn">',
        unsafe_allow_html=True,
    )

    movie_key = (
        movie.get("movie_id")
        or movie.get("tmdb_id")
        or movie.get(
            "title",
            "movie",
        )
    )

    if st.button(
        movie.get(
            "title",
            "View details",
        ),
        key=f"{key_prefix}_{movie_key}",
        use_container_width=True,
    ):

        # ----------------------------------------------------
        # IMPORTANT:
        # Store the UPDATED movie object.
        # This ensures movie details also receive poster_url.
        # ----------------------------------------------------

        st.session_state[
            "selected_movie"
        ] = movie

        st.session_state[
            "ask_roy_answer"
        ] = None

        st.session_state[
            "ask_roy_movie_key"
        ] = None

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# RESULTS
# ============================================================

def render_results(results, section_title="Search Result", subtitle="Roy's collection", empty_query=""):
    st.html(
        f"""
<div class="rr-section">
    <div class="rr-section-header">
        <div>
            <div class="rr-section-title">{escape(section_title)}</div>
            <div class="rr-section-subtitle">{escape(subtitle)}</div>
        </div>
    </div>
</div>
"""
    )

    if not results:
        st.html(
            f"""
<div class="rr-empty">
    <div class="rr-empty-icon">🎬</div>
    <div class="rr-empty-title">No film found</div>
    <div class="rr-empty-text">
        Nothing in Roy's collection matches "{escape(empty_query)}".
    </div>
</div>
"""
        )
        return

    st.html(
        f"""
<div style="color:#73777A;font-size:13px;margin-bottom:14px;">
    {len(results)} movie{"s" if len(results) != 1 else ""} found in Roy's collection.
</div>
"""
    )

    for movie in results:
        render_movie_card(movie, key_prefix="result")
        st.write("")


# ============================================================
# MAIN RENDER FUNCTION
# ============================================================

def render_home(movies_collection):
    """Render the complete RoyReview home dashboard."""

    render_css()
    render_header()
    render_hero()

    explore_results = render_explore(movies_collection)

    results = render_search(movies_collection)

    if explore_results is not None:
        render_results(
            explore_results,
            section_title=st.session_state.get("explore_filter", "Explore"),
            subtitle="Curated by Roy",
        )
    elif st.session_state.get("royreview_search"):
        render_results(
            results,
            section_title="Search Result",
            subtitle="Roy's collection",
            empty_query=st.session_state.get("royreview_search", ""),
        )