import requests
import streamlit as st


BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


class TMDBError(Exception):
    """Raised when a TMDB API request fails."""


# ============================================================
# TMDB API KEY
# ============================================================

def get_tmdb_api_key():
    """
    Read the TMDB API key from Streamlit secrets.
    """

    api_key = st.secrets.get(
        "TMDB_API_KEY",
        "",
    )

    if not api_key:
        raise TMDBError(
            "TMDB_API_KEY is not configured in Streamlit secrets."
        )

    return api_key


# ============================================================
# GENERIC TMDB REQUEST
# ============================================================

def tmdb_request(
    endpoint,
    params=None,
):
    """
    Send a request to TMDB.
    """

    api_key = get_tmdb_api_key()

    params = params.copy() if params else {}

    params["api_key"] = api_key

    try:

        response = requests.get(
            f"{BASE_URL}{endpoint}",
            params=params,
            timeout=15,
        )

    except requests.RequestException as error:

        raise TMDBError(
            f"TMDB request failed: {error}"
        )

    if response.status_code != 200:

        try:
            error_data = response.json()

            message = error_data.get(
                "status_message",
                "Unknown TMDB error",
            )

        except ValueError:

            message = response.text

        raise TMDBError(
            f"TMDB returned HTTP {response.status_code}: {message}"
        )

    try:

        return response.json()

    except ValueError:

        raise TMDBError(
            "TMDB returned an invalid JSON response."
        )


# ============================================================
# SEARCH MOVIE
# ============================================================

def search_movie(
    title,
    year=None,
):
    """
    Search TMDB using movie title and optional release year.

    Exact title matches are preferred.
    """

    title = (title or "").strip()

    if not title:
        return None

    params = {
        "query": title,
        "include_adult": False,
        "language": "en-US",
    }

    if year:
        params["year"] = int(year)

    data = tmdb_request(
        "/search/movie",
        params,
    )

    results = data.get(
        "results",
        [],
    )

    if not results:
        return None

    # --------------------------------------------------------
    # Prefer exact title match
    # --------------------------------------------------------

    normalized_title = title.lower()

    for movie in results:

        movie_title = (
            movie.get("title", "")
            .strip()
            .lower()
        )

        if movie_title == normalized_title:

            return movie

    # --------------------------------------------------------
    # Otherwise return best TMDB result
    # --------------------------------------------------------

    return results[0]


# ============================================================
# MOVIE DETAILS
# ============================================================

def get_movie_details(
    tmdb_id,
):
    """
    Get complete TMDB movie information.
    """

    if not tmdb_id:
        raise TMDBError(
            "TMDB movie ID is required."
        )

    return tmdb_request(
        f"/movie/{tmdb_id}",
        {
            "language": "en-US",
        },
    )


# ============================================================
# EXTERNAL IDS
# ============================================================

def get_external_ids(
    tmdb_id,
):
    """
    Get external IDs such as IMDb ID.
    """

    if not tmdb_id:
        raise TMDBError(
            "TMDB movie ID is required."
        )

    return tmdb_request(
        f"/movie/{tmdb_id}/external_ids"
    )


# ============================================================
# POSTER URL
# ============================================================

def get_poster_url(
    poster_path,
):
    """
    Convert a TMDB poster path into a full image URL.
    """

    if not poster_path:
        return None

    return (
        f"{POSTER_BASE_URL}"
        f"{poster_path}"
    )


# ============================================================
# BACKDROP URL
# ============================================================

def get_backdrop_url(
    backdrop_path,
):
    """
    Convert a TMDB backdrop path into a full image URL.
    """

    if not backdrop_path:
        return None

    return (
        f"{POSTER_BASE_URL}"
        f"{backdrop_path}"
    )


# ============================================================
# BUILD COMPLETE MOVIE METADATA
# ============================================================

def build_movie_metadata(
    title,
    year=None,
):
    """
    Search TMDB and build complete metadata for a movie.

    Returns:
        dict | None
    """

    search_result = search_movie(
        title,
        year,
    )

    if not search_result:
        return None

    tmdb_id = search_result.get(
        "id"
    )

    if not tmdb_id:
        return None

    details = get_movie_details(
        tmdb_id
    )

    external_ids = get_external_ids(
        tmdb_id
    )

    genres = [
        genre.get("name")
        for genre in details.get(
            "genres",
            []
        )
        if genre.get("name")
    ]

    release_date = details.get(
        "release_date"
    )

    return {
        # ----------------------------------------------------
        # TMDB
        # ----------------------------------------------------

        "tmdb_id": tmdb_id,

        "tmdb_title": details.get(
            "title"
        ),

        "original_title": details.get(
            "original_title"
        ),

        "overview": details.get(
            "overview",
            ""
        ),

        "release_date": release_date,

        "runtime": details.get(
            "runtime"
        ),

        "genres_tmdb": genres,

        "tmdb_rating": details.get(
            "vote_average"
        ),

        "tmdb_vote_count": details.get(
            "vote_count"
        ),

        # ----------------------------------------------------
        # IMAGES
        # ----------------------------------------------------

        "poster_url": get_poster_url(
            details.get(
                "poster_path"
            )
        ),

        "backdrop_url": get_backdrop_url(
            details.get(
                "backdrop_path"
            )
        ),

        # ----------------------------------------------------
        # EXTERNAL IDS
        # ----------------------------------------------------

        "imdb_id": external_ids.get(
            "imdb_id"
        ),

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        "metadata_source": "TMDB",
    }


# ============================================================
# ADMIN REVIEW ENRICHMENT
# ============================================================

def enrich_movie(
    title,
    year=None,
):
    """
    Find a movie on TMDB and return the information
    required by the Admin Review workflow.

    This is intentionally smaller than build_movie_metadata()
    because the Admin Dashboard mainly needs:

        TMDB ID
        poster
        title
        overview
        TMDB rating
    """

    try:
        metadata = build_movie_metadata(
            title=title,
            year=year,
        )
    except (TMDBError, ValueError, TypeError) as error:
        print(f"[TMDB Enrichment Error] {type(error).__name__}: {error}")
        metadata = None

    if not metadata:

        return {
            "tmdb_id": None,
            "poster_url": "",
            "tmdb_title": "",
            "tmdb_overview": "",
            "tmdb_rating": None,
            "imdb_id": None,
        }

    return {
        "tmdb_id": metadata.get(
            "tmdb_id"
        ),

        "poster_url": metadata.get(
            "poster_url",
            "",
        ),

        "tmdb_title": metadata.get(
            "tmdb_title",
            "",
        ),

        "tmdb_overview": metadata.get(
            "overview",
            "",
        ),

        "tmdb_rating": metadata.get(
            "tmdb_rating"
        ),

        "imdb_id": metadata.get(
            "imdb_id"
        ),
    }
