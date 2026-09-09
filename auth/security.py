import bcrypt


# ============================================================
# ROYREVIEW — PASSWORD SECURITY
# ============================================================


def hash_password(password: str) -> str:
    """
    Hash a password securely using bcrypt.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plain-text password against
    a bcrypt password hash.
    """

    if not password or not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    except (ValueError, TypeError):
        return False