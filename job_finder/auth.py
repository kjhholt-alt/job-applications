from __future__ import annotations

import json
import os
from typing import List, Tuple

import streamlit as st


def _load_auth_pairs() -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []

    raw_json = os.environ.get("APP_USERS_JSON")
    if raw_json:
        try:
            payload = json.loads(raw_json)
            if isinstance(payload, list):
                for item in payload:
                    username = str(item.get("username", "")).strip()
                    password = str(item.get("password", "")).strip()
                    if username and password:
                        pairs.append((username, password))
        except json.JSONDecodeError:
            pass

    single_user = os.environ.get("APP_USER")
    single_pass = os.environ.get("APP_PASS")
    if single_user and single_pass:
        pairs.append((single_user, single_pass))

    for idx in range(1, 4):
        user = os.environ.get(f"APP_USER{idx}")
        password = os.environ.get(f"APP_PASS{idx}")
        if user and password:
            pairs.append((user, password))

    return pairs


def require_login() -> str | None:
    pairs = _load_auth_pairs()
    if not pairs:
        return None

    if st.session_state.get("auth_ok"):
        return st.session_state.get("auth_user")

    st.title("Sign In")
    with st.form("auth_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Enter")

    if submitted:
        for user, pw in pairs:
            if username == user and password == pw:
                st.session_state["auth_ok"] = True
                st.session_state["auth_user"] = user
                st.success("Signed in")
                st.rerun()
        st.error("Invalid credentials")

    st.stop()
