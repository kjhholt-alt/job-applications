from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .config import get_data_dir

PROFILE_PATH = get_data_dir() / "interest_profile.json"


@dataclass
class InterestProfile:
    focus_skills: List[str] = field(default_factory=list)
    focus_domains: List[str] = field(default_factory=list)
    focus_keywords: List[str] = field(default_factory=list)
    preferred_locations: List[str] = field(default_factory=list)
    preferred_levels: List[str] = field(default_factory=list)
    remote_preference: str = "any"  # any | remote | hybrid | onsite
    salary_min: int = 0
    reputable_only: bool = False
    alert_sources: List[str] = field(default_factory=list)
    alert_email_to: Optional[str] = None
    alert_email_enabled: bool = False


def load_profile() -> InterestProfile:
    if not PROFILE_PATH.exists():
        return InterestProfile()
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    return InterestProfile(
        focus_skills=_to_list(data.get("focus_skills")),
        focus_domains=_to_list(data.get("focus_domains")),
        focus_keywords=_to_list(data.get("focus_keywords")),
        preferred_locations=_to_list(data.get("preferred_locations")),
        preferred_levels=_to_list(data.get("preferred_levels")),
        remote_preference=data.get("remote_preference") or "any",
        salary_min=int(data.get("salary_min") or 0),
        reputable_only=bool(data.get("reputable_only")),
        alert_sources=_to_list(data.get("alert_sources")),
        alert_email_to=data.get("alert_email_to"),
        alert_email_enabled=bool(data.get("alert_email_enabled")),
    )


def save_profile(profile: InterestProfile) -> None:
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(_as_dict(profile), indent=2), encoding="utf-8")


def _to_list(value) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()]


def _as_dict(profile: InterestProfile) -> Dict:
    return {
        "focus_skills": profile.focus_skills,
        "focus_domains": profile.focus_domains,
        "focus_keywords": profile.focus_keywords,
        "preferred_locations": profile.preferred_locations,
        "preferred_levels": profile.preferred_levels,
        "remote_preference": profile.remote_preference,
        "salary_min": profile.salary_min,
        "reputable_only": profile.reputable_only,
        "alert_sources": profile.alert_sources,
        "alert_email_to": profile.alert_email_to,
        "alert_email_enabled": profile.alert_email_enabled,
    }
