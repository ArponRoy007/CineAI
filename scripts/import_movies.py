import csv
import sys
from pathlib import Path

import streamlit as st

from pymongo import MongoClient

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from movies.tmdb import (
    build_movie_metadata,
    TMDBError,
)


# ============================================================
# PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "RoyReview_Milestone2_Master.csv"
)


# ============================================================
# DATABASE
# ============================================================

def get_database():

    client = MongoClient(
        st.secrets["MONGODB_URI"],
        serverSelectionTimeoutMS=10000,
    )

    client.admin.command("ping")

    return client["royreview"]


# ============================================================
# IMPORT
# ============================================================

def import_movies():

    print("=" * 60)
    print("🎬 RoyReview Movie Import")
    print("=" * 60)

    if not CSV_PATH.exists():

        print(
            f"❌ CSV not found:\n{CSV_PATH}"
        )

        sys.exit(1)

    db = get_database()

    movies = db["movies"]

    processed = 0
    failed = 0
    inserted = 0
    modified = 0

    with open(
        CSV_PATH,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            movie_id = row.get(
                "movie_id"
            )

            title = row.get(
                "title"
            )

            if not movie_id or not title:
                failed += 1
                continue

            try:

                year = row.get("year")

                if year:
                    year = int(year)

                # ------------------------------------------------
                # Existing Roy data
                # ------------------------------------------------

                document = {
                    "movie_id": movie_id,
                    "title": title,
                    "year": year,

                    "zone": row.get(
                        "zone",
                        "",
                    ),

                    "genre": row.get(
                        "genre",
                        "",
                    ),

                    "roy_rating": (
                        float(row["roy_rating"])
                        if row.get("roy_rating")
                        else None
                    ),

                    "verdict": row.get(
                        "verdict",
                        "",
                    ),

                    "review_text": row.get(
                        "review_text",
                        "",
                    ),

                    "review_char_count": (
                        int(row["review_char_count"])
                        if row.get("review_char_count")
                        else 0
                    ),

                    "review_source": row.get(
                        "review_source",
                        "user_provided",
                    ),

                    "review_status": row.get(
                        "review_status",
                        "CONFIRMED",
                    ),

                    "ingest_to_rag": (
                        row.get(
                            "ingest_to_rag",
                            ""
                        ).upper()
                        == "YES"
                    ),
                }

                # ------------------------------------------------
                # TMDB
                # ------------------------------------------------

                print(
                    f"\n🔎 {title} ({year})"
                )

                metadata = build_movie_metadata(
                    title,
                    year,
                )

                if metadata:

                    document.update(
                        metadata
                    )

                    print(
                        f"   ✅ TMDB ID: "
                        f"{metadata.get('tmdb_id')}"
                    )

                    print(
                        f"   🖼️ Poster: "
                        f"{'YES' if metadata.get('poster_url') else 'NO'}"
                    )

                else:

                    print(
                        "   ⚠️ TMDB match not found"
                    )

                # ------------------------------------------------
                # Upsert
                # ------------------------------------------------

                result = movies.update_one(
                    {
                        "movie_id": movie_id
                    },
                    {
                        "$set": document
                    },
                    upsert=True,
                )

                if result.upserted_id:

                    inserted += 1

                elif result.modified_count:

                    modified += 1

                processed += 1

            except TMDBError as error:

                print(
                    f"   ⚠️ TMDB error: {error}"
                )

                # Still save Roy's movie data.
                movies.update_one(
                    {
                        "movie_id": movie_id
                    },
                    {
                        "$set": document
                    },
                    upsert=True,
                )

                processed += 1

            except Exception as error:

                failed += 1

                print(
                    f"   ❌ Failed: {error}"
                )

    print("\n" + "=" * 60)
    print("📊 IMPORT SUMMARY")
    print("=" * 60)

    print(
        f"Processed: {processed}"
    )

    print(
        f"Inserted: {inserted}"
    )

    print(
        f"Modified: {modified}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        f"Movies in MongoDB: "
        f"{movies.count_documents({})}"
    )

    print("=" * 60)

    print(
        "\n🎉 Movie enrichment finished!"
    )


if __name__ == "__main__":
    import_movies()