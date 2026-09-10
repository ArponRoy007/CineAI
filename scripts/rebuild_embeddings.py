import sys
from pathlib import Path

# ============================================================
# ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from database.mongodb import movies_collection
from rag.ingest import ingest_movie_review


# ============================================================
# REBUILD RAG EMBEDDINGS
# ============================================================

def main():

    try:
        movies = movies_collection.find(
            {
                "review_status": "CONFIRMED",
            }
        )
    except Exception as error:
        print(f"Could not load confirmed reviews: {type(error).__name__}: {error}")
        return

    total = 0
    successful = 0

    for movie in movies:

        total += 1

        title = movie.get(
            "title",
            "Unknown movie",
        )

        try:

            success = ingest_movie_review(
                movie
            )

            if success:

                movies_collection.update_one(
                    {
                        "_id": movie["_id"]
                    },
                    {
                        "$set": {
                            "ingest_to_rag": True
                        }
                    },
                )

                successful += 1

                print(
                    f"✓ {title}"
                )

            else:

                print(
                    f"✗ Skipped: {title}"
                )

        except Exception as error:

            print(
                f"✗ Failed: {title} → {error}"
            )

    print()
    print(
        f"Processed: {total}"
    )
    print(
        f"Successfully embedded: {successful}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
