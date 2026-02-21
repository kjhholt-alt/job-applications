"""
Job scraper — LinkedIn (primary) + Indeed RSS (fallback).
Uses a warmed-up requests.Session so LinkedIn doesn't block cold requests.
No API key, no C extensions — just requests, bs4, feedparser.
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .parser import slugify

# ── Browser headers ───────────────────────────────────────────────────────────

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

_BASE_HEADERS = {
    "User-Agent": _UA,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}

# ── Search term extraction ────────────────────────────────────────────────────

def extract_search_terms(fingerprints: List[Dict]) -> List[str]:
    """Derive search queries from liked-job fingerprints (up to 4 terms)."""
    terms: list[str] = []
    seen: set[str] = set()

    for fp in fingerprints:
        role_title = (fp.get("role_title") or "").strip()
        role_family = (fp.get("role_family") or "").strip()
        domains = [d for d in (fp.get("domains") or []) if d]

        if role_title and role_title.lower() not in seen:
            terms.append(role_title)
            seen.add(role_title.lower())

        if role_family and domains:
            for domain in domains[:2]:
                combo = f"{domain} {role_family}".strip()
                if combo.lower() not in seen:
                    terms.append(combo)
                    seen.add(combo.lower())

    return terms[:4]


# ── LinkedIn scraper ──────────────────────────────────────────────────────────

def _make_session() -> requests.Session:
    """Create a session with cookies by visiting LinkedIn's public jobs page."""
    session = requests.Session()
    session.headers.update(_BASE_HEADERS)
    try:
        session.get(
            "https://www.linkedin.com/jobs/search/?keywords=manager&location=United+States",
            timeout=15,
        )
        time.sleep(1.5)
    except Exception:
        pass
    return session


def _extract_job_id_from_href(href: str) -> Optional[str]:
    """Pull the numeric job ID from a LinkedIn /jobs/view/ URL."""
    # Pattern: /jobs/view/some-title-at-company-1234567890
    m = re.search(r"/jobs/view/[^?/]*?(\d{8,})", href)
    if m:
        return m.group(1)
    # Fallback: just find any long number in the URL
    m = re.search(r"(\d{9,})", href)
    return m.group(1) if m else None


def _search_linkedin(
    session: requests.Session, keywords: str, location: str, count: int = 20
) -> List[Dict]:
    """Fetch job cards from LinkedIn's guest search API."""
    url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={requests.utils.quote(keywords)}"
        f"&location={requests.utils.quote(location)}"
        f"&count={count}&start=0"
    )
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []

    for card in soup.select("li"):
        a_tag = (
            card.select_one("a.base-card__full-link")
            or card.select_one("a[href*='/jobs/view/']")
        )
        if not a_tag:
            continue

        href = a_tag.get("href", "")
        job_id = _extract_job_id_from_href(href)
        if not job_id:
            continue

        title_el = card.select_one("h3.base-search-card__title") or card.select_one("h3")
        company_el = card.select_one("h4.base-search-card__subtitle") or card.select_one("h4")
        loc_el = card.select_one("span.job-search-card__location")

        jobs.append({
            "job_id": job_id,
            "title": title_el.get_text(strip=True) if title_el else "Unknown Role",
            "company": company_el.get_text(strip=True) if company_el else "Unknown Company",
            "location": loc_el.get_text(strip=True) if loc_el else location,
            "url": f"https://www.linkedin.com/jobs/view/{job_id}",
        })

    return jobs


def _fetch_description_linkedin(session: requests.Session, job_id: str) -> Optional[str]:
    """Fetch a job's full description from LinkedIn's guest detail endpoint."""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    desc_el = (
        soup.select_one("div.show-more-less-html__markup")
        or soup.select_one("div.description__text")
        or soup.select_one("section.description")
    )

    if desc_el:
        text = desc_el.get_text(separator="\n", strip=True)
        return text if len(text) > 80 else None

    return None


