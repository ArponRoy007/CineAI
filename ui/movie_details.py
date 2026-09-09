import html

import streamlit as st

from ui.ask_roy import render_ask_roy


# ============================================================
# ROYREVIEW — MOVIE DETAILS
# ============================================================

BG = "#F4F4F4"
CHARCOAL = "#393A3A"
CHARCOAL_2 = "#575959"
SOFT_BLUE = "#B8D5E5"
ORANGE = "#F89344"
ACCENT_ORANGE = "#FF642F"
TEXT = "#17181C"
WHITE = "#FFFFFF"
BORDER = "#E2E3E5"


# ============================================================
# PAGE CSS
# ============================================================

def inject_movie_details_css():

    st.html(
        f"""
        <style>

        /* =====================================================
           PAGE
        ===================================================== */

        .stApp {{
            background: {BG};
            color: {TEXT};
        }}

        .block-container {{
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }}

        #MainMenu {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        header {{
            background: transparent !important;
        }}


        /* =====================================================
           DETAILS HEADER
        ===================================================== */

        .rr-details-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0 22px 0;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 30px;
        }}

        .rr-details-logo {{
            font-family: "Plus Jakarta Sans",
                         Inter,
                         -apple-system,
                         BlinkMacSystemFont,
                         "Segoe UI",
                         sans-serif;

            font-size: 25px;
            font-weight: 800;
            letter-spacing: -1.2px;
            color: {CHARCOAL};
        }}

        .rr-details-logo span {{
            color: {ACCENT_ORANGE};
        }}

        .rr-details-tag {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1.4px;
            text-transform: uppercase;
            color: {CHARCOAL_2};
        }}


        /* =====================================================
           BACK LABEL
        ===================================================== */

        .rr-back-label {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: {CHARCOAL_2};
            margin-bottom: 12px;
        }}


        /* =====================================================
           MOVIE CARD
        ===================================================== */

        .rr-movie-card {{
            background: {WHITE};
            border: 1px solid {BORDER};
            border-radius: 28px;
            padding: 34px;

            box-shadow:
                0 20px 50px rgba(57, 58, 58, 0.08),
                0 4px 14px rgba(57, 58, 58, 0.04);

            margin-bottom: 28px;
        }}


        /* =====================================================
           POSTER
        ===================================================== */

        .rr-poster-frame {{
            background: {SOFT_BLUE};
            border-radius: 20px;
            padding: 8px;
            overflow: hidden;
        }}

        .rr-poster-caption {{
            text-align: center;

            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;

            color: {CHARCOAL_2};

            margin-top: 12px;
        }}


        /* =====================================================
           VERDICT
        ===================================================== */

        .rr-verdict {{
            display: inline-flex;
            align-items: center;
            gap: 7px;

            background: #FFF1E8;
            color: {ACCENT_ORANGE};

            border: 1px solid #FFD8C2;

            border-radius: 999px;

            padding: 8px 14px;

            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;

            margin-bottom: 16px;
        }}

        .rr-verdict-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: {ACCENT_ORANGE};
        }}


        /* =====================================================
           MOVIE TITLE
        ===================================================== */

        .rr-movie-title {{
            font-family: "Plus Jakarta Sans",
                         Inter,
                         sans-serif;

            font-size: clamp(32px, 4vw, 52px);
            line-height: 1.02;

            letter-spacing: -2.5px;
            font-weight: 800;

            color: {TEXT};

            margin: 0 0 8px 0;
        }}

        .rr-movie-year {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 15px;
            font-weight: 600;

            color: {CHARCOAL_2};

            margin-bottom: 22px;
        }}


        /* =====================================================
           RATING
        ===================================================== */

        .rr-rating-box {{
            background: {CHARCOAL};

            border-radius: 18px;

            padding: 17px 20px;

            margin-bottom: 24px;
        }}

        .rr-rating-label {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            color: #C9CCCD;

            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.4px;

            text-transform: uppercase;

            margin-bottom: 5px;
        }}

        .rr-rating-value {{
            font-family: "Plus Jakarta Sans",
                         Inter,
                         sans-serif;

            color: {WHITE};

            font-size: 27px;
            font-weight: 800;
            letter-spacing: -0.8px;
        }}

        .rr-rating-value span {{
            color: {ORANGE};
        }}


        /* =====================================================
           META GRID
        ===================================================== */

        .rr-meta-grid {{
            display: grid;

            grid-template-columns:
                repeat(2, minmax(0, 1fr));

            gap: 10px;

            margin-bottom: 25px;
        }}

        .rr-meta-item {{
            background: {BG};

            border: 1px solid {BORDER};

            border-radius: 14px;

            padding: 13px 15px;
        }}

        .rr-meta-label {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 9px;
            font-weight: 800;
            letter-spacing: 1.2px;

            text-transform: uppercase;

            color: {CHARCOAL_2};

            margin-bottom: 4px;
        }}

        .rr-meta-value {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 14px;
            font-weight: 700;

            color: {TEXT};
        }}


        /* =====================================================
           REVIEW
        ===================================================== */

        .rr-review-heading {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.3px;

            text-transform: uppercase;

            color: {CHARCOAL_2};

            margin-bottom: 9px;
        }}

        .rr-review {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 17px;
            line-height: 1.65;
            font-weight: 500;

            color: {TEXT};

            margin-bottom: 24px;
        }}

        .rr-review-mark {{
            color: {ORANGE};

            font-size: 24px;
            font-weight: 800;
        }}


        /* =====================================================
           ASK ROY PANEL
        ===================================================== */

        .rr-ask-panel {{
            background: {SOFT_BLUE};

            border-radius: 22px;

            padding: 23px;

            margin-top: 10px;
        }}

        .rr-ask-kicker {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.3px;

            text-transform: uppercase;

            color: {CHARCOAL_2};

            margin-bottom: 7px;
        }}

        .rr-ask-title {{
            font-family: "Plus Jakarta Sans",
                         Inter,
                         sans-serif;

            font-size: 21px;
            line-height: 1.2;

            font-weight: 800;

            color: {TEXT};

            margin-bottom: 6px;
        }}

        .rr-ask-description {{
            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 13px;
            line-height: 1.55;

            color: {CHARCOAL_2};

            margin-bottom: 14px;
        }}


        /* =====================================================
           ASK ROY ANSWER
        ===================================================== */

        .rr-ask-answer {{
            background: {WHITE};

            border-radius: 16px;

            padding: 16px 18px;

            margin-top: 14px;

            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 14px;
            line-height: 1.65;

            color: {TEXT};

            box-shadow:
                0 6px 20px rgba(57, 58, 58, 0.04);
        }}

        .rr-ask-answer-label {{
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.2px;

            text-transform: uppercase;

            color: {ACCENT_ORANGE};

            margin-bottom: 8px;
        }}

        .rr-ask-question {{
            font-size: 12px;

            color: {CHARCOAL_2};

            font-weight: 600;

            margin-bottom: 10px;
        }}

        .rr-ask-answer-text {{
            font-size: 14px;
            line-height: 1.7;

            color: {TEXT};
        }}

        .rr-ask-source {{
            margin-top: 10px;
            font-family: "DM Sans", Inter, sans-serif;
            font-size: 10px;
            line-height: 1.5;
            color: {CHARCOAL_2};
            font-weight: 600;
        }}

        .rr-chip-row {{
            margin-top: 12px;
        }}


        /* =====================================================
           BUTTONS
        ===================================================== */

        div.stButton > button {{
            border-radius: 12px !important;

            border: 1px solid {CHARCOAL} !important;

            background: {WHITE} !important;

            color: {CHARCOAL} !important;

            font-family: "DM Sans",
                         Inter,
                         sans-serif !important;

            font-weight: 700 !important;

            min-height: 44px !important;

            transition:
                background 0.2s ease,
                color 0.2s ease,
                border-color 0.2s ease !important;
        }}

        div.stButton > button:hover {{
            background: {CHARCOAL} !important;

            color: {WHITE} !important;

            border-color: {CHARCOAL} !important;
        }}


        /* =====================================================
           ASK ROY QUESTION CHIPS
        ===================================================== */

        .rr-chip-row div.stButton > button {{
            border-radius: 999px !important;

            font-size: 12px !important;

            min-height: 40px !important;

            padding:
                0 14px !important;

            background: {WHITE} !important;

            border:
                1px solid rgba(57, 58, 58, 0.55) !important;

            color: {CHARCOAL} !important;

            font-weight: 700 !important;
        }}

        .rr-chip-row div.stButton > button:hover {{
            background: {CHARCOAL} !important;

            color: {WHITE} !important;

            border-color: {CHARCOAL} !important;
        }}


        /* =====================================================
           SPINNER
        ===================================================== */

        .rr-ask-status {{
            font-size: 12px;
            font-weight: 600;

            color: {CHARCOAL_2};

            margin-top: 10px;
        }}


        /* =====================================================
           FOOTER
        ===================================================== */

        .rr-details-footer {{
            text-align: center;

            padding: 30px 0 10px 0;

            font-family: "DM Sans",
                         Inter,
                         sans-serif;

            font-size: 11px;

            color: #8B8D8E;
        }}


        /* =====================================================
           MOBILE
        ===================================================== */

        @media (max-width: 768px) {{

            .block-container {{
                padding:
                    1rem 1rem 3rem 1rem;
            }}

            .rr-details-top {{
                margin-bottom: 20px;
            }}

            .rr-details-logo {{
                font-size: 22px;
            }}

            .rr-details-tag {{
                display: none;
            }}

            .rr-movie-card {{
                padding: 18px;
                border-radius: 22px;
            }}

            .rr-movie-title {{
                font-size: 34px;
                letter-spacing: -1.5px;
            }}

            .rr-meta-grid {{
                grid-template-columns: 1fr;
            }}

            .rr-review {{
                font-size: 15px;
            }}

            .rr-ask-panel {{
                padding: 18px;
            }}

        }}

        </style>
        """,
    )


