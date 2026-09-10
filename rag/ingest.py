from rag.embeddings import embed_text
from rag.vector_store import upsert_documents


def build_review_document(movie: dict) -> str:
    """
    Convert one confirmed movie review into the document
    that will be stored in the vector database.
    """

    title = movie.get("title", "Unknown movie")
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
Verdict: {verdict}
Roy's Review: {review}
""".strip()


def ingest_movie_review(movie: dict) -> bool:
    """
    Add/update one confirmed movie review in ChromaDB.

    Returns True when ingestion succeeds.
    """

    if movie.get("review_status") != "CONFIRMED":
        return False

    if not movie.get("review_text", "").strip():
        return False

    try:
        document = build_review_document(movie)
        embedding = embed_text(document)
        movie_id = str(movie.get("movie_id") or movie.get("tmdb_id") or movie.get("title"))
        metadata = {
            "movie_id": movie_id,
            "title": str(movie.get("title", "")),
            "year": int(movie.get("year", 0)),
            "zone": str(movie.get("zone", "")),
            "genre": str(movie.get("genre", "")),
            "roy_rating": float(movie.get("roy_rating", 0)),
            "verdict": str(movie.get("verdict", "")),
        }
        return bool(upsert_documents(ids=[movie_id], documents=[document], embeddings=[embedding], metadatas=[metadata]))
    except Exception as error:
        print(f"[RAG Ingestion Error] {type(error).__name__}: {error}")
        return False
