"""
Jarvis AIOS — Aggregator Job Provider
--------------------------------------
Queries verified live job APIs (RemoteOK, Arbeitnow, and optional Adzuna API).
Strict Zero-Fabrication: If APIs are offline or return 0 items, returns an empty list.
Never invents fake companies, salaries, or phantom opportunities.
"""

import html
import logging
import re
import time
from typing import Any, Dict, List, Optional
import httpx

from app.Config import settings
from app.Jobs.models.job_opportunity import JobOpportunity, JobSearchFilters
from app.Jobs.providers.base import BaseJobProvider
from app.Jobs.services.skill_normalizer import skill_normalizer

logger = logging.getLogger(__name__)


def clean_html_tags(text: str) -> str:
    """Strip HTML markup from API descriptions."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = html.unescape(clean)
    return " ".join(clean.split())


class AggregatorJobProvider(BaseJobProvider):
    """Job provider aggregating authentic public tech job board feeds."""

    def __init__(self) -> None:
        self._cache: Dict[str, List[JobOpportunity]] = {}
        self._cache_timestamp: Dict[str, float] = {}
        self._job_lookup: Dict[str, JobOpportunity] = {}
        self._last_statuses: Dict[str, str] = {}
        self.cache_ttl_seconds = 300  # 5 minutes

    @property
    def last_statuses(self) -> Dict[str, str]:
        """Return dict of provider name to status: 'ok', 'rate_limited', 'unavailable', 'not_configured'."""
        return dict(self._last_statuses)

    def get_status_summary(self, total_jobs: int) -> str:
        """Provide an honest status description for search results."""
        if total_jobs > 0:
            return f"Found {total_jobs} verified opportunities."

        statuses = list(self._last_statuses.values())
        if not statuses or all(s == "not_configured" for s in statuses):
            return "Live job search is not configured."
        if any(s == "rate_limited" for s in statuses):
            return "Live job provider rate limit reached. Please try again shortly."
        if all(s in ["unavailable", "not_configured"] for s in statuses):
            return "No live job results are currently available."
        return "No matching opportunities were found."

    def search_jobs(self, filters: JobSearchFilters) -> List[JobOpportunity]:
        """Search authentic opportunities across live feeds and apply filtering."""
        cache_key = f"{filters.role}_{filters.location}_{filters.is_remote}_{filters.employment_type}"
        now = time.time()

        if cache_key in self._cache and (now - self._cache_timestamp.get(cache_key, 0)) < self.cache_ttl_seconds:
            logger.debug("[JOB-PROVIDER] Returning %d cached results", len(self._cache[cache_key]))
            return self._apply_filters(self._cache[cache_key], filters)

        self._last_statuses = {}
        all_jobs: List[JobOpportunity] = []

        # 1. Query RemoteOK API (Public Tech / Remote / AI Opportunities)
        remote_ok_jobs = self._fetch_remoteok_jobs(filters)
        all_jobs.extend(remote_ok_jobs)

        # 2. Query Arbeitnow API (Tech Job Board API)
        arbeitnow_jobs = self._fetch_arbeitnow_jobs(filters)
        all_jobs.extend(arbeitnow_jobs)

        # 3. Optional: Query Adzuna API if keys are configured
        adzuna_app_id = getattr(settings, "ADZUNA_APP_ID", None)
        adzuna_app_key = getattr(settings, "ADZUNA_APP_KEY", None)
        if adzuna_app_id and adzuna_app_key:
            adzuna_jobs = self._fetch_adzuna_jobs(filters, adzuna_app_id, adzuna_app_key)
            all_jobs.extend(adzuna_jobs)
        else:
            self._last_statuses["Adzuna"] = "not_configured"

        # 4. Optional: Query JSearch (Live Google Jobs for India & Global)
        rapidapi_key = getattr(settings, "RAPIDAPI_KEY", None)
        if rapidapi_key:
            jsearch_jobs = self._fetch_jsearch_jobs(filters, rapidapi_key)
            all_jobs.extend(jsearch_jobs)

        # 5. Optional: Query Jooble India
        jooble_key = getattr(settings, "JOOBLE_API_KEY", None)
        if jooble_key:
            jooble_jobs = self._fetch_jooble_jobs(filters, jooble_key)
            all_jobs.extend(jooble_jobs)

        # Store in lookup by ID
        for job in all_jobs:
            self._job_lookup[job.id] = job

        filtered_jobs = self._apply_filters(all_jobs, filters)
        self._cache[cache_key] = all_jobs
        self._cache_timestamp[cache_key] = now

        return filtered_jobs

    def get_job_by_id(self, job_id: str) -> Optional[JobOpportunity]:
        """Fetch cached job or return None if not found."""
        return self._job_lookup.get(job_id)

    def _fetch_remoteok_jobs(self, filters: JobSearchFilters) -> List[JobOpportunity]:
        """Fetch verified listings from RemoteOK public API."""
        url = "https://remoteok.com/api"
        jobs: List[JobOpportunity] = []

        try:
            headers = {"User-Agent": "Lisa-AIOS-JobFinder/1.0 (Educational/Career Assistant)"}
            with httpx.Client(timeout=6.0) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    self._last_statuses["RemoteOK"] = "ok"
                    data = resp.json()
                    # First element in RemoteOK payload is legal disclaimer metadata
                    items = data[1:] if isinstance(data, list) and len(data) > 1 else []

                    for item in items:
                        if not isinstance(item, dict) or not item.get("id"):
                            continue

                        title = str(item.get("position", "")).strip()
                        company = str(item.get("company", "")).strip()
                        if not title or not company:
                            continue

                        # Extract tags / skills
                        raw_tags = item.get("tags", [])
                        if isinstance(raw_tags, list):
                            normalized_skills = skill_normalizer.normalize_list([str(t) for t in raw_tags])
                        else:
                            normalized_skills = []

                        # Salary detection
                        salary_min = item.get("salary_min")
                        salary_max = item.get("salary_max")
                        salary_text = None
                        try:
                            if salary_min is not None and salary_max is not None:
                                salary_text = f"${int(float(salary_min)):,} - ${int(float(salary_max)):,} USD"
                            elif salary_min is not None:
                                salary_text = f"${int(float(salary_min)):,} USD"
                            elif salary_max is not None:
                                salary_text = f"${int(float(salary_max)):,} USD"
                        except (ValueError, TypeError):
                            salary_text = None

                        # Determine employment type
                        is_internship = any(term in title.lower() for term in ["intern", "internship", "fellow", "student"])
                        emp_type = "internship" if is_internship else "full_time"

                        # Raw description
                        desc = clean_html_tags(str(item.get("description", "")))[:1200]

                        # Apply URL
                        apply_url = item.get("url") or f"https://remoteok.com/remote-jobs/{item.get('id')}"

                        job = JobOpportunity(
                            id=f"remoteok_{item.get('id')}",
                            title=title,
                            company=company,
                            location=item.get("location") or "Worldwide Remote",
                            is_remote=True,
                            remote_type="remote",
                            employment_type=emp_type,
                            experience_level="intern" if is_internship else "entry_level",
                            salary_or_stipend=salary_text,
                            salary_min=float(salary_min) if salary_min else None,
                            salary_max=float(salary_max) if salary_max else None,
                            posted_date=item.get("date"),
                            description=desc,
                            required_skills=normalized_skills[:8],
                            preferred_skills=normalized_skills[8:12],
                            apply_url=apply_url,
                            source_provider="RemoteOK",
                            company_logo=item.get("company_logo"),
                        )
                        jobs.append(job)
                elif resp.status_code == 429:
                    self._last_statuses["RemoteOK"] = "rate_limited"
                    logger.warning("[JOB-PROVIDER] RemoteOK API rate-limited (HTTP 429)")
                else:
                    self._last_statuses["RemoteOK"] = "unavailable"
                    logger.warning("[JOB-PROVIDER] RemoteOK API returned HTTP %s", resp.status_code)
        except Exception as exc:
            self._last_statuses["RemoteOK"] = "unavailable"
            logger.warning("[JOB-PROVIDER] Failed to fetch RemoteOK jobs: %s", exc)

        return jobs

    def _fetch_arbeitnow_jobs(self, filters: JobSearchFilters) -> List[JobOpportunity]:
        """Fetch verified listings from Arbeitnow public job board API."""
        url = "https://www.arbeitnow.com/api/job-board-api"
        jobs: List[JobOpportunity] = []

        try:
            with httpx.Client(timeout=6.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    self._last_statuses["Arbeitnow"] = "ok"
                    payload = resp.json()
                    items = payload.get("data", [])

                    for item in items:
                        if not isinstance(item, dict) or not item.get("slug"):
                            continue

                        title = str(item.get("title", "")).strip()
                        company = str(item.get("company_name", "")).strip()
                        if not title or not company:
                            continue

                        raw_tags = item.get("tags", [])
                        normalized_skills = skill_normalizer.normalize_list([str(t) for t in raw_tags]) if isinstance(raw_tags, list) else []

                        is_remote = bool(item.get("remote", False))
                        is_intern = any(term in title.lower() for term in ["intern", "working student", "werkstudent", "internship", "graduate", "trainee"])
                        emp_type = "internship" if is_intern else "full_time"

                        desc = clean_html_tags(str(item.get("description", "")))[:1200]
                        apply_url = item.get("url") or f"https://www.arbeitnow.com/view/{item.get('slug')}"

                        job = JobOpportunity(
                            id=f"arbeitnow_{item.get('slug')}",
                            title=title,
                            company=company,
                            location=item.get("location") or ("Remote" if is_remote else "Multiple Locations"),
                            is_remote=is_remote,
                            remote_type="remote" if is_remote else "hybrid",
                            employment_type=emp_type,
                            experience_level="intern" if is_intern else "entry_level",
                            salary_or_stipend=None,  # Arbeitnow typically does not list static salary
                            posted_date=str(item.get("created_at")),
                            description=desc,
                            required_skills=normalized_skills[:8],
                            preferred_skills=normalized_skills[8:12],
                            apply_url=apply_url,
                            source_provider="Arbeitnow",
                        )
                        jobs.append(job)
                elif resp.status_code == 429:
                    self._last_statuses["Arbeitnow"] = "rate_limited"
                    logger.warning("[JOB-PROVIDER] Arbeitnow API rate-limited (HTTP 429)")
                else:
                    self._last_statuses["Arbeitnow"] = "unavailable"
                    logger.warning("[JOB-PROVIDER] Arbeitnow API returned HTTP %s", resp.status_code)
        except Exception as exc:
            self._last_statuses["Arbeitnow"] = "unavailable"
            logger.warning("[JOB-PROVIDER] Failed to fetch Arbeitnow jobs: %s", exc)

        return jobs

    def _fetch_adzuna_jobs(
        self, filters: JobSearchFilters, app_id: str, app_key: str
    ) -> List[JobOpportunity]:
        """Fetch listings from Adzuna API if partner credentials exist."""
        loc_lower = (filters.location or "").lower().strip()
        india_cities = {
            "india", "bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "delhi", "new delhi",
            "noida", "gurgaon", "gurugram", "chennai", "kolkata", "ahmedabad", "jaipur", "chandigarh",
            "kochi", "trivandrum", "indore", "bhopal", "mysore", "coimbatore"
        }
        country = "in" if any(c in loc_lower for c in india_cities) else "us"
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        jobs: List[JobOpportunity] = []

        raw_role = filters.role or "Software Engineer"
        role_what = [r.strip() for r in re.split(r"[,;/|]|\bor\b", raw_role) if r.strip()][0] if ("," in raw_role or " or " in raw_role) else raw_role

        params: Dict[str, Any] = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 20,
            "what": role_what,
        }
        if filters.location and filters.location.lower() not in ["any", "all"]:
            loc_parts = [p.strip() for p in re.split(r"[,;/|]|\bor\b", filters.location) if p.strip()]
            # Pick first specific city (e.g. Bangalore) or fallback to first element
            specific_city = next((p for p in loc_parts if p.lower() not in ["india", "in", "any", "all"]), None)
            params["where"] = specific_city or loc_parts[0]

        try:
            with httpx.Client(timeout=6.0) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 200:
                    self._last_statuses["Adzuna"] = "ok"
                    data = resp.json()
                    for item in data.get("results", []):
                        title = item.get("title", "")
                        company = item.get("company", {}).get("display_name", "")
                        if not title or not company:
                            continue

                        salary_min = item.get("salary_min")
                        salary_max = item.get("salary_max")
                        salary_text = None
                        try:
                            curr_sym = "₹" if country == "in" else "$"
                            if salary_min is not None and salary_max is not None:
                                salary_text = f"{curr_sym}{int(float(salary_min)):,} - {curr_sym}{int(float(salary_max)):,}"
                            elif salary_min is not None:
                                salary_text = f"{curr_sym}{int(float(salary_min)):,}"
                            elif salary_max is not None:
                                salary_text = f"{curr_sym}{int(float(salary_max)):,}"
                        except (ValueError, TypeError):
                            salary_text = None

                        is_intern = any(t in title.lower() for t in ["intern", "internship", "graduate"])

                        job = JobOpportunity(
                            id=f"adzuna_{item.get('id')}",
                            title=title,
                            company=company,
                            location=item.get("location", {}).get("display_name", "India" if country == "in" else "Unknown"),
                            is_remote=False,
                            remote_type="on_site",
                            employment_type="internship" if is_intern else "full_time",
                            experience_level="intern" if is_intern else "entry_level",
                            salary_or_stipend=salary_text,
                            posted_date=item.get("created"),
                            description=clean_html_tags(item.get("description", ""))[:1200],
                            required_skills=[],
                            preferred_skills=[],
                            apply_url=item.get("redirect_url") or "",
                            source_provider="Adzuna India" if country == "in" else "Adzuna",
                        )
                        jobs.append(job)
                elif resp.status_code == 429:
                    self._last_statuses["Adzuna"] = "rate_limited"
                    logger.warning("[JOB-PROVIDER] Adzuna API rate-limited (HTTP 429)")
                else:
                    self._last_statuses["Adzuna"] = "unavailable"
                    logger.warning("[JOB-PROVIDER] Adzuna API returned HTTP %s", resp.status_code)
        except Exception as exc:
            self._last_statuses["Adzuna"] = "unavailable"
            logger.warning("[JOB-PROVIDER] Failed to fetch Adzuna jobs: %s", exc)

        return jobs

    def _fetch_jsearch_jobs(self, filters: JobSearchFilters, rapidapi_key: str) -> List[JobOpportunity]:
        """Fetch live Google Jobs for India & Global via JSearch RapidAPI."""
        url = "https://jsearch.p.rapidapi.com/search"
        jobs: List[JobOpportunity] = []
        loc_str = filters.location or "India"
        role_str = filters.role or "Software Engineer"
        primary_role = [r.strip() for r in re.split(r"[,;/|]|\bor\b", role_str) if r.strip()][0] if ("," in role_str or " or " in role_str) else role_str
        query = f"{primary_role} in {loc_str}"
        if filters.employment_type == "internship":
            query = f"{primary_role} internship in {loc_str}"

        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com",
            "User-Agent": "Lisa-AIOS-JobFinder/1.0",
        }
        params = {
            "query": query,
            "page": "1",
            "num_pages": "1",
        }
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url, headers=headers, params=params)
                if resp.status_code == 200:
                    self._last_statuses["JSearch"] = "ok"
                    data = resp.json()
                    for item in data.get("data", []):
                        title = item.get("job_title", "")
                        company = item.get("employer_name", "")
                        if not title or not company:
                            continue
                        apply_link = item.get("job_apply_link") or item.get("job_google_link") or ""
                        is_remote = bool(item.get("job_is_remote"))
                        is_intern = item.get("job_employment_type") == "INTERN" or "intern" in title.lower()

                        salary_text = None
                        min_sal = item.get("job_min_salary")
                        max_sal = item.get("job_max_salary")
                        currency = item.get("job_salary_currency") or "INR"
                        if min_sal and max_sal:
                            salary_text = f"{currency} {min_sal:,.0f} - {max_sal:,.0f}"
                        elif min_sal:
                            salary_text = f"{currency} {min_sal:,.0f}+"

                        city = item.get("job_city") or ""
                        state = item.get("job_state") or ""
                        country = item.get("job_country") or ""
                        loc_display = ", ".join(p for p in [city, state, country] if p) or "India"

                        job = JobOpportunity(
                            id=f"jsearch_{item.get('job_id')}",
                            title=title,
                            company=company,
                            location=loc_display,
                            is_remote=is_remote,
                            remote_type="remote" if is_remote else "on_site",
                            employment_type="internship" if is_intern else "full_time",
                            experience_level="intern" if is_intern else "entry_level",
                            salary_or_stipend=salary_text,
                            posted_date=item.get("job_posted_at_datetime_utc"),
                            description=clean_html_tags(item.get("job_description", ""))[:1200],
                            required_skills=item.get("job_required_skills") or [],
                            preferred_skills=[],
                            apply_url=apply_link,
                            source_provider="Google Jobs (India)",
                            company_logo=item.get("employer_logo"),
                        )
                        jobs.append(job)
                elif resp.status_code == 429:
                    self._last_statuses["JSearch"] = "rate_limited"
                else:
                    self._last_statuses["JSearch"] = "unavailable"
        except Exception as exc:
            self._last_statuses["JSearch"] = "unavailable"
            logger.warning("[JOB-PROVIDER] Failed to fetch JSearch jobs: %s", exc)
        return jobs

    def _fetch_jooble_jobs(self, filters: JobSearchFilters, jooble_key: str) -> List[JobOpportunity]:
        """Fetch live listings from Jooble India."""
        url = f"https://jooble.org/api/{jooble_key}"
        jobs: List[JobOpportunity] = []
        loc_str = filters.location or "India"
        role_str = filters.role or "Software Developer"
        payload = {
            "keywords": role_str,
            "location": loc_str,
            "page": 1,
        }
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    self._last_statuses["Jooble"] = "ok"
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = item.get("title", "")
                        company = item.get("company", "")
                        if not title or not company:
                            continue
                        job = JobOpportunity(
                            id=f"jooble_{item.get('id')}",
                            title=clean_html_tags(title),
                            company=clean_html_tags(company),
                            location=item.get("location") or "India",
                            is_remote="remote" in (item.get("location") or "").lower(),
                            remote_type="remote" if "remote" in (item.get("location") or "").lower() else "on_site",
                            employment_type="internship" if "intern" in title.lower() else "full_time",
                            salary_or_stipend=item.get("salary") or None,
                            posted_date=item.get("updated"),
                            description=clean_html_tags(item.get("snippet", ""))[:1000],
                            apply_url=item.get("link") or "",
                            source_provider="Jooble India",
                        )
                        jobs.append(job)
                elif resp.status_code == 429:
                    self._last_statuses["Jooble"] = "rate_limited"
                else:
                    self._last_statuses["Jooble"] = "unavailable"
        except Exception as exc:
            self._last_statuses["Jooble"] = "unavailable"
            logger.warning("[JOB-PROVIDER] Failed to fetch Jooble jobs: %s", exc)
        return jobs

    def _apply_filters(self, jobs: List[JobOpportunity], filters: JobSearchFilters) -> List[JobOpportunity]:
        """Filter jobs based on user criteria with city alias normalization."""
        filtered = jobs

        # Role filter (supports comma/or separated roles)
        if filters.role:
            raw_role = filters.role.lower().strip()
            role_phrases = [p.strip() for p in re.split(r"[,;/|]|\bor\b", raw_role) if p.strip()]
            filtered = [
                j for j in filtered
                if any(
                    any(term in j.title.lower() or term in j.description.lower() for term in phrase.split())
                    or phrase in j.title.lower()
                    for phrase in role_phrases
                )
            ]

        # Location filter with multi-location parsing and city alias normalization
        if filters.location:
            raw_loc = filters.location.lower().strip()
            if raw_loc not in ["any", "all"]:
                individual_locs = [p.strip() for p in re.split(r"[,;/|]|\bor\b", raw_loc) if p.strip()]
                all_aliases: List[str] = []
                for loc in individual_locs:
                    all_aliases.append(loc)
                    if loc in ["bangalore", "bengaluru"]:
                        all_aliases.extend(["bangalore", "bengaluru", "blr"])
                    elif loc in ["chennai", "madras"]:
                        all_aliases.extend(["chennai", "madras", "maa"])
                    elif loc in ["mumbai", "bombay"]:
                        all_aliases.extend(["mumbai", "bombay", "bom"])
                    elif loc in ["delhi", "new delhi", "ncr", "gurgaon", "gurugram", "noida"]:
                        all_aliases.extend(["delhi", "new delhi", "ncr", "gurgaon", "gurugram", "noida"])
                    elif loc in ["kolkata", "calcutta"]:
                        all_aliases.extend(["kolkata", "calcutta"])
                    elif loc in ["hyderabad", "hyd"]:
                        all_aliases.extend(["hyderabad", "hyd", "cyberabad"])
                    elif loc in ["pune"]:
                        all_aliases.extend(["pune", "pnq"])
                    elif loc in ["india", "in"]:
                        all_aliases.extend([
                            "india", "in", "bangalore", "bengaluru", "blr", "chennai", "madras", "maa",
                            "mumbai", "delhi", "new delhi", "ncr", "gurgaon", "gurugram", "noida",
                            "hyderabad", "hyd", "pune", "pnq", "kolkata", "ahmedabad", "kochi"
                        ])

                filtered = [
                    j for j in filtered
                    if any(a in j.location.lower() for a in all_aliases)
                    or (j.is_remote and any("remote" in a for a in all_aliases))
                ]

        # Remote toggle
        if filters.is_remote is not None:
            filtered = [j for j in filtered if j.is_remote == filters.is_remote]

        # Employment type
        if filters.employment_type and filters.employment_type.lower() != "any":
            target_type = filters.employment_type.lower()
            filtered = [j for j in filtered if j.employment_type.lower() == target_type]

        # Company filter
        if filters.company:
            comp_term = filters.company.lower().strip()
            filtered = [j for j in filtered if comp_term in j.company.lower()]

        # Skills overlap filter (if candidate requested specific skills)
        if filters.skills:
            req_set = {s.lower() for s in filters.skills}
            filtered = [
                j for j in filtered
                if not j.required_skills or any(s.lower() in req_set for s in j.required_skills)
            ]

        # Sorting
        if filters.sort_by == "newest":
            filtered.sort(key=lambda j: j.posted_date or "", reverse=True)
        elif filters.sort_by == "salary":
            filtered.sort(key=lambda j: j.salary_min or 0.0, reverse=True)

        return filtered[: filters.limit]


job_provider = AggregatorJobProvider()
