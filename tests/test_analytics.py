from ui.analytics import (
    genre_preferences,
    highest_rated_movies,
    rating_distribution,
    verdict_distribution,
    year_trends,
    zone_ratings,
)


class AggregateCollection:
    """Fixture collection that returns known aggregation output by pipeline shape."""

    def __init__(self):
        self.pipelines = []

    def aggregate(self, pipeline):
        self.pipelines.append(pipeline)
        group = next((stage["$group"] for stage in pipeline if "$group" in stage), None)
        if group and group["_id"] == "$roy_rating":
            return [{"_id": 3.0, "count": 1}, {"_id": 5.0, "count": 2}]
        if group and group["_id"] == "$verdict":
            return [{"_id": "Must Watch", "count": 2}, {"_id": "Don't Watch", "count": 1}]
        if group and group["_id"] == "$genre":
            return [{"_id": "Thriller", "count": 2, "average_rating": 4.5}, {"_id": "Drama", "count": 1, "average_rating": 3.0}]
        if group and group["_id"] == "$zone":
            return [{"_id": "Bollywood", "count": 2, "average_rating": 4.5}, {"_id": "Hollywood", "count": 1, "average_rating": 3.0}]
        if group and group["_id"] == "$year":
            return [{"_id": 1993, "count": 1, "average_rating": 5.0}, {"_id": 2023, "count": 2, "average_rating": 3.5}]
        if any("$project" in stage for stage in pipeline):
            return [{"title": "Darr", "year": 1993, "roy_rating": 5.0, "verdict": "Must Watch"}]
        return []


def test_rating_distribution_uses_aggregation_and_returns_known_counts():
    collection = AggregateCollection()
    assert rating_distribution(collection) == [{"_id": 3.0, "count": 1}, {"_id": 5.0, "count": 2}]
    assert collection.pipelines[0][-1] == {"$sort": {"_id": 1}}


def test_verdict_distribution_uses_aggregation_and_returns_known_counts():
    collection = AggregateCollection()
    assert verdict_distribution(collection)[0] == {"_id": "Must Watch", "count": 2}
    assert "$group" in collection.pipelines[0][1]


def test_genre_preferences_returns_count_and_average_rating():
    collection = AggregateCollection()
    assert genre_preferences(collection)[0] == {"_id": "Thriller", "count": 2, "average_rating": 4.5}


def test_zone_ratings_returns_count_and_average_rating():
    collection = AggregateCollection()
    assert zone_ratings(collection)[1] == {"_id": "Hollywood", "count": 1, "average_rating": 3.0}


def test_year_trends_returns_movies_and_average_rating_per_year():
    collection = AggregateCollection()
    assert year_trends(collection) == [{"_id": 1993, "count": 1, "average_rating": 5.0}, {"_id": 2023, "count": 2, "average_rating": 3.5}]


def test_highest_rated_movies_limits_results_in_mongodb_pipeline():
    collection = AggregateCollection()
    assert highest_rated_movies(collection, limit=3)[0]["title"] == "Darr"
    assert {"$limit": 3} in collection.pipelines[0]


def test_empty_collection_returns_empty_analytics_without_crashing():
    class EmptyCollection:
        def aggregate(self, _pipeline):
            return []

    collection = EmptyCollection()
    assert rating_distribution(collection) == []
    assert verdict_distribution(collection) == []
    assert genre_preferences(collection) == []
    assert zone_ratings(collection) == []
    assert year_trends(collection) == []
    assert highest_rated_movies(collection) == []


def test_analytics_chart_encodings_compile_for_dictionary_rows():
    import altair as alt
    import pandas as pd

    chart = alt.Chart(pd.DataFrame([{"Rating": 5.0, "Movies": 2}])).mark_bar().encode(
        x=alt.X("Rating:Q"),
        y=alt.Y("Movies:Q"),
        tooltip=[alt.Tooltip("Rating:Q"), alt.Tooltip("Movies:Q")],
    )
    assert chart.to_dict()["encoding"]["tooltip"][0]["type"] == "quantitative"
