"""
Jarvis AIOS — Jobs Domain Models
"""

from app.Jobs.models.candidate_profile import (
    CandidateProfile,
    EducationItem,
    ProjectItem,
    ExperienceItem,
    SkillCategory,
)
from app.Jobs.models.job_opportunity import (
    JobOpportunity,
    JobSearchFilters,
    JobSearchResponse,
)
from app.Jobs.models.skill_matching import (
    SkillMatchResult,
    SkillGapAnalysis,
    ResumeJobAnalysisRequest,
    ResumeJobAnalysisResponse,
)
from app.Jobs.models.application_tracker import (
    ApplicationStatusEnum,
    ApplicationTrackItem,
    UpdateApplicationStatusRequest,
)

__all__ = [
    "CandidateProfile",
    "EducationItem",
    "ProjectItem",
    "ExperienceItem",
    "SkillCategory",
    "JobOpportunity",
    "JobSearchFilters",
    "JobSearchResponse",
    "SkillMatchResult",
    "SkillGapAnalysis",
    "ResumeJobAnalysisRequest",
    "ResumeJobAnalysisResponse",
    "ApplicationStatusEnum",
    "ApplicationTrackItem",
    "UpdateApplicationStatusRequest",
]
