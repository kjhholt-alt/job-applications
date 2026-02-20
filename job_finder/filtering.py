from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import get_data_dir
from .profile import InterestProfile

REPUTABLE_LIST_PATH = get_data_dir() / "reputable_companies.txt"

SALARY_REGEX = re.compile(r"\$\s?(\d{2,3})(?:,?\d{3})?\s?(k|K)?")


def extract_salary(text: str) -> Optional[int]:
    if not text:
        return None
    matches = SALARY_REGEX.findall(text)
    if not matches:
        return None
    values = []
    for raw, kflag in matches:
        try:
            val = int(raw)
        except ValueError:
            continue
        if kflag:
            val *= 1000
        # Heuristic: ignore very low numbers that are likely not salary
        if val < 30000:
            continue
        values.append(val)
    if not values:
        return None
    return max(values)


def load_reputable_companies() -> List[str]:
    if not REPUTABLE_LIST_PATH.exists():
        return []
    return [line.strip().lower() for line in REPUTABLE_LIST_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_reputable_companies(lines: List[str]) -> None:
    REPUTABLE_LIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPUTABLE_LIST_PATH.write_text("\n".join(lines), encoding="utf-8")


@dataclass
class FilterResult:
    salary_value: Optional[int]
    salary_flag_low: bool
    salary_unknown: bool
    location_flag: bool
    reputable_flag: bool
    notes: List[str]


def evaluate_filters(job_body: str, company: Optional[str], job_fp: dict, profile: InterestProfile) -> FilterResult:
    notes: List[str] = []
    salary_value = extract_salary(job_body)
    salary_unknown = salary_value is None
    salary_flag_low = False

    if salary_unknown:
        notes.append("Salary not listed")
    elif profile.salary_min and salary_value < profile.salary_min:
        salary_flag_low = True
        notes.append(f"Salary below ${profile.salary_min}")

    location_flag = False
    preferred_locations = [loc.lower() for loc in profile.preferred_locations]
    location_type = (job_fp.get("location_type") or "").lower()

    if preferred_locations:
        if location_type == "remote":
            pass
        else:
            # Check if any preferred location keyword appears in the job text
            text = job_body.lower()
            if not any(loc in text for loc in preferred_locations):
                location_flag = True
                notes.append("Location not preferred (needs remote)")

    reputable_flag = False
    if profile.reputable_only:
        allowlist = load_reputable_companies()
        if not allowlist:
            reputable_flag = True
            notes.append("Reputable list empty")
        else:
            company_norm = (company or "").lower()
            if company_norm not in allowlist:
                reputable_flag = True
                notes.append("Company not in reputable list")

    return FilterResult(
        salary_value=salary_value,
        salary_flag_low=salary_flag_low,
        salary_unknown=salary_unknown,
        location_flag=location_flag,
        reputable_flag=reputable_flag,
        notes=notes,
    )
