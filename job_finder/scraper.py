"""
Job scraper using LinkedIn's public guest API.
No authentication, no API key, no C extensions — just requests + bs4.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .parser import slugify

# ── Constants ────────────────────────────────────────────────────────────────

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_LI_SEARCH = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    "?keywords={keywords}&location={location}&count={count}&start={start}"
)
_LI_DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"


# ── Search term extraction ────────────────────────────────────────────────────

def extract_search_terms(fingerprints: List[Dict]) -> List[str]:
    """
    Derive search queries from liked-job fingerprints.
    Prioritises role_title, then role_family + top domain combos.
    Returns up to 4 distinct terms.
    """
    terms: list[str] = []
    seen: set[str] = set()

    for fp in fingerprints:
        role_title = (fp.get("role_title") or "").strip()
        role_family = (fp.get("role_family") or "").strip()
        domains = [d for d in (fp.get("domains") or []) if d]

        if role_title and role_title.lower() not in seen:
            terms.append(role_title)
            seen.add(role_title.lower())

        # e.g. "finance AI" + "manager/consultant"
        if role_family and domains:
            for domain in domains[:2]:
                combo = f"{domain} {role_family}".strip()
                if combo.lower() not in seen:
                    terms.append(combo)
                    seen.add(combo.lower())

    return terms[:4]


# ── LinkedIn guest scraper ────────────────────────────────────────────────────

def _search_linkedin(keywords: str, location: str, count: int = 25) -> List[Dict]:
    """Fetch one page of LinkedIn job cards (guest API)."""
    url = _LI_SEARCH.format(
        keywords=requests.utils.quote(keywords),
        location=requests.utils.quote(location),
        count=count,
        start=0,
    )
    try:
        r = requests.get(url, headers=_HEADERS, timeout=15)
        r.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []

    for card in soup.select("li"):
        # Job ID
        job_id = None
        a_tag = card.select_one("a[data-tracking-id]") or card.select_one("a.base-card__full-link")
        if not a_tag:
            a_tag = card.select_one("a[href*='/jobs/view/']")
        if a_tag:
            href = a_tag.get("href", "")
            m = re.search(r"/jobs/view/(\d+)", href)
            if m:
                job_id = m.group(1)

        if not job_id:
            # Try data attribute
            entity = card.get("data-entity-urn", "")
            m = re.search(r":(\d+)$", entity)
            if m:
                job_id = m.group(1)

        if not job_id:
            continue

        title_el = card.select_one("h3.base-search-card__title") or card.select_one("h3")
        company_el = card.select_one("h4.base-search-card__subtitle") or card.select_one("h4")
        location_el = card.select_one("span.job-search-card__location")

        jobs.append({
            "job_id": job_id,
            "title": title_el.get_text(strip=True) if title_el else "Unknown Role",
            "company": company_el.get_text(strip=True) if company_el else "Unknown Company",
            "location": location_el.get_text(strip=True) if location_el else location,
            "url": f"https://www.linkedin.com/jobs/view/{job_id}",
        })

    return jobs


def _fetch_description(job_id: str) -> Optional[str]:
    """Fetch full job description from LinkedIn guest detail endpoint."""
    url = _LI_DETAIL.format(job_id=job_id)
    try:
        r = requests.get(url, headers=_HEADERS, timeout=15)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Primary selector
    desc_el = (
        soup.select_one("div.show-more-less-html__markup")
        or soup.select_one("section.description")
        or soup.select_one("div.description__text")
        or soup.select_one("div[class*='description']")
    )

    if desc_el:
        # Convert to clean plain text
        text = desc_el.get_text(separator="\n", strip=True)
        return text if len(text) > 80 else None

    return None


# ── Public interface ──────────────────────────────────────────────────────────

def scrape_similar_jobs(
    fingerprints: List[Dict],
    location: str = "United States",
    results_per_term: int = 15,
    delay: float = 1.5,
    on_progress: Optional[Any] = None,
) -> List[Dict]:
    """
    Search LinkedIn for jobs similar to the given fingerprints.
    Returns a list of job dicts with keys:
      title, company, location, url, description, search_term
    """
    search_terms = extract_search_terms(fingerprints)
    if not search_terms:
        return []

    all_jobs: list[Dict] = []
    seen_ids: set[str] = set()

    total_steps = len(search_terms)
    for step, term in enumerate(search_terms):
        if on_progress:
            on_progress(step, total_steps, f"Searching: {term}…")

        cards = _search_linkedin(term, location, count=results_per_term)

        for card in cards:
            jid = card["job_id"]
            if jid in seen_ids:
                continue
            seen_ids.add(jid)

            time.sleep(delay)
            description = _fetch_description(jid)
            if not description:
                continue

            all_jobs.append({
                "title": card["title"],
                "company": card["company"],
                "location": card["location"],
                "url": card["url"],
                "description": description,
                "search_term": term,
            })

    return all_jobs


# ── Save to inbox ─────────────────────────────────────────────────────────────

def save_jobs_to_inbox(jobs: List[Dict], inbox_dir: Path) -> List[Path]:
    """
    Write each job as a .md file with YAML frontmatter into inbox_dir.
    Returns list of paths saved.
    """
    saved: list[Path] = []
    inbox_dir.mkdir(parents=True, exist_ok=True)

    for job in jobs:
        company = job.get("company", "company")
        title = job.get("title", "role")
        slug = slugify(f"{company}-{title}")

        path = inbox_dir / f"{slug}.md"
        counter = 1
        while path.exists():
            path = inbox_dir / f"{slug}-{counter}.md"
            counter += 1

        frontmatter = (
            f"---\n"
            f"company: {company}\n"
            f"role: {title}\n"
            f"location: {job.get('location', '')}\n"
            f"source: linkedin ({job.get('url', '')})\n"
            f"search_term: {job.get('search_term', '')}\n"
            f"---\n\n"
        )

        path.write_text(frontmatter + job["description"], encoding="utf-8")
        saved.append(path)

    return saved
