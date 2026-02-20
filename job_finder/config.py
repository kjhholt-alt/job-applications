from __future__ import annotations

import os
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1]


def get_data_root() -> Path:
    data_root = os.environ.get("JOB_FINDER_DATA_ROOT") or os.environ.get("WORKSPACE_ROOT")
    if data_root:
        return Path(data_root).resolve()
    return CODE_ROOT


def get_data_dir() -> Path:
    return get_data_root() / "data"


def get_db_path() -> Path:
    return get_data_dir() / "jobs.db"


def get_jobs_dir() -> Path:
    return get_data_root() / "jobs"


def get_inbox_dir() -> Path:
    return get_jobs_dir() / "inbox"


def get_liked_dir() -> Path:
    return get_jobs_dir() / "liked"


def get_templates_dir() -> Path:
    return CODE_ROOT / "templates"


def get_base_resume_path() -> Path:
    return get_templates_dir() / "base-resume.md"


def get_applications_dir() -> Path:
    return get_data_root() / "applications"


def get_user_templates_dir() -> Path:
    return get_data_root() / "templates"


def get_user_base_resume_path() -> Path:
    return get_user_templates_dir() / "base-resume.md"


def get_example_base_resume_path() -> Path:
    return get_templates_dir() / "base-resume.example.md"


# Backwards-compatible constants (resolved at import time)
DATA_DIR = get_data_dir()
DB_PATH = get_db_path()
JOBS_DIR = get_jobs_dir()
INBOX_DIR = get_inbox_dir()
LIKED_DIR = get_liked_dir()
TEMPLATES_DIR = get_templates_dir()
BASE_RESUME_PATH = get_base_resume_path()
APPLICATIONS_DIR = get_applications_dir()

ENV_CANDIDATE_PATHS = [
    CODE_ROOT / ".env",
    CODE_ROOT / ".env.local",
    CODE_ROOT / ".env.production",
]
