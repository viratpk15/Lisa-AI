"""
Jarvis AIOS — Job Opportunity & Search Models
----------------------------------------------
Pydantic schemas for live job opportunities, search queries, and filter parameters.
Strict zero-fabrication: fields reflect real provider data or explicit empty states.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class JobOpportunity(BaseModel):
    id: str
    title: str
    company: str
    location: str
    is_remote: bool = False
    remote_type: str = "on_site"  # remote, hybrid, on_site
    employment_type: str = "full_time"  # internship, full_time, part_time, graduate
    experience_level: str = "entry_level"  # intern, entry_level, junior, mid, senior
    salary_or_stipend: Optional[str] = None  # None if provider did not supply salary
    salary_currency: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    posted_date: Optional[str] = None
    deadline: Optional[str] = None
    description: str = ""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    apply_url: str  # Direct authentic provider / company link
    source_provider: str = "aggregator"
    company_logo: Optional[str] = None


class JobSearchFilters(BaseModel):
    role: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    employment_type: Optional[str] = None  # internship, full_time, any
    experience_level: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    company: Optional[str] = None
    sort_by: str = "relevance"  # relevance, newest, salary
    limit: int = 25


class JobSearchResponse(BaseModel):
    query: str
    total_results: int
    jobs: List[JobOpportunity] = Field(default_factory=list)
    provider_used: str
    has_live_results: bool
    status_message: Optional[str] = None
    disclaimer: str = "Results fetched directly from verified provider job listings."
