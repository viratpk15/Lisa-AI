"""
Jarvis AIOS — Candidate Profile Models
---------------------------------------
Pydantic models representing the candidate's academic background, skills,
projects, work experiences, certifications, and job search preferences.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    college: str
    degree: str
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    current_semester: Optional[str] = None


class ProjectItem(BaseModel):
    title: str
    description: str
    tech_stack: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None


class ExperienceItem(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    description: Optional[str] = None
    is_internship: bool = False
    skills_used: List[str] = Field(default_factory=list)


class SkillCategory(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    ai_ml_skills: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_devops: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[EducationItem] = Field(default_factory=list)
    skills: SkillCategory = Field(default_factory=SkillCategory)
    all_normalized_skills: List[str] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    experiences: List[ExperienceItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)

    # Career Preferences
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_preference: str = "any"  # any, remote_only, hybrid, on_site
    expected_salary_or_stipend: Optional[str] = None
    availability: Optional[str] = "immediate"  # immediate, 1_month, etc.
    experience_level: str = "entry_level"  # student, entry_level, junior, mid, senior

    # Metadata
    raw_resume_text: Optional[str] = None
    extracted_from_resume: bool = False
    is_confirmed_by_user: bool = False
