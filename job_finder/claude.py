from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

import requests


class ClaudeClient:
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or os.environ.get("CLAUDE_MODEL") or "claude-sonnet-4-20250514"
        self.base_url = "https://api.anthropic.com/v1/messages"

    def _request(self, system: str, user: str, max_tokens: int = 1200) -> Dict[str, Any]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("content") or []
        text = ""
        for block in content:
            if block.get("type") == "text":
                text += block.get("text", "")
        return {"text": text, "raw": data}

    def extract_fingerprint(self, job_text: str) -> Dict[str, Any]:
        system = (
            "You extract structured job fingerprints for similarity matching. "
            "Return ONLY valid JSON without markdown or commentary."
        )
        user = (
            "Extract a concise fingerprint of this job description. "
            "Return JSON with keys: role_title, role_family, seniority, industries, domains, "
            "skills, tools, responsibilities, keywords, location_type. "
            "All list fields must be arrays of strings (lowercase, no duplicates). "
            "seniority should be one of: intern, entry, mid, senior, manager, director, exec, unknown. "
            "location_type should be one of: onsite, hybrid, remote, unknown.\n\n"
            f"JOB DESCRIPTION:\n{job_text}\n"
        )
        result = self._request(system, user, max_tokens=1200)
        return _parse_json(result["text"])

    def generate_tailored_docs(self, base_resume: str, job_text: str) -> Tuple[str, str]:
        system = (
            "You are a resume and cover letter writer. "
            "Return ONLY valid JSON without markdown or commentary."
        )
        user = (
            "Create a tailored resume and cover letter using the base resume and job description. "
            "Return JSON with keys: resume_md, cover_letter_md. "
            "Keep resume concise (1-2 pages in markdown). "
            "Use bullet points, preserve factual accuracy from base resume, and align to job keywords. "
            "Do not invent roles, dates, degrees, or metrics.\n\n"
            f"BASE RESUME (SOURCE OF TRUTH):\n{base_resume}\n\n"
            f"JOB DESCRIPTION:\n{job_text}\n"
        )
        result = self._request(system, user, max_tokens=4000)
        data = _parse_json(result["text"])
        resume_md = data.get("resume_md", "")
        cover_letter_md = data.get("cover_letter_md", "")
        return resume_md.strip(), cover_letter_md.strip()


def _parse_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return {}
    return {}
