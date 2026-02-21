from __future__ import annotations

import json
import math
from typing import Dict, Iterable, List

from .profile import InterestProfile


def _as_list(value) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v).lower().strip() for v in value if str(v).strip()]
    return [str(value).lower().strip()]


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    set_a = set(a)
    set_b = set(b)
    if not set_a and not set_b:
        return 0.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _token_overlap(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    tokens_a = {t for t in a.lower().replace("/", " ").split() if t}
    tokens_b = {t for t in b.lower().replace("/", " ").split() if t}
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def similarity(a: Dict, b: Dict) -> float:
    if not a or not b:
        return 0.0

    skills = _jaccard(_as_list(a.get("skills")), _as_list(b.get("skills")))
    tools = _jaccard(_as_list(a.get("tools")), _as_list(b.get("tools")))
    domains = _jaccard(_as_list(a.get("domains")), _as_list(b.get("domains")))
    keywords = _jaccard(_as_list(a.get("keywords")), _as_list(b.get("keywords")))
    industries = _jaccard(_as_list(a.get("industries")), _as_list(b.get("industries")))

    role_title = _token_overlap(str(a.get("role_title", "")), str(b.get("role_title", "")))
    role_family = _token_overlap(str(a.get("role_family", "")), str(b.get("role_family", "")))

    seniority = 1.0 if a.get("seniority") and a.get("seniority") == b.get("seniority") else 0.0

    score = (
        0.30 * skills
        + 0.15 * tools
        + 0.12 * domains
        + 0.10 * keywords
        + 0.08 * industries
        + 0.12 * role_title
        + 0.08 * role_family
        + 0.05 * seniority
    )

    return round(score, 4)


def aggregate_profile(fingerprints: List[Dict]) -> Dict:
    agg = {
        "skills": [],
        "tools": [],
        "domains": [],
        "keywords": [],
        "industries": [],
    }
    for fp in fingerprints:
        for key in agg.keys():
            agg[key].extend(_as_list(fp.get(key)))
    for key in agg.keys():
        agg[key] = sorted(set(agg[key]))
    return agg


def score_against_seed(job_fp: Dict, seed_fp: Dict) -> float:
    """Score a single job fingerprint directly against a seed fingerprint."""
    return similarity(job_fp, seed_fp)


def rank_by_seed(jobs_with_fps: List[tuple], seed_fp: Dict, top_n: int = 10) -> List[tuple]:
    """
    Rank (job, fingerprint_dict) pairs by similarity to seed_fp.
    Returns top_n as [(score, job), ...] sorted descending.
    """
    scored = [(similarity(fp, seed_fp), job) for job, fp in jobs_with_fps]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_n]


def score_against_liked(job_fp: Dict, liked_fps: List[Dict], profile: InterestProfile | None = None) -> float:
    if not liked_fps:
        return 0.0
    per_job = [similarity(job_fp, fp) for fp in liked_fps]
    best = max(per_job) if per_job else 0.0
    agg = aggregate_profile(liked_fps)
    agg_score = similarity(job_fp, agg)
    base_score = 0.7 * best + 0.3 * agg_score

    profile_boost = 0.0
    if profile:
        focus = {
            "skills": profile.focus_skills,
            "domains": profile.focus_domains,
            "keywords": profile.focus_keywords,
        }
        for key, values in focus.items():
            if values:
                profile_boost += 0.12 * _jaccard(_as_list(job_fp.get(key)), _as_list(values))

    score = base_score + profile_boost
    return round(min(score, 1.0), 4)
