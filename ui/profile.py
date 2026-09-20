"""Profile and edit-profile screens for authenticated RoyReview users."""

import html

import streamlit as st
from bson import ObjectId
from pymongo import ReturnDocument

from auth.security import hash_password, verify_password
from database.models import public_user
from database.mongodb import users_collection
from ui.design import esc, inject_design_system, render_nav


def _back_home():
    if st.button("Back to collection", key="profile_back"):
        st.session_state["view"] = "home"
        st.rerun()


def render_profile(user):
    inject_design_system()
    render_nav(user)
    _back_home()
    name = user.get("name") or user.get("username", "CineAI member")
    avatar = user.get("avatar_url", "")
    avatar_html = f'<img class="rr-profile-avatar" src="{esc(avatar)}" alt="{esc(name)}">' if avatar else f'<div class="rr-profile-avatar">{esc(name[:1].upper())}</div>'
    st.markdown(f'''<div class="rr-panel"><div style="display:flex;gap:20px;align-items:center">{avatar_html}<div><div class="rr-kicker">Profile</div><h1 style="margin:5px 0">{esc(name)}</h1><div class="rr-card-meta">@{esc(user.get("username"))} · {esc(user.get("email"))}</div></div></div></div>''', unsafe_allow_html=True)
    reviews = st.session_state.get("reviews_viewed", 0)
    cols = st.columns(3)
    stats = [("Reviews viewed", reviews), ("Favorite genre", user.get("favorite_genre") or "Not set"), ("Member since", "CineAI")]
    for col, (label, value) in zip(cols, stats):
        with col:
            st.markdown(f'<div class="rr-stat-card"><label>{esc(label)}</label><strong>{esc(value)}</strong></div>', unsafe_allow_html=True)
    if st.button("Edit profile", type="primary", key="profile_edit"):
        st.session_state["view"] = "edit_profile"
        st.rerun()


def render_edit_profile(user):
    inject_design_system()
    render_nav(user)
    _back_home()
    st.markdown('<div class="rr-section-head"><div><h2>Edit profile</h2><p>Choose what CineAI shows about you.</p></div></div>', unsafe_allow_html=True)
    with st.form("edit_profile_form"):
        name = st.text_input("Display name", value=user.get("name", ""))
        username = st.text_input("Username", value=user.get("username", ""))
        email = st.text_input("Email", value=user.get("email", ""))
        avatar_url = st.text_input("Avatar URL", value=user.get("avatar_url", ""), placeholder="https://...")
        favorite_genre = st.text_input("Favorite genre", value=user.get("favorite_genre", ""), placeholder="Optional")
        st.markdown("<div class='rr-kicker' style='margin-top:18px'>Change password</div>", unsafe_allow_html=True)
        current_password = st.text_input("Current password", type="password")
        new_password = st.text_input("New password", type="password", help="Leave both blank to keep your current password.")
        save = st.form_submit_button("Save changes", type="primary", use_container_width=True)
    if not save:
        return
    if not name.strip() or not username.strip() or not email.strip():
        st.error("Display name, username, and email are required.")
        return
    if new_password and len(new_password) < 8:
        st.error("New password must be at least 8 characters.")
        return
    if new_password:
        try:
            user_object_id = ObjectId(user.get("user_id", ""))
        except Exception:
            st.error("We couldn't verify this account. Please sign in again.")
            return
        record = users_collection.find_one({"_id": user_object_id})
        if not record or not current_password or not verify_password(current_password, record.get("password_hash", "")):
            st.error("Enter your current password to set a new one.")
            return
    existing = users_collection.find_one({"$or": [{"username": username.strip()}, {"email": email.strip().lower()}], "_id": {"$ne": user.get("user_id")}})
    if existing:
        st.error("That username or email is already in use.")
        return
    update = {"name": name.strip(), "username": username.strip(), "email": email.strip().lower(), "avatar_url": avatar_url.strip(), "favorite_genre": favorite_genre.strip()}
    if new_password:
        update["password_hash"] = hash_password(new_password)
    try:
        result = users_collection.find_one_and_update(
            {"_id": ObjectId(user["user_id"])},
            {"$set": update},
            return_document=ReturnDocument.AFTER,
        )
        st.session_state["current_user"] = public_user(result) | {"avatar_url": update["avatar_url"], "favorite_genre": update["favorite_genre"]}
        st.toast("Profile saved.")
        st.session_state["view"] = "profile"
        st.rerun()
    except Exception:
        st.error("We couldn't save those changes. Please try again.")
