from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


@dataclass
class ParsedJob:
    meta: Dict[str, Any]
    body: str


def parse_front_matter(text: str) -> ParsedJob:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return ParsedJob(meta={}, body=text.strip())

    end = text.find("\n---", 4)
    if end == -1:
        return ParsedJob(meta={}, body=text.strip())

    raw_meta = text[4:end].strip()
    body = text[end + 4 :].strip()
    meta = yaml.safe_load(raw_meta) or {}
    if not isinstance(meta, dict):
        meta = {}
    return ParsedJob(meta=meta, body=body)


def parse_job_file(path: Path) -> ParsedJob:
    text = path.read_text(encoding="utf-8")
    return parse_front_matter(text)


def normalize_job_id(meta: Dict[str, Any], path: Path) -> str:
    if "id" in meta and meta["id"]:
        return str(meta["id"])
    if "company" in meta and "role" in meta and meta["company"] and meta["role"]:
        raw = f"{meta['company']}-{meta['role']}"
        return slugify(raw)
    return slugify(path.stem)


def slugify(value: str) -> str:
    out = []
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in [" ", "-", "_", ".", "/"]:
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def read_job_file(path: Path) -> Tuple[str, Dict[str, Any], str]:
    parsed = parse_job_file(path)
    job_id = normalize_job_id(parsed.meta, path)
    return job_id, parsed.meta, parsed.body