# ============================================================
# HELPERS
# ============================================================

def _safe_value(movie, key, default=""):

    value = movie.get(
        key,
        default,
    )

    if value is None:
        return default

    return value


def _escape(value):

    if value is None:
        return ""

    return html.escape(
        str(value)
    )


def _format_rating(rating):

    if rating is None or rating == "":
        return "—"

    try:

        number = float(rating)

        if number.is_integer():
            return f"{int(number)}/5"

        return f"{number:g}/5"

    except (TypeError, ValueError):

        return str(rating)


def _stars(rating):

    if rating is None or rating == "":
        return "☆☆☆☆☆"

    try:

        rating = float(rating)

        full_stars = int(rating)

        half_star = (
            rating - full_stars >= 0.5
            and full_stars < 5
        )

        result = "★" * full_stars

        if half_star:
            result += "½"

        remaining = (
            5
            - full_stars
            - (1 if half_star else 0)
        )

        if remaining > 0:
            result += "☆" * remaining

        return result

    except (TypeError, ValueError):

        return "☆☆☆☆☆"


# ============================================================
# MOVIE DETAILS RENDERER
# ============================================================

def render_movie_details(movie):
    """
    Render the complete RoyReview movie details screen.

    Parameters
    ----------
    movie : dict
        MongoDB movie document.
    """

    # --------------------------------------------------------
    # PAGE CSS
    # --------------------------------------------------------

    inject_movie_details_css()


    # --------------------------------------------------------
    # MOVIE DATA
    # --------------------------------------------------------

    title = _safe_value(
        movie,
        "title",
        "Unknown Film",
    )

    year = _safe_value(
        movie,
        "year",
        "",
    )

    zone = _safe_value(
        movie,
        "zone",
        "Unknown",
    )

    genre = _safe_value(
        movie,
        "genre",
        "Unknown",
    )

    rating = _safe_value(
        movie,
        "roy_rating",
        "",
    )

    verdict = _safe_value(
        movie,
        "verdict",
        "Not Rated",
    )

    review = _safe_value(
        movie,
        "review_text",
        "Roy hasn't written a review for this film yet.",
    )

    imdb_rating = _safe_value(
        movie,
        "imdb_rating",
        "",
    )

    poster_url = _safe_value(
        movie,
        "poster_url",
        "",
    )


    # --------------------------------------------------------
    # ESCAPED DISPLAY VALUES
    # --------------------------------------------------------

    safe_title = _escape(title)
    safe_year = _escape(year)
    safe_zone = _escape(zone)
    safe_genre = _escape(genre)
    safe_verdict = _escape(verdict)
    safe_review = _escape(review)


    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="rr-details-top">

            <div class="rr-details-logo">
                Roy<span>Review</span>
            </div>

            <div class="rr-details-tag">
                Roy's personal movie journal
            </div>

        </div>
        """,
    )


    # ========================================================
    # BACK BUTTON
    # ========================================================

    if st.button(
        "←  Back to collection",
        key="movie_details_back",
    ):

        # Clear selected movie

        st.session_state[
            "selected_movie"
        ] = None

        # Clear Ask Roy state

        st.session_state[
            "ask_roy_answer"
        ] = None

        st.session_state[
            "show_ask_roy"
        ] = False

        st.rerun()


    st.html(
        '<div class="rr-back-label">Film details</div>',
    )


    # ========================================================
    # MAIN MOVIE CARD
    # ========================================================

    st.html(
        '<div class="rr-movie-card">',
    )


    poster_col, info_col = st.columns(
        [0.38, 0.62],
        gap="large",
    )


    # ========================================================
    # POSTER
    # ========================================================

    with poster_col:

        if poster_url:

            st.image(
                poster_url,
                use_container_width=True,
            )

        else:

            st.html(
                f"""
                <div
                    class="rr-poster-frame"
                    style="
                        height:500px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                    "
                >

                    <div
                        style="
                            font-family:'DM Sans',sans-serif;
                            font-size:18px;
                            font-weight:700;
                            color:{CHARCOAL};
                            text-align:center;
                        "
                    >
                        {safe_title}
                    </div>

                </div>
                """,
            )


        st.html(
            f"""
            <div class="rr-poster-caption">
                {safe_zone}
            </div>
            """,
        )


    # ========================================================
    # INFORMATION
    # ========================================================

    with info_col:

        # ----------------------------------------------------
        # VERDICT
        # ----------------------------------------------------

        st.html(
            f"""
            <div class="rr-verdict">

                <span class="rr-verdict-dot"></span>

                {safe_verdict}

            </div>
            """,
        )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        st.html(
            f"""
            <div class="rr-movie-title">
                {safe_title}
            </div>

            <div class="rr-movie-year">
                {safe_year}
            </div>
            """,
        )


        # ----------------------------------------------------
        # RATING
        # ----------------------------------------------------

        star_text = _stars(rating)

        rating_text = _format_rating(
            rating
        )

        st.html(
            f"""
            <div class="rr-rating-box">

                <div class="rr-rating-label">
                    Roy's rating
                </div>

                <div class="rr-rating-value">

                    <span>
                        {star_text}
                    </span>

                    &nbsp;

                    {html.escape(rating_text)}

                </div>

            </div>
            """,
        )


        # ----------------------------------------------------
        # IMDb
        # ----------------------------------------------------

        if imdb_rating not in ("", None):

            imdb_display = (
                f"{html.escape(str(imdb_rating))}/10"
            )

        else:

            imdb_display = "Not available"


        # ----------------------------------------------------
        # META
        # ----------------------------------------------------

        st.html(
            f"""
            <div class="rr-meta-grid">

                <div class="rr-meta-item">

                    <div class="rr-meta-label">
                        Zone
                    </div>

                    <div class="rr-meta-value">
                        {safe_zone}
                    </div>

                </div>


                <div class="rr-meta-item">

                    <div class="rr-meta-label">
                        Genre
                    </div>

                    <div class="rr-meta-value">
                        {safe_genre}
                    </div>

                </div>


                <div class="rr-meta-item">

                    <div class="rr-meta-label">
                        IMDb
                    </div>

                    <div class="rr-meta-value">
                        {imdb_display}
                    </div>

                </div>


                <div class="rr-meta-item">

                    <div class="rr-meta-label">
                        Year
                    </div>

                    <div class="rr-meta-value">
                        {safe_year}
                    </div>

                </div>

            </div>
            """,
        )


        # ----------------------------------------------------
        # ROY'S REVIEW
        # ----------------------------------------------------

        st.html(
            """
            <div class="rr-review-heading">
                Roy's review
            </div>
            """,
        )

        st.html(
            f"""
            <div class="rr-review">

                <span class="rr-review-mark">
                    "
                </span>

                {safe_review}

                <span class="rr-review-mark">
                    "
                </span>

            </div>
            """,
        )


        # ====================================================
        # ASK ROY
        # ====================================================

        render_ask_roy(movie)


    # ========================================================
    # CLOSE MAIN MOVIE CARD
    # ========================================================

    st.html(
        "</div>",
    )


    # ========================================================
    # FOOTER
    # ========================================================

    st.html(
        """
        <div class="rr-details-footer">
            RoyReview · Movies, from Roy's perspective.
        </div>
        """,
    )