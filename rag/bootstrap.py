"""Deployment-safe initialization for RoyReview's vector store."""

import logging

from rag.vector_store import collection_count
from rag.ingest import ingest_movie_review
from database.mongodb import movies_collection


LOGGER = logging.getLogger("royreview.bootstrap")


def ensure_vector_store():
    """
    Ensure ChromaDB contains embeddings for all confirmed RoyReview reviews.

    Streamlit Community Cloud may start with a fresh filesystem, so the
    local ChromaDB collection is rebuilt from MongoDB when it is empty.
    """

    try:
        count = collection_count()

        if count > 0:
            LOGGER.info(
                "RoyReview vector store ready: %s documents.",
                count,
            )
            return count

        LOGGER.info(
            "RoyReview vector store is empty. "
            "Building embeddings from confirmed MongoDB reviews..."
        )

        movies = movies_collection.find(
            {
                "review_status": "CONFIRMED",
            }
        )

        successful = 0
        failed = 0

        for movie in movies:
            try:
                success = ingest_movie_review(movie)

                if success:
                    movies_collection.update_one(
                        {
                            "_id": movie["_id"],
                        },
                        {
                            "$set": {
                                "ingest_to_rag": True,
                            },
                        },
                    )

                    successful += 1

            except Exception as error:
                failed += 1

                LOGGER.warning(
                    "Failed to embed %s: %s",
                    movie.get("title", "Unknown movie"),
                    error,
                )

        final_count = collection_count()

        LOGGER.info(
            "Vector store initialization complete: "
            "%s embedded, %s failed, %s total in ChromaDB.",
            successful,
            failed,
            final_count,
        )

        return final_count

    except Exception as error:
        LOGGER.exception(
            "Vector store initialization failed: %s",
            error,
        )

        # Do not crash the whole Streamlit application if the
        # vector store cannot be initialized.
        return 0
