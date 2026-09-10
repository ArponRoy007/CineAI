import streamlit as st


# ============================================================
# ROYREVIEW CONFIGURATION
# ============================================================

APP_NAME = "RoyReview"

DATABASE_NAME = "royreview"

# MongoDB collection names
USERS_COLLECTION_NAME = "users"
MOVIES_COLLECTION_NAME = "movies"
CONVERSATIONS_COLLECTION_NAME = "conversations"
USER_INTERACTIONS_COLLECTION_NAME = "user_interactions"

# Vector database collection
VECTOR_COLLECTION_NAME = "royreview_reviews"

# Hybrid recommendation model weights. Keep these together so tuning is
# deliberate and the final score remains easy to audit.
RECOMMENDER_CONTENT_WEIGHT = 0.18
RECOMMENDER_EMBEDDING_WEIGHT = 0.50
RECOMMENDER_RATING_WEIGHT = 0.08
RECOMMENDER_GENRE_WEIGHT = 0.14
RECOMMENDER_PERSONALIZATION_WEIGHT = 0.10
PERSONALIZATION_MIN_INTERACTIONS = 5


# ============================================================
# API KEYS
# ============================================================

MONGODB_URI = st.secrets["MONGODB_URI"]

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
