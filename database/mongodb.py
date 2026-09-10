import streamlit as st
from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection


class _LazyCollection:
    """Delay network-backed collection construction until it is used."""

    def __init__(self, factory):
        self._factory = factory
        self._collection = None

    def _resolve(self):
        if self._collection is None:
            self._collection = self._factory()
        return self._collection

    def __getattr__(self, name):
        return getattr(self._resolve(), name)


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


def get_user_interactions_collection() -> Collection:
    """Return the append-only user interaction collection."""
    collection = get_database()[
        st.secrets.get(
            "USER_INTERACTIONS_COLLECTION_NAME",
            "user_interactions",
        )
    ]
    collection.create_index(
        [("user_id", ASCENDING), ("timestamp", ASCENDING)],
        name="user_interaction_history",
    )
    return collection


# Existing import seams used by the current RoyReview application. Keeping
# these lazy lets local tests and transient outages import the app safely.
movies_collection = _LazyCollection(get_movies_collection)
users_collection = _LazyCollection(get_users_collection)

# Interaction logging remains lazy in ai.personalization so a failure here can
# never block ordinary browsing, search, or Ask Roy requests.
