"""
Jarvis AIOS — Skill Matching & Gap Analysis Models
---------------------------------------------------
Data models for transparent, non-arbitrary skill matching, gap identification,
and resume-to-job deep analysis.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SkillMatchResult(BaseModel):
    job_id: str
    matched_required_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    matched_preferred_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    match_score: float = 0.0  # Documented, deterministic calculation
    match_reasons: List[str] = Field(default_factory=list)
    potential_gaps: List[str] = Field(default_factory=list)
    score_breakdown: Dict[str, Any] = Field(default_factory=dict)


class SkillGapAnalysis(BaseModel):
    job_id: str
    job_title: str
    company: str
    user_skills: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    relevant_projects: List[str] = Field(default_factory=list)
    recommended_preparation: List[str] = Field(default_factory=list)


class ResumeJobAnalysisRequest(BaseModel):
    job_id: str
    custom_resume_text: Optional[str] = None


class ResumeJobAnalysisResponse(BaseModel):
    job_id: str
    job_title: str
    company: str
    strengths: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    relevant_projects: List[str] = Field(default_factory=list)
    resume_keywords_to_consider: List[str] = Field(default_factory=list)
    potential_weaknesses: List[str] = Field(default_factory=list)
    interview_preparation_topics: List[str] = Field(default_factory=list)
    transparent_assessment: str = ""
