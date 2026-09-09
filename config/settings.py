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

# Vector database collection
VECTOR_COLLECTION_NAME = "royreview_reviews"


# ============================================================
# API KEYS
# ============================================================

MONGODB_URI = st.secrets["MONGODB_URI"]

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]