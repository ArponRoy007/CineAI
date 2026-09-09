from database.mongodb import movies_collection


def get_exact_movies(
    rating=None,
    verdict=None,
    zone=None,
    genre=None,
    min_rating=None,
):
    query = {
        "review_status": "CONFIRMED",
        "ingest_to_rag": True,
    }

    if rating is not None:
        query["roy_rating"] = float(rating)

    if verdict:
        query["verdict"] = verdict

    if zone:
        query["zone"] = zone

    if genre:
        query["genre"] = {
            "$regex": genre,
            "$options": "i",
        }

    if min_rating is not None:
        query["roy_rating"] = {
            "$gte": float(min_rating),
        }

    return list(
        movies_collection.find(
            query,
            {
                "_id": 0,
                "movie_id": 1,
                "title": 1,
                "year": 1,
                "zone": 1,
                "genre": 1,
                "roy_rating": 1,
                "verdict": 1,
                "review_text": 1,
            },
        ).sort(
            [
                ("roy_rating", -1),
                ("year", -1),
            ]
        )
    )


def format_exact_movies(movies):
    if not movies:
        return "No matching movies were found in Roy's confirmed movie notes."

    lines = []

    for movie in movies:
        title = movie.get("title", "Unknown")
        year = movie.get("year", "")
        rating = movie.get("roy_rating", "")
        verdict = movie.get("verdict", "")

        lines.append(
            f"- {title} ({year}) — {rating}/5 — {verdict}"
        )

    return "\n".join(lines)