from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import feedparser
import requests

from .config import get_data_dir, get_inbox_dir
from .profile import InterestProfile

STATE_PATH = get_data_dir() / "alerts_state.json"


def load_state() -> Dict:
    if not STATE_PATH.exists():
        return {"seen": []}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: Dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def run_alerts(profile: InterestProfile) -> List[Path]:
    sources = profile.alert_sources
    if not sources:
        return []

    state = load_state()
    seen = set(state.get("seen", []))
    new_files = []

    for url in sources:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            entry_id = entry.get("id") or entry.get("link") or entry.get("title")
            if not entry_id or entry_id in seen:
                continue

            title = entry.get("title", "New Job")
            link = entry.get("link", "")
            summary = entry.get("summary", "")

            file_name = _safe_name(entry_id) + ".md"
            path = get_inbox_dir() / file_name
            content = _render_job_md(title, link, summary)
            path.write_text(content, encoding="utf-8")

            seen.add(entry_id)
            new_files.append(path)

    save_state({"seen": sorted(seen)})
    return new_files


def build_alert_email(new_files: List[Path]) -> str:
    items = "".join(
        [f"<li>{path.name}</li>" for path in new_files]
    )
    return (
        "<p>New job alerts added to your inbox:</p>"
        f"<ul>{items}</ul>"
        "<p>Open the Job Similarity Finder to ingest and score them.</p>"
    )


def _render_job_md(title: str, link: str, summary: str) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return (
        "---\n"
        f"role: {title}\n"
        f"source: {link}\n"
        f"date_saved: {today}\n"
        "---\n\n"
        f"{summary}\n"
    )


def _safe_name(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("-")
    name = "".join(out)
    while "--" in name:
        name = name.replace("--", "-")
    return name.strip("-")[:80]


def send_resend_email(api_key: str, to_email: str, subject: str, html: str, from_email: Optional[str] = None) -> None:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": from_email or "onboarding@resend.dev",
        "to": [to_email],
        "subject": subject,
        "html": html,
    }
    resp = requests.post("https://api.resend.com/emails", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
