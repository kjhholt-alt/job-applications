from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .claude import ClaudeClient
from .config import (
    get_applications_dir,
    get_base_resume_path,
    get_example_base_resume_path,
    get_inbox_dir,
    get_liked_dir,
    get_user_base_resume_path,
)
from .parser import read_job_file, slugify
from .storage import JobRecord, list_jobs, upsert_job


def _extract_meta(meta: Dict) -> Dict:
    return {
        "company": meta.get("company"),
        "role": meta.get("role"),
        "location": meta.get("location"),
        "level": meta.get("level"),
        "domain": meta.get("domain"),
        "skills": meta.get("skills") or [],
        "source": meta.get("source"),
        "date_saved": meta.get("date_saved"),
    }


def ingest_folder(folder: Path, bucket: str, client: Optional[ClaudeClient] = None) -> List[JobRecord]:
    ingested = []
    for path in folder.glob("*.md"):
        job_id, meta, body = read_job_file(path)
        fingerprint = None
        if client:
            fingerprint = client.extract_fingerprint(body)

        job = {
            "job_id": job_id,
            "path": str(path),
            "bucket": bucket,
            "liked": 1 if bucket == "liked" else 0,
            "body": body,
            "fingerprint": fingerprint,
            **_extract_meta(meta),
        }
        upsert_job(job)
        record = next((j for j in list_jobs() if j.job_id == job_id), None)
        if record:
            ingested.append(record)
    return ingested


def list_inbox_files() -> List[Path]:
    return sorted(get_inbox_dir().glob("*.md"))


def list_liked_files() -> List[Path]:
    return sorted(get_liked_dir().glob("*.md"))


def auto_import_applications_to_liked() -> int:
    count = 0
    for folder in get_applications_dir().glob("*"):
        if not folder.is_dir():
            continue
        job_file = folder / "job-description.md"
        if not job_file.exists():
            continue
        dest_name = f"{folder.name}-job-description.md"
        dest = get_liked_dir() / dest_name
        if dest.exists():
            continue
        shutil.copy2(job_file, dest)
        count += 1
    return count


def move_to_liked(job: JobRecord) -> Path:
    src = Path(job.path)
    if not src.exists():
        raise FileNotFoundError(f"Missing source file: {src}")
    dest = get_liked_dir() / src.name
    shutil.move(str(src), str(dest))
    job_update = {
        "job_id": job.job_id,
        "path": str(dest),
        "bucket": "liked",
        "liked": 1,
        "company": job.company,
        "role": job.role,
        "location": job.location,
        "level": job.level,
        "domain": job.domain,
        "skills": job.skills,
        "source": job.source,
        "date_saved": job.date_saved,
        "body": job.body,
        "fingerprint": json.loads(job.fingerprint_json) if job.fingerprint_json else None,
    }
    upsert_job(job_update)
    return dest


def create_application_folder(job: JobRecord, resume_md: str, cover_letter_md: str) -> Path:
    company = job.company or "company"
    role = job.role or "role"
    folder_name = slugify(f"{company}-{role}")
    dest_dir = get_applications_dir() / folder_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    job_path = dest_dir / "job-description.md"
    resume_path = dest_dir / "resume.md"
    cover_path = dest_dir / "cover-letter.md"

    if job.path:
        src = Path(job.path)
        if src.exists():
            job_path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        job_path.write_text(job.body or "", encoding="utf-8")

    if resume_md:
        resume_path.write_text(resume_md, encoding="utf-8")
    if cover_letter_md:
        cover_path.write_text(cover_letter_md, encoding="utf-8")

    return dest_dir


def load_base_resume() -> str:
    user_path = get_user_base_resume_path()
    if user_path.exists():
        return user_path.read_text(encoding="utf-8")

    base_path = get_base_resume_path()
    if base_path.exists():
        return base_path.read_text(encoding="utf-8")

    example_path = get_example_base_resume_path()
    if example_path.exists():
        return example_path.read_text(encoding="utf-8")

    return ""
