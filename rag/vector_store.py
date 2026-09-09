from pathlib import Path

import chromadb

from config.settings import VECTOR_COLLECTION_NAME


CHROMA_PATH = Path("chroma_db")

_client = None
_collection = None


def get_chroma_client():
    global _client

    if _client is None:
        CHROMA_PATH.mkdir(exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

    return _client


def get_vector_collection():
    global _collection

    if _collection is None:
        client = get_chroma_client()

        _collection = client.get_or_create_collection(
            name=VECTOR_COLLECTION_NAME,
            metadata={
                "description": (
                    "RoyReview movie review knowledge base"
                )
            },
        )

    return _collection


def upsert_documents(
    ids,
    documents,
    embeddings,
    metadatas,
):
    if not ids:
        return

    get_vector_collection().upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search_similar(
    query_embedding,
    n_results=5,
    movie_title=None,
):
    collection = get_vector_collection()

    if collection.count() == 0:
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    where = None

    if movie_title:
        where = {
            "title": movie_title.strip()
        }

        # A movie-specific query should never fall back to another
        # movie if the requested title is not in the knowledge base.
        matching = collection.get(
            where=where,
            include=["metadatas"],
        )

        if not matching.get("ids"):
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

    n_results = min(
        n_results,
        collection.count(),
    )

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )


def collection_count():
    return get_vector_collection().count()


def clear_collection():
    global _collection

    client = get_chroma_client()

    try:
        client.delete_collection(
            name=VECTOR_COLLECTION_NAME
        )
    except Exception:
        pass

    _collection = None
