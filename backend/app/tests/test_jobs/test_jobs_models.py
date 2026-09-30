"""
Tests for Jobs Domain Models and Validations
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
)
from app.Jobs.models.application_tracker import (
    ApplicationStatusEnum,
    ApplicationTrackItem,
)
from app.Jobs.models.skill_matching import SkillMatchResult


def test_candidate_profile_creation():
    edu = EducationItem(
        college="RV College of Engineering",
        degree="B.Tech",
        branch="Computer Science",
        graduation_year=2025,
        cgpa=8.9,
    )
    proj = ProjectItem(
        title="Lisa AI Operating System",
        description="Autonomous LangGraph assistant",
        tech_stack=["Python", "FastAPI", "React"],
    )
    exp = ExperienceItem(
        company="AI Research Labs",
        role="ML Engineering Intern",
        duration="3 months",
        is_internship=True,
    )
    skills = SkillCategory(
        programming_languages=["Python", "TypeScript"],
        ai_ml_skills=["Machine Learning", "PyTorch"],
    )

    profile = CandidateProfile(
        name="Aarav Sharma",
        email="aarav@example.com",
        education=[edu],
        skills=skills,
        all_normalized_skills=["Python", "TypeScript", "Machine Learning", "PyTorch"],
        projects=[proj],
        experiences=[exp],
        preferred_roles=["AI Engineer", "Software Engineer"],
        preferred_locations=["Bangalore", "Remote"],
        remote_preference="any",
    )

    assert profile.name == "Aarav Sharma"
    assert len(profile.education) == 1
    assert profile.education[0].cgpa == 8.9
    assert len(profile.projects) == 1
    assert profile.experiences[0].is_internship is True
    assert "Python" in profile.all_normalized_skills


def test_job_opportunity_model():
    job = JobOpportunity(
        id="remoteok_12345",
        title="Junior AI Engineer",
        company="Anthropic Labs",
        location="Worldwide Remote",
        is_remote=True,
        remote_type="remote",
        employment_type="full_time",
        experience_level="entry_level",
        salary_or_stipend="$90,000 - $120,000 USD",
        required_skills=["Python", "PyTorch", "FastAPI"],
        preferred_skills=["Docker", "Kubernetes"],
        apply_url="https://remoteok.com/job/12345",
        source_provider="RemoteOK",
    )

    assert job.id == "remoteok_12345"
    assert job.is_remote is True
    assert len(job.required_skills) == 3
    assert job.apply_url.startswith("https://")


def test_application_tracker_item():
    item = ApplicationTrackItem(
        job_id="job_999",
        title="Full Stack Intern",
        company="Acme Corp",
        location="Bangalore",
        apply_url="https://example.com/apply",
        status=ApplicationStatusEnum.SAVED,
        saved_at="2026-10-01 10:00 UTC",
    )
    assert item.status == ApplicationStatusEnum.SAVED
    assert item.is_user_confirmed is True


def test_skill_match_result_model():
    res = SkillMatchResult(
        job_id="job_1",
        matched_required_skills=["Python", "FastAPI"],
        missing_required_skills=["Kubernetes"],
        match_score=75.0,
        match_reasons=["✓ Matched 2 required skills"],
        potential_gaps=["△ Required skill gap: Kubernetes"],
        score_breakdown={"skill_overlap": 40.0},
    )
    assert res.match_score == 75.0
    assert len(res.matched_required_skills) == 2
    assert len(res.missing_required_skills) == 1
