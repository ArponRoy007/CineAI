import streamlit as st

from auth.security import hash_password
from database.models import build_user_document
from database.mongodb import users_collection


def username_exists(username: str) -> bool:
    return users_collection.find_one(
        {"username": username.strip()}
    ) is not None


def email_exists(email: str) -> bool:
    return users_collection.find_one(
        {"email": email.strip().lower()}
    ) is not None


def create_user(
    name: str,
    username: str,
    email: str,
    password: str,
) -> tuple[bool, str]:
    """Create a normal RoyReview user."""

    name = name.strip()
    username = username.strip()
    email = email.strip().lower()

    if not name or not username or not email or not password:
        return False, "All fields are required."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    try:
        if username_exists(username):
            return False, "Username is already registered."

        if email_exists(email):
            return False, "Email is already registered."

        password_hash = hash_password(password)

        document = build_user_document(
            name=name,
            username=username,
            email=email,
            password_hash=password_hash,
            role="user",
        )

        users_collection.insert_one(document)
        return True, "Account created successfully."

    except Exception as error:
        print(f"[Signup MongoDB Error] {type(error).__name__}: {error}")
        return False, "Account creation is temporarily unavailable. Please try again."


def render_signup() -> None:
    """Render the RoyReview signup screen."""

    st.markdown("## Create your RoyReview account")
    st.caption("Join RoyReview to explore movies and Ask Roy.")

    with st.form("royreview_signup_form"):
        name = st.text_input(
            "Full name",
            placeholder="Your name",
        )

        username = st.text_input(
            "Username",
            placeholder="Choose a username",
        )

        email = st.text_input(
            "Email",
            placeholder="you@example.com",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="At least 8 characters",
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Repeat your password",
        )

        submitted = st.form_submit_button(
            "Create account",
            use_container_width=True,
        )

    if submitted:
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        success, message = create_user(
            name=name,
            username=username,
            email=email,
            password=password,
        )

        if success:
            st.success(message)
            st.info("You can now sign in.")
        else:
            st.error(message)
