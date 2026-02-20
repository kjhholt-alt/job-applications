from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values

from .config import ENV_CANDIDATE_PATHS


def _load_env_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    values = dotenv_values(path)
    for key in [
        "ANTHROPIC_API_KEY",
        "CLAUDE_API_KEY",
        "RESEND_API_KEY",
        "RESEND_FROM",
        "RESEND_FROM_EMAIL",
        "WORKSPACE_ROOT",
        "JOB_FINDER_DATA_ROOT",
        "APP_USER",
        "APP_PASS",
        "APP_USER1",
        "APP_PASS1",
        "APP_USER2",
        "APP_PASS2",
        "APP_USER3",
        "APP_PASS3",
        "APP_USERS_JSON",
        "APP_USER_STORAGE",
    ]:
        if values.get(key):
            os.environ.setdefault(key, str(values.get(key)))
    return str(path)


def ensure_anthropic_key() -> tuple[Optional[str], Optional[str]]:
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
    if key:
        return key, None

    for path in ENV_CANDIDATE_PATHS:
        source = _load_env_file(path)
        if source:
            key = os.environ.get("ANTHROPIC_API_KEY")
            if key:
                return key, source

    return None, None


def ensure_resend_key() -> tuple[Optional[str], Optional[str]]:
    key = os.environ.get("RESEND_API_KEY")
    if key:
        return key, None

    for path in ENV_CANDIDATE_PATHS:
        source = _load_env_file(path)
        if source:
            key = os.environ.get("RESEND_API_KEY")
            if key:
                return key, source

    return None, None


def get_resend_from() -> Optional[str]:
    return os.environ.get("RESEND_FROM") or os.environ.get("RESEND_FROM_EMAIL")
