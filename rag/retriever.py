from rag.embeddings import embed_text
from rag.vector_store import search_similar


def retrieve_reviews(
    question: str,
    top_k: int = 5,
    movie_title: str | None = None,
) -> list[dict]:
    """Retrieve Roy's review notes.

    When movie_title is supplied, only that movie's confirmed
    vector document is eligible. This prevents Ask Roy for one
    movie from returning semantically similar but unrelated films.
    """
    if not question or not question.strip():
        return []

    query_embedding = embed_text(question)

    results = search_similar(
        query_embedding=query_embedding,
        n_results=top_k,
        movie_title=movie_title,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        retrieved.append(
            {
                "document": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved


def build_context(
    question: str,
    top_k: int = 5,
    movie_title: str | None = None,
) -> tuple[str, list[dict]]:
    results = retrieve_reviews(
        question=question,
        top_k=top_k,
        movie_title=movie_title,
    )

    if not results:
        return "", []

    context_parts = []

    for index, item in enumerate(results, start=1):
        metadata = item["metadata"]

        title = metadata.get("title", "Unknown movie")
        year = metadata.get("year", "")
        zone = metadata.get("zone", "")
        genre = metadata.get("genre", "")
        rating = metadata.get("roy_rating", "")
        verdict = metadata.get("verdict", "")
        document = item["document"]

        context_parts.append(
            f"""SOURCE {index}
Movie: {title}
Year: {year}
Zone: {zone}
Genre: {genre}
Roy's Rating: {rating}/5
Verdict: {verdict}
Roy's Review: {document}"""
        )

    return "\n\n".join(context_parts), results
