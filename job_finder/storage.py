from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .config import get_db_path


@dataclass
class JobRecord:
    job_id: str
    path: str
    bucket: str
    company: Optional[str]
    role: Optional[str]
    location: Optional[str]
    level: Optional[str]
    domain: Optional[str]
    skills: List[str]
    source: Optional[str]
    date_saved: Optional[str]
    liked: int
    body: str
    fingerprint_json: Optional[str]
    created_at: str
    updated_at: str


def _connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    resolved_path = db_path or get_db_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            path TEXT,
            bucket TEXT,
            company TEXT,
            role TEXT,
            location TEXT,
            level TEXT,
            domain TEXT,
            skills TEXT,
            source TEXT,
            date_saved TEXT,
            liked INTEGER DEFAULT 0,
            body TEXT,
            fingerprint_json TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            job_id TEXT PRIMARY KEY,
            status TEXT,
            notes TEXT,
            updated_at TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def _now() -> str:
    return datetime.utcnow().isoformat()


def upsert_job(job: Dict[str, Any]) -> None:
    init_db()
    conn = _connect()
    cur = conn.cursor()

    skills_json = json.dumps(job.get("skills") or [])
    fingerprint_json = json.dumps(job.get("fingerprint")) if job.get("fingerprint") else None

    cur.execute(
        """
        INSERT INTO jobs (
            job_id, path, bucket, company, role, location, level, domain, skills, source,
            date_saved, liked, body, fingerprint_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            path=excluded.path,
            bucket=excluded.bucket,
            company=excluded.company,
            role=excluded.role,
            location=excluded.location,
            level=excluded.level,
            domain=excluded.domain,
            skills=excluded.skills,
            source=excluded.source,
            date_saved=excluded.date_saved,
            liked=excluded.liked,
            body=excluded.body,
            fingerprint_json=excluded.fingerprint_json,
            updated_at=excluded.updated_at;
        """,
        (
            job.get("job_id"),
            job.get("path"),
            job.get("bucket"),
            job.get("company"),
            job.get("role"),
            job.get("location"),
            job.get("level"),
            job.get("domain"),
            skills_json,
            job.get("source"),
            job.get("date_saved"),
            int(job.get("liked") or 0),
            job.get("body"),
            fingerprint_json,
            job.get("created_at") or _now(),
            _now(),
        ),
    )
    conn.commit()
    conn.close()


def list_jobs(bucket: Optional[str] = None) -> List[JobRecord]:
    init_db()
    conn = _connect()
    cur = conn.cursor()
    if bucket:
        cur.execute("SELECT * FROM jobs WHERE bucket = ? ORDER BY updated_at DESC", (bucket,))
    else:
        cur.execute("SELECT * FROM jobs ORDER BY updated_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [_row_to_job(row) for row in rows]


def get_job(job_id: str) -> Optional[JobRecord]:
    init_db()
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_job(row)


def update_feedback(job_id: str, status: str, notes: Optional[str] = None) -> None:
    init_db()
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO feedback (job_id, status, notes, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            status=excluded.status,
            notes=excluded.notes,
            updated_at=excluded.updated_at;
        """,
        (job_id, status, notes, _now()),
    )
    conn.commit()
    conn.close()


def _row_to_job(row: sqlite3.Row) -> JobRecord:
    skills = []
    if row["skills"]:
        try:
            skills = json.loads(row["skills"])
        except json.JSONDecodeError:
            skills = []

    return JobRecord(
        job_id=row["job_id"],
        path=row["path"],
        bucket=row["bucket"],
        company=row["company"],
        role=row["role"],
        location=row["location"],
        level=row["level"],
        domain=row["domain"],
        skills=skills,
        source=row["source"],
        date_saved=row["date_saved"],
        liked=int(row["liked"] or 0),
        body=row["body"],
        fingerprint_json=row["fingerprint_json"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
