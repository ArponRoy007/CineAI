"""Read-only MongoDB analytics for the RoyReview admin dashboard."""

import altair as alt
import pandas as pd
import streamlit as st


NUMERIC_RATING = {
    "$match": {
        "roy_rating": {
            "$type": "number"
        }
    }
}


def _aggregate(collection, pipeline, label):
    """Run one analytics pipeline without taking the admin screen down."""
    try:
        return list(collection.aggregate(pipeline))
    except Exception as error:
        print(
            f"[Analytics {label} Error] "
            f"{type(error).__name__}: {error}"
        )
        return []


# -------------------------------------------------------------------
# MongoDB aggregation functions
# -------------------------------------------------------------------

def rating_distribution(collection):
    return _aggregate(
        collection,
        [
            NUMERIC_RATING,
            {
                "$group": {
                    "_id": "$roy_rating",
                    "count": {"$sum": 1},
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            },
        ],
        "rating distribution",
    )


def verdict_distribution(collection):
    return _aggregate(
        collection,
        [
            {
                "$match": {
                    "verdict": {
                        "$in": [
                            "Must Watch",
                            "Good Watch",
                            "Don't Watch",
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$verdict",
                    "count": {"$sum": 1},
                }
            },
            {
                "$sort": {
                    "count": -1,
                    "_id": 1,
                }
            },
        ],
        "verdict distribution",
    )


def genre_preferences(collection):
    return _aggregate(
        collection,
        [
            {
                "$match": {
                    "genre": {
                        "$type": "string",
                        "$ne": "",
                    },
                    "roy_rating": {
                        "$type": "number"
                    },
                }
            },
            {
                "$group": {
                    "_id": "$genre",
                    "count": {"$sum": 1},
                    "average_rating": {
                        "$avg": "$roy_rating"
                    },
                }
            },
            {
                "$sort": {
                    "count": -1,
                    "average_rating": -1,
                    "_id": 1,
                }
            },
        ],
        "genre preferences",
    )


def zone_ratings(collection):
    return _aggregate(
        collection,
        [
            {
                "$match": {
                    "zone": {
                        "$type": "string",
                        "$ne": "",
                    },
                    "roy_rating": {
                        "$type": "number"
                    },
                }
            },
            {
                "$group": {
                    "_id": "$zone",
                    "count": {"$sum": 1},
                    "average_rating": {
                        "$avg": "$roy_rating"
                    },
                }
            },
            {
                "$sort": {
                    "average_rating": -1,
                    "_id": 1,
                }
            },
        ],
        "zone ratings",
    )


def year_trends(collection):
    return _aggregate(
        collection,
        [
            {
                "$match": {
                    "year": {
                        "$type": "number"
                    },
                    "roy_rating": {
                        "$type": "number"
                    },
                }
            },
            {
                "$group": {
                    "_id": "$year",
                    "count": {"$sum": 1},
                    "average_rating": {
                        "$avg": "$roy_rating"
                    },
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            },
        ],
        "year trends",
    )


def highest_rated_movies(collection, limit=10):
    limit = max(1, min(int(limit), 50))

    return _aggregate(
        collection,
        [
            NUMERIC_RATING,
            {
                "$sort": {
                    "roy_rating": -1,
                    "year": -1,
                    "title": 1,
                }
            },
            {
                "$limit": limit
            },
            {
                "$project": {
                    "_id": 0,
                    "title": 1,
                    "year": 1,
                    "zone": 1,
                    "genre": 1,
                    "roy_rating": 1,
                    "verdict": 1,
                }
            },
        ],
        "highest rated",
    )


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _rows(records, fields):
    """Convert MongoDB aggregation output into chart-friendly rows."""
    return [
        {
            label: record.get(key)
            for key, label in fields.items()
        }
        for record in records
    ]


def _show_chart(chart):
    """Render an Altair chart safely in Streamlit."""
    st.altair_chart(
        chart,
        use_container_width=True,
    )


# -------------------------------------------------------------------
# Dashboard
# -------------------------------------------------------------------

def render_analytics(collection):
    """Render read-only analytics using MongoDB aggregation results."""

    st.markdown(
        """
        <div class="rr-section-head">
            <div>
                <div class="rr-kicker">Internal analytics</div>
                <h2>Roy's collection at a glance</h2>
                <p>Read-only aggregates calculated in MongoDB.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ================================================================
    # Rating + Verdict
    # ================================================================

    ratings = rating_distribution(collection)
    verdicts = verdict_distribution(collection)

    left, right = st.columns(2, gap="large")

    # -------------------- Rating distribution ----------------------

    with left:
        rating_rows = _rows(
            ratings,
            {
                "_id": "Rating",
                "count": "Movies",
            },
        )

        if rating_rows:
            frame = pd.DataFrame(rating_rows)

            chart = (
                alt.Chart(frame)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Rating:Q",
                        title="Roy's rating",
                        scale=alt.Scale(
                            domain=[0.5, 5.5]
                        ),
                    ),
                    y=alt.Y(
                        "Movies:Q",
                        title="Films",
                    ),
                    color=alt.value("#F89344"),
                    tooltip=[
                        alt.Tooltip(
                            "Rating:Q",
                            title="Rating",
                        ),
                        alt.Tooltip(
                            "Movies:Q",
                            title="Films",
                        ),
                    ],
                )
                .properties(
                    title="Rating distribution",
                    height=240,
                )
            )

            _show_chart(chart)

        else:
            st.info(
                "No movie data is available for this view yet."
            )

    # -------------------- Verdict distribution ---------------------

    with right:
        verdict_rows = _rows(
            verdicts,
            {
                "_id": "Verdict",
                "count": "Movies",
            },
        )

        if verdict_rows:
            frame = pd.DataFrame(verdict_rows)

            chart = (
                alt.Chart(frame)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Verdict:N",
                        title="Verdict",
                        sort="-y",
                    ),
                    y=alt.Y(
                        "Movies:Q",
                        title="Films",
                    ),
                    color=alt.value("#FF642F"),
                    tooltip=[
                        alt.Tooltip(
                            "Verdict:N",
                            title="Verdict",
                        ),
                        alt.Tooltip(
                            "Movies:Q",
                            title="Films",
                        ),
                    ],
                )
                .properties(
                    title="Verdict distribution",
                    height=240,
                )
            )

            _show_chart(chart)

        else:
            st.info(
                "No movie data is available for this view yet."
            )

    # ================================================================
    # Genre + Zone
    # ================================================================

    genres = _rows(
        genre_preferences(collection),
        {
            "_id": "Genre",
            "count": "Movies",
            "average_rating": "Average rating",
        },
    )

    zones = _rows(
        zone_ratings(collection),
        {
            "_id": "Zone",
            "count": "Movies",
            "average_rating": "Average rating",
        },
    )

    left, right = st.columns(2, gap="large")

    # -------------------- Genre preferences -----------------------

    with left:
        if genres:
            frame = pd.DataFrame(genres)

            chart = (
                alt.Chart(frame)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Genre:N",
                        title="Genre",
                        sort="-y",
                    ),
                    y=alt.Y(
                        "Average rating:Q",
                        title="Average rating",
                        scale=alt.Scale(
                            domain=[0, 5]
                        ),
                    ),
                    size=alt.Size(
                        "Movies:Q",
                        title="Films",
                    ),
                    color=alt.value("#B8D5E5"),
                    tooltip=[
                        alt.Tooltip(
                            "Genre:N",
                            title="Genre",
                        ),
                        alt.Tooltip(
                            "Movies:Q",
                            title="Films",
                        ),
                        alt.Tooltip(
                            "Average rating:Q",
                            title="Average rating",
                            format=".2f",
                        ),
                    ],
                )
                .properties(
                    title="Genre preferences",
                    height=240,
                )
            )

            _show_chart(chart)

        else:
            st.info(
                "No genre data is available yet."
            )

    # -------------------- Zone ratings -----------------------------

    with right:
        if zones:
            frame = pd.DataFrame(zones)

            chart = (
                alt.Chart(frame)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Zone:N",
                        title="Zone",
                        sort="-y",
                    ),
                    y=alt.Y(
                        "Average rating:Q",
                        title="Average rating",
                        scale=alt.Scale(
                            domain=[0, 5]
                        ),
                    ),
                    size=alt.Size(
                        "Movies:Q",
                        title="Films",
                    ),
                    color=alt.value("#393A3A"),
                    tooltip=[
                        alt.Tooltip(
                            "Zone:N",
                            title="Zone",
                        ),
                        alt.Tooltip(
                            "Movies:Q",
                            title="Films",
                        ),
                        alt.Tooltip(
                            "Average rating:Q",
                            title="Average rating",
                            format=".2f",
                        ),
                    ],
                )
                .properties(
                    title="Zone-wise ratings",
                    height=240,
                )
            )

            _show_chart(chart)

        else:
            st.info(
                "No zone data is available yet."
            )

    # ================================================================
    # Year-wise trend
    # ================================================================

    years = _rows(
        year_trends(collection),
        {
            "_id": "Year",
            "count": "Movies",
            "average_rating": "Average rating",
        },
    )

    if years:
        frame = pd.DataFrame(years)

        chart = (
            alt.Chart(frame)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "Year:Q",
                    title="Year",
                ),
                y=alt.Y(
                    "Average rating:Q",
                    title="Average rating",
                    scale=alt.Scale(
                        domain=[0, 5]
                    ),
                ),
                size=alt.Size(
                    "Movies:Q",
                    title="Films reviewed",
                ),
                color=alt.value("#FF642F"),
                tooltip=[
                    alt.Tooltip(
                        "Year:Q",
                        title="Year",
                    ),
                    alt.Tooltip(
                        "Movies:Q",
                        title="Films",
                    ),
                    alt.Tooltip(
                        "Average rating:Q",
                        title="Average rating",
                        format=".2f",
                    ),
                ],
            )
            .properties(
                title="Year-wise rating trend",
                height=240,
            )
        )

        _show_chart(chart)

    else:
        st.info(
            "No year-wise movie data is available yet."
        )

    # ================================================================
    # Highest-rated movies
    # ================================================================

    st.markdown(
        """
        <div class="rr-section-head">
            <div>
                <h2>Highest-rated films</h2>
                <p>Top 10 by Roy's rating.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_movies = highest_rated_movies(collection)

    if top_movies:
        st.dataframe(
            top_movies,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "No rated movies are available yet."
        )