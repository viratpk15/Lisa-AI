"""
Jarvis AIOS — FastAPI Jobs & Internship Routes
-----------------------------------------------
Endpoints for resume parsing, candidate profile management, live job search,
skill gap analysis, resume-to-job deep evaluation, and application lifecycle tracking.
"""

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.Auth.dependencies import get_current_user
from app.Auth.models import User
from app.Jobs.models.candidate_profile import CandidateProfile
from app.Jobs.models.job_opportunity import (
    JobOpportunity,
    JobSearchFilters,
    JobSearchResponse,
)
from app.Jobs.models.skill_matching import (
    ResumeJobAnalysisRequest,
    ResumeJobAnalysisResponse,
    SkillGapAnalysis,
    SkillMatchResult,
)
from app.Jobs.models.application_tracker import (
    ApplicationStatusEnum,
    ApplicationTrackItem,
    UpdateApplicationStatusRequest,
)
from app.Jobs.services.resume_parser import resume_parser
from app.Jobs.services.jobs_service import jobs_service
from app.Jobs.services.tracker_service import tracker_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _extract_user_info(current_user: Any) -> tuple[str, str | None]:
    """Safely extract user ID and email whether current_user is a User instance or dict fixture."""
    if isinstance(current_user, dict):
        uid = str(current_user.get("id") or current_user.get("user_id") or "1")
        email = current_user.get("email") or current_user.get("sub")
        return uid, email
    uid = str(getattr(current_user, "id", "1"))
    email = getattr(current_user, "email", None)
    return uid, email


class JobSearchWithMatchesResponse(BaseModel):
    search_response: JobSearchResponse
    matches: Dict[str, SkillMatchResult]


class TrackJobRequest(BaseModel):
    job_id: str
    status: ApplicationStatusEnum = ApplicationStatusEnum.SAVED


@router.post(
    "/profile/extract-resume",
    response_model=CandidateProfile,
    summary="Extract Profile from Resume File",
    description="Parses PDF, DOCX, or TXT resume to extract education, skills, projects, and experiences.",
)
async def extract_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> CandidateProfile:
    try:
        content = await file.read()
        filename = file.filename or "resume.pdf"
        profile = resume_parser.parse_resume(content, filename)
        _, email = _extract_user_info(current_user)
        # Associate user email if not in resume
        if not profile.email and email:
            profile.email = email
        return profile
    except Exception as exc:
        logger.error("[JOBS-ROUTE] Failed to extract resume: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "resume_extraction_error", "message": str(exc)}},
        )


@router.get(
    "/profile",
    response_model=CandidateProfile,
    summary="Get User Candidate Profile",
)
def get_profile(
    current_user: User = Depends(get_current_user),
) -> CandidateProfile:
    uid, email = _extract_user_info(current_user)
    profile = jobs_service.get_candidate_profile(uid)
    if not profile:
        # Return initialized empty profile
        return CandidateProfile(
            name=email.split("@")[0].title() if email else "Candidate",
            email=email,
        )
    return profile


@router.post(
    "/profile",
    response_model=CandidateProfile,
    summary="Save/Update Candidate Profile",
)
def save_profile(
    profile: CandidateProfile,
    current_user: User = Depends(get_current_user),
) -> CandidateProfile:
    uid, _ = _extract_user_info(current_user)
    try:
        return jobs_service.save_candidate_profile(uid, profile)
    except Exception as exc:
        logger.error("[JOBS-ROUTE] Failed to save candidate profile: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "profile_save_error", "message": str(exc)}},
        )


@router.post(
    "/search",
    response_model=JobSearchWithMatchesResponse,
    summary="Search Real Opportunities with Match Scoring",
)
def search_jobs(
    filters: JobSearchFilters,
    current_user: User = Depends(get_current_user),
) -> JobSearchWithMatchesResponse:
    uid, _ = _extract_user_info(current_user)
    try:
        search_resp, matches = jobs_service.search_jobs(filters, uid)
        return JobSearchWithMatchesResponse(search_response=search_resp, matches=matches)
    except Exception as exc:
        logger.error("[JOBS-ROUTE] Job search failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "job_search_error", "message": str(exc)}},
        )


@router.get(
    "/{job_id}",
    response_model=JobOpportunity,
    summary="Get Job Opportunity Details",
)
def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> JobOpportunity:
    job = jobs_service.get_job_details(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "job_not_found", "message": f"Job '{job_id}' not found."}},
        )
    return job


@router.get(
    "/{job_id}/skill-gap",
    response_model=SkillGapAnalysis,
    summary="Analyze Skill Gaps for a Job",
)
def get_skill_gap(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> SkillGapAnalysis:
    uid, _ = _extract_user_info(current_user)
    gap = jobs_service.analyze_skill_gap(job_id, uid)
    if not gap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "gap_analysis_failed", "message": "Could not compute skill gap. Ensure your candidate profile is created."}},
        )
    return gap


@router.post(
    "/analyze-resume-job",
    response_model=ResumeJobAnalysisResponse,
    summary="Deep Resume-to-Job Analysis",
)
def analyze_resume_job(
    req: ResumeJobAnalysisRequest,
    current_user: User = Depends(get_current_user),
) -> ResumeJobAnalysisResponse:
    uid, _ = _extract_user_info(current_user)
    analysis = jobs_service.analyze_resume_job(
        req.job_id, uid, req.custom_resume_text
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "analysis_failed", "message": f"Opportunity '{req.job_id}' not found."}},
        )
    return analysis


@router.get(
    "/applications/all",
    response_model=List[ApplicationTrackItem],
    summary="Get Tracked Applications",
)
def get_applications(
    current_user: User = Depends(get_current_user),
) -> List[ApplicationTrackItem]:
    uid, _ = _extract_user_info(current_user)
    return tracker_service.get_user_applications(uid)


@router.post(
    "/applications",
    response_model=ApplicationTrackItem,
    summary="Track a Job Opportunity",
)
def track_job(
    req: TrackJobRequest,
    current_user: User = Depends(get_current_user),
) -> ApplicationTrackItem:
    uid, _ = _extract_user_info(current_user)
    job = jobs_service.get_job_details(req.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "job_not_found", "message": f"Opportunity '{req.job_id}' not found to track."}},
        )
    return tracker_service.track_job(uid, job, req.status)


@router.patch(
    "/applications/{job_id}/status",
    response_model=ApplicationTrackItem,
    summary="Update Application Status",
)
def update_application_status(
    job_id: str,
    req: UpdateApplicationStatusRequest,
    current_user: User = Depends(get_current_user),
) -> ApplicationTrackItem:
    uid, _ = _extract_user_info(current_user)
    updated = tracker_service.update_application_status(uid, job_id, req)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "track_not_found", "message": f"Tracked application '{job_id}' not found."}},
        )
    return updated


@router.delete(
    "/applications/{job_id}",
    summary="Untrack Application",
)
def delete_application(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, bool]:
    uid, _ = _extract_user_info(current_user)
    success = tracker_service.remove_job(uid, job_id)
    return {"deleted": success}
