import streamlit as st

from database.mongodb import movies_collection
from movies.tmdb import enrich_movie


def get_count(query=None):

    if query is None:
        query = {}

    return movies_collection.count_documents(
        query
    )


def render_explore():

    st.markdown(
        """
        <div class="rr-explore-panel">

            <div class="rr-explore-title">
                Explore
            </div>

            <div class="rr-explore-subtitle">
                Browse Roy's collection
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    must_watch = get_count(
        {"verdict": "Must Watch"}
    )

    good_watch = get_count(
        {"verdict": "Good Watch"}
    )

    dont_watch = get_count(
        {"verdict": "Don't Watch"}
    )

    five_star = get_count(
        {"roy_rating": 5.0}
    )

    if st.button(
        f"››› Must Watch  ·  {must_watch}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "Must Watch"
        )

        st.session_state.page = "explore_results"

        st.rerun()

    if st.button(
        f"››› Good Watch  ·  {good_watch}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "Good Watch"
        )

        st.session_state.page = "explore_results"

        st.rerun()

    if st.button(
        f"››› Don't Watch  ·  {dont_watch}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "Don't Watch"
        )

        st.session_state.page = "explore_results"

        st.rerun()

    if st.button(
        f"››› ★★★★★  ·  {five_star}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "5 Star"
        )

        st.session_state.page = "explore_results"

        st.rerun()


def render_explore_results():

    filter_name = st.session_state.get(
        "explore_filter",
        "Must Watch",
    )

    if filter_name == "5 Star":

        query = {
            "roy_rating": 5.0
        }

    else:

        query = {
            "verdict": filter_name
        }

    movies = list(
        movies_collection.find(
            query,
            {"_id": 0},
        )
        .sort("roy_rating", -1)
    )

    st.markdown(
        f"""
        <div class="rr-result-header">

            <div class="rr-kicker">
                EXPLORE
            </div>

            <h1>
                {filter_name}
            </h1>

            <p>
                {len(movies)} movies in this collection.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "← Explore",
        key="back_explore",
    ):

        st.session_state.page = "explore"
        st.rerun()

    columns = st.columns(4)

    for index, movie in enumerate(movies):

        with columns[index % 4]:

            poster = movie.get(
                "poster_url"
            )

            title = movie.get(
                "title",
                "Movie",
            )

            rating = movie.get(
                "roy_rating",
                0,
            )

            if poster:

                st.image(
                    poster,
                    use_container_width=True,
                )

            else:

                st.markdown(
                    """
                    <div class="rr-small-poster">
                        🎬
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="rr-grid-title">
                    {title}
                </div>

                <div class="rr-grid-rating">
                    ★ {rating}/5
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Open",
                key=f"explore_{movie.get('movie_id')}",
                use_container_width=True,
            ):

                st.session_state.selected_movie_id = (
                    movie.get("movie_id")
                )

                st.session_state.page = "movie"

                st.rerun()