import streamlit as st

from ai.personalization import build_preference_profile, log_interaction
from ai.recommender import recommend_similar_movies
from ui.ask_roy import render_ask_roy
from ui.design import esc, inject_design_system, render_nav


def _stars(rating):
    try:
        whole = int(float(rating))
        whole = max(0, min(5, whole))
        return "★" * whole + "☆" * (5 - whole)
    except (TypeError, ValueError):
        return "☆☆☆☆☆"


def render_recommendations(movie, user=None):
    """Render compact hybrid recommendations."""

    try:
        recommendations = recommend_similar_movies(
            movie,
            limit=6,
            profile=build_preference_profile(user),
        )
    except Exception as error:
        print(
            f"[Recommendations Error] "
            f"{type(error).__name__}: {error}"
        )
        return

    if not recommendations:
        return

    # ---------------------------------------------------------
    # Section heading
    # ---------------------------------------------------------
    st.html(
        """
        <div class="rr-section-head" style="margin-top:42px;">
            <div>
                <div class="rr-kicker">SIMILAR TO THIS</div>
                <h2>You might also like</h2>
                <p>
                    Chosen from Our collection by review similarity and taste.
                </p>
            </div>
        </div>
        """
    )

    # ---------------------------------------------------------
    # Three compact recommendation cards per row
    # ---------------------------------------------------------
    columns = st.columns(
        min(3, len(recommendations)),
        gap="medium",
    )

    for index, recommendation in enumerate(recommendations):

        with columns[index % len(columns)]:
            # Keep the 3-column grid; shrink each card ~18% inside its cell.
            _, card_col, _ = st.columns([0.09, 0.82, 0.09])
            with card_col:

                title = recommendation.get(
                    "title",
                    "Untitled",
                )

                poster = recommendation.get(
                    "poster_url"
                )

                verdict = recommendation.get(
                    "verdict",
                    "Roy's pick",
                )

                rating = recommendation.get(
                    "roy_rating",
                    "-",
                )

                year = recommendation.get(
                    "year",
                    "",
                )

                genre = recommendation.get(
                    "genre",
                    "Film",
                )

                score = recommendation.get(
                    "recommendation_score"
                )

                # -------------------------------------------------
                # Poster
                # -------------------------------------------------
                if poster:
                    st.image(
                        poster,
                        use_container_width=True,
                    )
                else:
                    st.html(
                        f"""
                        <div
                            style="
                                width:100%;
                                height:198px;
                                border-radius:12px;
                                background:#393A3A;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                color:#FFFFFF;
                                font-weight:600;
                                text-align:center;
                                padding:16px;
                                font-size:13px;
                            "
                        >
                            {esc(title)}
                        </div>
                        """
                    )

                # -------------------------------------------------
                # Compact card information
                # -------------------------------------------------
                score_html = ""

                if score is not None:
                    try:
                        score_html = (
                            f"""
                            <div
                                style="
                                    margin-top:4px;
                                    font-size:9px;
                                    color:#7B8285;
                                "
                            >
                                Match {float(score):.3f}
                            </div>
                            """
                        )
                    except (TypeError, ValueError):
                        pass

                st.html(
                    f"""
                    <div
                        style="
                            margin-top:7px;
                            margin-bottom:6px;
                        "
                    >

                        <div
                            style="
                                display:flex;
                                justify-content:space-between;
                                align-items:center;
                                gap:6px;
                                margin-bottom:5px;
                            "
                        >

                            <span
                                style="
                                    display:inline-block;
                                    padding:3px 7px;
                                    border-radius:999px;
                                    background:#F89344;
                                    color:#FFFFFF;
                                    font-size:8px;
                                    font-weight:700;
                                    text-transform:uppercase;
                                "
                            >
                                {esc(verdict)}
                            </span>

                            <span
                                style="
                                    font-size:10px;
                                    font-weight:600;
                                    color:#393A3A;
                                    white-space:nowrap;
                                "
                            >
                                {_stars(rating)}
                                {esc(rating)}/5
                            </span>

                        </div>

                        <div
                            style="
                                font-size:15px;
                                font-weight:700;
                                color:#17181C;
                                line-height:1.2;
                                margin-bottom:4px;
                            "
                        >
                            {esc(title)}
                        </div>

                        <div
                            style="
                                font-size:10px;
                                color:#7B8285;
                                line-height:1.4;
                            "
                        >
                            {esc(year)} · {esc(genre)}
                        </div>

                        {score_html}

                    </div>
                    """
                )

                movie_id = recommendation.get(
                    "movie_id",
                    recommendation.get(
                        "_id",
                        f"{title}_{index}",
                    ),
                )

                if st.button(
                    "View review",
                    key=f"recommended_{movie_id}_{index}",
                    use_container_width=True,
                ):
                    st.session_state["selected_movie"] = recommendation
                    st.session_state["ask_roy_answer"] = None
                    st.session_state["ask_roy_source"] = None
                    st.rerun()


