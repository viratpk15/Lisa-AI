"""
Jarvis AIOS — Jobs & Internships Orchestration Service
-------------------------------------------------------
Coordinates candidate profiles, live job searches, transparent matching evaluations,
skill gap analyses, and application lifecycle tracking.
"""

import logging
from typing import Dict, Optional, Tuple

from app.Jobs.models.candidate_profile import CandidateProfile
from app.Jobs.models.job_opportunity import (
    JobOpportunity,
    JobSearchFilters,
    JobSearchResponse,
)
from app.Jobs.models.skill_matching import (
    ResumeJobAnalysisResponse,
    SkillGapAnalysis,
    SkillMatchResult,
)
from app.Jobs.providers.base import BaseJobProvider
from app.Jobs.services.matching_service import matching_service
from app.Jobs.services.resume_analyzer import resume_analyzer
from app.Jobs.services.skill_normalizer import skill_normalizer

logger = logging.getLogger(__name__)


class JobsService:
    """Master domain service orchestrating the Jobs & Internship capability."""

    def __init__(self, provider: Optional[BaseJobProvider] = None) -> None:
        self._provider = provider
        # User ID -> CandidateProfile
        self._user_profiles: Dict[str, CandidateProfile] = {}

    @property
    def provider(self) -> BaseJobProvider:
        if self._provider is None:
            from app.Jobs.providers.aggregator_provider import job_provider
            self._provider = job_provider
        return self._provider

    def get_candidate_profile(self, user_id: str) -> Optional[CandidateProfile]:
        """Retrieve candidate profile for a user."""
        return self._user_profiles.get(user_id)

    def save_candidate_profile(self, user_id: str, profile: CandidateProfile) -> CandidateProfile:
        """Save or update candidate profile for a user."""
        # Normalize all skills before saving
        profile.all_normalized_skills = skill_normalizer.normalize_list(profile.all_normalized_skills)
        profile.skills = skill_normalizer.categorize_skills(profile.all_normalized_skills)
        self._user_profiles[user_id] = profile
        logger.info("[JOBS-SERVICE] Saved candidate profile for user %s (%d skills)", user_id, len(profile.all_normalized_skills))
        return profile

    def search_jobs(
        self, filters: JobSearchFilters, user_id: Optional[str] = None
    ) -> Tuple[JobSearchResponse, Dict[str, SkillMatchResult]]:
        """
        Search live opportunities and evaluate compatibility against user's candidate profile.
        Returns JobSearchResponse and mapping of job_id -> SkillMatchResult.
        """
        profile = self.get_candidate_profile(user_id) if user_id else None

        jobs = self.provider.search_jobs(filters)

        match_results: Dict[str, SkillMatchResult] = {}
        if profile and jobs:
            for job in jobs:
                match_results[job.id] = matching_service.compute_match(profile, job)

            # If user sorts by relevance, sort by match_score descending
            if filters.sort_by == "relevance":
                jobs.sort(key=lambda j: match_results[j.id].match_score, reverse=True)

        status_summary = self.provider.get_status_summary(len(jobs))

        resp = JobSearchResponse(
            query=filters.role or "Software & AI Engineering Opportunities",
            total_results=len(jobs),
            jobs=jobs,
            provider_used="RemoteOK & Arbeitnow Live Aggregator",
            has_live_results=len(jobs) > 0,
            status_message=status_summary,
            disclaimer="Results sourced from verified live tech job feeds. Opportunities link to official applications.",
        )

        return resp, match_results

    def get_job_details(self, job_id: str) -> Optional[JobOpportunity]:
        """Retrieve full details of a specific opportunity."""
        return self.provider.get_job_by_id(job_id)

    def analyze_skill_gap(
        self, job_id: str, user_id: str
    ) -> Optional[SkillGapAnalysis]:
        """Generate detailed skill gap analysis between user profile and target job."""
        job = self.get_job_details(job_id)
        profile = self.get_candidate_profile(user_id)
        if not job or not profile:
            return None

        return matching_service.analyze_skill_gaps(profile, job)

    def analyze_resume_job(
        self, job_id: str, user_id: str, custom_resume_text: Optional[str] = None
    ) -> Optional[ResumeJobAnalysisResponse]:
        """Perform comprehensive resume-to-job deep evaluation."""
        job = self.get_job_details(job_id)
        if not job:
            return None

        profile = self.get_candidate_profile(user_id)
        if not profile:
            # Create a minimal profile with custom resume text if provided
            profile = CandidateProfile(
                name="Candidate",
                raw_resume_text=custom_resume_text or "",
                all_normalized_skills=skill_normalizer.normalize_list([]),
            )

        if custom_resume_text:
            profile.raw_resume_text = custom_resume_text

        return resume_analyzer.analyze(profile, job)


jobs_service = JobsService()
