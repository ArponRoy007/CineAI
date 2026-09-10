from datetime import datetime, timezone


def build_user_document(
    name: str,
    username: str,
    email: str,
    password_hash: str,
    role: str = "user",
) -> dict:
    """Build a MongoDB document for a RoyReview user."""

    return {
        "name": name.strip(),
        "username": username.strip(),
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }


def public_user(user: dict | None) -> dict | None:
    """Remove private fields before putting user data in session state."""
    if not user:
        return None

    return {
        "user_id": str(user.get("_id", "")),
        "name": user.get("name", ""),
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "user"),
        "is_active": bool(user.get("is_active", True)),
        "avatar_url": user.get("avatar_url", ""),
        "favorite_genre": user.get("favorite_genre", ""),
    }
