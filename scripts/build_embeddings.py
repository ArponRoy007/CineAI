import sys
from pathlib import Path

# Allow imports from project root when this script
# is executed as: python scripts/build_embeddings.py
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from database.mongodb import movies_collection
from rag.embeddings import embed_texts
from rag.vector_store import (
    upsert_documents,
    collection_count,
)


def create_document(movie: dict) -> str:
    """
    Build the text that will be embedded.

    This contains Roy's actual review plus structured
    information about the movie.
    """

    title = movie.get("title", "")
    year = movie.get("year", "")
    zone = movie.get("zone", "")
    genre = movie.get("genre", "")
    rating = movie.get("roy_rating", "")
    verdict = movie.get("verdict", "")
    review = movie.get("review_text", "")

    return f"""
Movie: {title}
Year: {year}
Zone: {zone}
Genre: {genre}
Roy's Rating: {rating}/5
Roy's Verdict: {verdict}
Roy's Review: {review}
""".strip()


def main():

    print("=" * 60)
    print("ROYREVIEW RAG EMBEDDING BUILDER")
    print("=" * 60)

    movies = list(
        movies_collection.find(
            {
                "review_status": "CONFIRMED",
                "ingest_to_rag": True,
            }
        )
    )

    print(f"\nConfirmed RAG movies found: {len(movies)}")

    if not movies:
        print("No movies available for RAG.")
        return

    documents = []
    ids = []
    metadatas = []

    for movie in movies:

        movie_id = str(
            movie.get(
                "movie_id",
                movie.get("_id"),
            )
        )

        document = create_document(movie)

        documents.append(document)
        ids.append(movie_id)

        metadatas.append(
            {
                "movie_id": movie_id,
                "title": str(movie.get("title", "")),
                "year": int(movie.get("year", 0)),
                "zone": str(movie.get("zone", "")),
                "genre": str(movie.get("genre", "")),
                "roy_rating": float(
                    movie.get("roy_rating", 0)
                ),
                "verdict": str(
                    movie.get("verdict", "")
                ),
            }
        )

    print("\nCreating embeddings...")

    embeddings = embed_texts(documents)

    print(
        f"Generated {len(embeddings)} embeddings."
    )

    print("\nSaving vectors to ChromaDB...")

    upsert_documents(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print("\n" + "=" * 60)
    print("RAG BUILD COMPLETE")
    print("=" * 60)

    print(
        f"Vector documents: {collection_count()}"
    )

    print("\nYour RAG knowledge base is ready.")


if __name__ == "__main__":
    main()