def _log_view_once(movie, user):
    user_id = str((user or {}).get("user_id") or "").strip()
    movie_id = str(movie.get("movie_id") or movie.get("tmdb_id") or "").strip()
    if not user_id or not movie_id:
        return
    key = f"{user_id}:{movie_id}"
    if st.session_state.get("last_logged_view") != key:
        log_interaction(user, movie_id, "viewed")
        st.session_state["last_logged_view"] = key


def render_movie_details(movie, user=None):
    """Render the movie details page."""

    inject_design_system()
    render_nav(user)
    _log_view_once(movie, user)

    # ---------------------------------------------------------
    # Back button
    # ---------------------------------------------------------
    if st.button(
        "Back to collection",
        key="movie_details_back",
    ):
        st.session_state["selected_movie"] = None
        st.session_state["ask_roy_answer"] = None
        st.session_state["ask_roy_source"] = None
        st.rerun()

    title = movie.get(
        "title",
        "Unknown Film",
    )

    rating = movie.get(
        "roy_rating"
    )

    imdb = movie.get(
        "imdb_rating"
    )

    verdict = movie.get(
        "verdict",
        "Roy's pick",
    )

    year = movie.get(
        "year",
        "",
    )

    zone = movie.get(
        "zone",
        "Unknown",
    )

    genre = movie.get(
        "genre",
        "Unknown",
    )

    review_text = movie.get(
        "review_text",
        "Roy hasn't written a review for this film yet.",
    )

    # ---------------------------------------------------------
    # Hero section
    # ---------------------------------------------------------
    poster_col, content_col = st.columns(
        [0.38, 0.62],
        gap="large",
    )

    with poster_col:

        if movie.get("poster_url"):
            st.image(
                movie["poster_url"],
                use_container_width=True,
            )
        else:
            st.html(
                f"""
                <div
                    style="
                        width:100%;
                        min-height:480px;
                        border-radius:14px;
                        background:#393A3A;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        color:#FFFFFF;
                        font-weight:600;
                        text-align:center;
                        padding:30px;
                    "
                >
                    {esc(title)}
                </div>
                """
            )

    with content_col:

        if imdb:
            imdb_display = f"{esc(imdb)}/10"
        else:
            imdb_display = "Not available"

        # -----------------------------------------------------
        # Movie information
        # -----------------------------------------------------
        st.html(
            f"""
            <div class="rr-verdict">
                {esc(verdict)}
            </div>

            <h1 class="rr-movie-title">
                {esc(title)}
            </h1>

            <div class="rr-card-meta">
                {esc(year)}
            </div>

            <div class="rr-rating-block">

                <div
                    class="rr-kicker"
                    style="color:#FFFFFF"
                >
                    Our rating
                </div>

                <div class="rr-rating-stars">
                    {_stars(rating)}

                    <span
                        style="
                            color:#FFFFFF;
                            font-size:18px;
                            letter-spacing:0;
                        "
                    >
                        {esc(rating)}/5
                    </span>
                </div>

            </div>

            <div class="rr-stats">

                <div class="rr-stat">
                    <label>Zone</label>
                    <b>{esc(zone)}</b>
                </div>

                <div class="rr-stat">
                    <label>Genre</label>
                    <b>{esc(genre)}</b>
                </div>

                <div class="rr-stat">
                    <label>IMDb</label>
                    <b>{imdb_display}</b>
                </div>

                <div class="rr-stat">
                    <label>Year</label>
                    <b>{esc(year)}</b>
                </div>

            </div>

            <div class="rr-kicker">
                Our review
            </div>

            <div class="rr-quote">
                {esc(review_text)}
            </div>
            """
        )

    # ---------------------------------------------------------
    # PHASE 3
    # Recommendations BEFORE Ask Roy
    # ---------------------------------------------------------
    render_recommendations(movie, user)

    # ---------------------------------------------------------
    # Ask Roy
    # ---------------------------------------------------------
    render_ask_roy(movie, user)