# ── Indeed RSS fallback ───────────────────────────────────────────────────────

def _search_indeed_rss(keywords: str, location: str, count: int = 20) -> List[Dict]:
    """
    Pull jobs from Indeed's RSS feed — very reliable, no cookies needed.
    Descriptions are short summaries (not full JDs) but good enough to fingerprint.
    """
    try:
        import feedparser
    except ImportError:
        return []

    url = (
        f"https://www.indeed.com/rss"
        f"?q={requests.utils.quote(keywords)}"
        f"&l={requests.utils.quote(location)}"
        f"&limit={count}"
    )
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    jobs = []
    for entry in feed.entries[:count]:
        raw_title = entry.get("title", "")
        # Indeed titles are "Job Title - Company - Location"
        parts = [p.strip() for p in raw_title.split(" - ")]
        title = parts[0] if parts else raw_title
        company = parts[1] if len(parts) > 1 else "Unknown Company"
        loc = parts[2] if len(parts) > 2 else location

        # Strip HTML from summary
        summary_html = entry.get("summary", "")
        summary = BeautifulSoup(summary_html, "html.parser").get_text(separator="\n", strip=True)

        job_url = entry.get("link", "")

        if not summary or len(summary) < 50:
            continue

        jobs.append({
            "job_id": job_url,  # use URL as unique key
            "title": title,
            "company": company,
            "location": loc,
            "url": job_url,
            "description": summary,
        })

    return jobs


# ── Public interface ──────────────────────────────────────────────────────────

def scrape_similar_jobs(
    fingerprints: List[Dict],
    location: str = "United States",
    results_per_term: int = 15,
    delay: float = 1.5,
    on_progress: Optional[Callable] = None,
) -> List[Dict]:
    """
    Search LinkedIn (+ Indeed fallback) for jobs matching the fingerprints.
    Returns list of dicts: title, company, location, url, description, search_term, source.
    """
    search_terms = extract_search_terms(fingerprints)
    if not search_terms:
        return []

    if on_progress:
        on_progress(0, len(search_terms) + 1, "Initializing session…")

    session = _make_session()
    all_jobs: list[Dict] = []
    seen_ids: set[str] = set()
    total = len(search_terms)

    for step, term in enumerate(search_terms):
        if on_progress:
            on_progress(step, total, f"Searching LinkedIn: {term}…")

        # ── LinkedIn ──
        cards = _search_linkedin(session, term, location, count=results_per_term)

        li_found = 0
        for card in cards:
            jid = card["job_id"]
            if jid in seen_ids:
                continue
            seen_ids.add(jid)

            time.sleep(delay)
            description = _fetch_description_linkedin(session, jid)
            if not description:
                continue

            all_jobs.append({
                "title": card["title"],
                "company": card["company"],
                "location": card["location"],
                "url": card["url"],
                "description": description,
                "search_term": term,
                "source": "linkedin",
            })
            li_found += 1

        # ── Indeed fallback if LinkedIn gave nothing ──
        if li_found == 0:
            if on_progress:
                on_progress(step, total, f"LinkedIn empty — trying Indeed: {term}…")
            indeed_jobs = _search_indeed_rss(term, location, count=results_per_term)
            for job in indeed_jobs:
                jid = job["job_id"]
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)
                job["search_term"] = term
                job["source"] = "indeed"
                all_jobs.append(job)

        time.sleep(delay)

    return all_jobs


# ── Save to inbox ─────────────────────────────────────────────────────────────

def save_jobs_to_inbox(jobs: List[Dict], inbox_dir: Path) -> List[Path]:
    """Write each job as a .md file with YAML frontmatter into inbox_dir."""
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
            f"source: {job.get('source', 'scraped')} ({job.get('url', '')})\n"
            f"search_term: \"{job.get('search_term', '')}\"\n"
            f"---\n\n"
        )

        path.write_text(frontmatter + job["description"], encoding="utf-8")
        saved.append(path)

    return saved
