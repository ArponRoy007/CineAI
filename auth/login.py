import streamlit as st

from auth.security import verify_password
from database.models import public_user
from database.mongodb import users_collection


def authenticate_user(identifier: str, password: str) -> dict | None:
    """
    Authenticate a normal user or admin.

    Admin credentials are read from Streamlit Secrets.
    Normal users are read from MongoDB.
    """

    identifier = (identifier or "").strip()

    if not identifier or not password:
        return None

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------
    admin_username = st.secrets.get(
        "ADMIN_USERNAME",
        "",
    )

    admin_password = st.secrets.get(
        "ADMIN_PASSWORD",
        "",
    )

    if (
        admin_username
        and admin_password
        and identifier.lower() == admin_username.lower()
        and password == admin_password
    ):
        return {
            "user_id": "admin",
            "name": admin_username,
            "username": admin_username,
            "email": "",
            "role": "admin",
            "is_active": True,
        }

    # --------------------------------------------------------
    # NORMAL USER
    # --------------------------------------------------------
    user = users_collection.find_one(
        {
            "$or": [
                {"username": identifier},
                {"email": identifier.lower()},
            ],
            "is_active": True,
        }
    )

    if not user:
        return None

    password_hash = user.get("password_hash", "")

    if not verify_password(
        password=password,
        password_hash=password_hash,
    ):
        return None

    return public_user(user)


def login_user(identifier: str, password: str) -> bool:
    """Authenticate and store the user in Streamlit session state."""

    user = authenticate_user(
        identifier=identifier,
        password=password,
    )

    if not user:
        return False

    st.session_state["authenticated"] = True
    st.session_state["current_user"] = user
    st.session_state["user_role"] = user.get(
        "role",
        "user",
    )

    return True


def logout_user() -> None:
    """Clear authentication-related session state."""

    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.session_state["user_role"] = None


def is_authenticated() -> bool:
    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
    )


def is_admin() -> bool:
    return (
        is_authenticated()
        and st.session_state.get(
            "user_role"
        ) == "admin"
    )


def current_user() -> dict | None:
    return st.session_state.get(
        "current_user"
    )


def render_login() -> None:
    """Render the RoyReview login screen."""

    st.markdown("## Welcome back to RoyReview")
    st.caption("Sign in to continue.")

    with st.form("royreview_login_form"):
        identifier = st.text_input(
            "Username or email",
            placeholder="Enter username or email",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
        )

        submitted = st.form_submit_button(
            "Sign in",
            use_container_width=True,
        )

    if submitted:
        if login_user(
            identifier=identifier,
            password=password,
        ):
            st.success("Signed in successfully.")
            st.rerun()
        else:
            st.error(
                "Invalid username/email or password."
            )
