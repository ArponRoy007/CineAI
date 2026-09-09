import streamlit as st
from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection


@st.cache_resource
def get_mongo_client() -> MongoClient:
    """Create and cache the MongoDB Atlas client."""

    uri = st.secrets.get("MONGODB_URI", "")

    if not uri:
        raise ValueError(
            "MONGODB_URI is not configured in Streamlit secrets."
        )

    return MongoClient(
        uri,
        serverSelectionTimeoutMS=10000,
    )


def get_database():
    """Return the RoyReview MongoDB database."""

    database_name = st.secrets.get(
        "DATABASE_NAME",
        "royreview",
    )

    return get_mongo_client()[database_name]


def get_movies_collection() -> Collection:
    """Return the movies collection."""

    collection_name = st.secrets.get(
        "MOVIES_COLLECTION_NAME",
        "movies",
    )

    return get_database()[collection_name]


def get_users_collection() -> Collection:
    """Return the users collection."""

    collection = get_database()["users"]

    # Safe to call repeatedly because MongoDB ignores an
    # existing identical index.
    collection.create_index(
        [("username", ASCENDING)],
        unique=True,
        name="unique_username",
    )

    collection.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="unique_email",
    )

    return collection


# Existing import used by the current RoyReview application.
movies_collection = get_movies_collection()

# New authentication collection.
users_collection = get_users_collection()
