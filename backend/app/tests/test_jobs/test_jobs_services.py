"""
Tests for Jobs Services (Resume Parser, Matcher, Gap Analyzer, Tracker)
"""

from app.Jobs.models.candidate_profile import (
    CandidateProfile,
    ProjectItem,
)
from app.Jobs.models.job_opportunity import JobOpportunity
from app.Jobs.models.application_tracker import (
    ApplicationStatusEnum,
    UpdateApplicationStatusRequest,
)
from app.Jobs.services.resume_parser import resume_parser
from app.Jobs.services.matching_service import matching_service
from app.Jobs.services.resume_analyzer import resume_analyzer
from app.Jobs.services.tracker_service import tracker_service


SAMPLE_RESUME_TEXT = """
Aarav Sharma
Email: aarav@example.com
Phone: +91 98765 43210

EDUCATION
B.Tech in Computer Science and Engineering
RV College of Engineering, Bangalore
Graduation Year: 2025 | CGPA: 8.8

SKILLS
Programming: Python, JavaScript, TypeScript, SQL
AI/ML: Machine Learning, PyTorch, Scikit-Learn, NLP
Web Frameworks: FastAPI, React, Next.js, Node.js
Cloud & Databases: PostgreSQL, MongoDB, Docker, AWS

PROJECTS
Autonomous Code Assistant
Built a multi-agent developer assistant with LangGraph and FastAPI.

Vector Search Engine
Implemented semantic search with PyTorch and ChromaDB.
"""


def test_resume_parser_heuristic_extraction():
    file_bytes = SAMPLE_RESUME_TEXT.encode("utf-8")
    profile = resume_parser.parse_resume(file_bytes, "aarav_resume.txt")

    assert profile.name == "Aarav Sharma"
    assert profile.email == "aarav@example.com"
    assert len(profile.education) > 0
    assert profile.education[0].graduation_year == 2025
    assert profile.education[0].cgpa == 8.8
    assert "Python" in profile.all_normalized_skills
    assert "React" in profile.all_normalized_skills
    assert "Machine Learning" in profile.all_normalized_skills
    assert profile.extracted_from_resume is True
    assert profile.is_confirmed_by_user is False


def test_matching_service_transparent_score():
    profile = CandidateProfile(
        name="Aarav Sharma",
        all_normalized_skills=["Python", "FastAPI", "React", "Docker", "Machine Learning"],
        experience_level="entry_level",
        preferred_locations=["Bangalore"],
        remote_preference="any",
    )

    job = JobOpportunity(
        id="job_test_1",
        title="AI Engineer",
        company="TechCorp",
        location="Worldwide Remote",
        is_remote=True,
        employment_type="full_time",
        experience_level="entry_level",
        required_skills=["Python", "FastAPI", "Kubernetes"],
        preferred_skills=["Docker", "AWS"],
        apply_url="https://example.com/apply",
        source_provider="Test",
    )

    result = matching_service.compute_match(profile, job)

    assert result.job_id == "job_test_1"
    # 2 out of 3 required matched (Python, FastAPI) -> 2/3 * 60 = 40.0 pts
    # 1 out of 2 preferred matched (Docker)
    # Entry level match -> 20 pts
    # Remote match -> 20 pts
    # Total score should be approx 80.0
    assert 70.0 <= result.match_score <= 85.0
    assert "Python" in result.matched_required_skills
    assert "FastAPI" in result.matched_required_skills
    assert "Kubernetes" in result.missing_required_skills
    assert "score_breakdown" in result.model_dump()
    assert len(result.match_reasons) > 0
    assert any("Kubernetes" in gap for gap in result.potential_gaps)


def test_analyze_skill_gaps():
    profile = CandidateProfile(
        name="Aarav Sharma",
        all_normalized_skills=["Python", "FastAPI"],
        projects=[ProjectItem(title="API Backend", description="FastAPI service", tech_stack=["Python"])],
    )
    job = JobOpportunity(
        id="job_test_2",
        title="Backend Engineer",
        company="Fintech Inc",
        location="Bangalore",
        is_remote=False,
        employment_type="full_time",
        required_skills=["Python", "PostgreSQL", "Kafka"],
        apply_url="https://example.com/apply",
        source_provider="Test",
    )

    gaps = matching_service.analyze_skill_gaps(profile, job)
    assert gaps.job_id == "job_test_2"
    assert "Python" in gaps.matched_skills
    assert "PostgreSQL" in gaps.missing_skills
    assert "Kafka" in gaps.missing_skills
    assert len(gaps.recommended_preparation) > 0


def test_resume_analyzer():
    profile = CandidateProfile(
        name="Aarav Sharma",
        all_normalized_skills=["Python", "FastAPI", "Docker"],
        projects=[ProjectItem(title="Chat API", description="LangGraph pipeline", tech_stack=["Python"])],
    )
    job = JobOpportunity(
        id="job_test_3",
        title="Python Developer",
        company="Startup Labs",
        location="Remote",
        is_remote=True,
        required_skills=["Python", "FastAPI", "Kubernetes"],
        apply_url="https://example.com/apply",
    )

    analysis = resume_analyzer.analyze(profile, job)
    assert analysis.job_id == "job_test_3"
    assert len(analysis.strengths) > 0
    assert len(analysis.missing_requirements) > 0
    assert len(analysis.interview_preparation_topics) > 0
    assert analysis.transparent_assessment != ""


def test_application_tracker_service():
    user_id = "user_42"
    job = JobOpportunity(
        id="track_1",
        title="ML Engineer Intern",
        company="DeepMind Labs",
        location="Bangalore",
        apply_url="https://deepmind.com/careers",
    )

    # Track as saved
    item = tracker_service.track_job(user_id, job, ApplicationStatusEnum.SAVED)
    assert item.status == ApplicationStatusEnum.SAVED

    # Retrieve all
    apps = tracker_service.get_user_applications(user_id)
    assert len(apps) == 1
    assert apps[0].job_id == "track_1"

    # Update to applied with interview date
    updated = tracker_service.update_application_status(
        user_id,
        "track_1",
        UpdateApplicationStatusRequest(
            status=ApplicationStatusEnum.INTERVIEW,
            notes="Technical round scheduled",
            interview_date="2026-10-10",
        ),
    )
    assert updated is not None
    assert updated.status == ApplicationStatusEnum.INTERVIEW
    assert updated.notes == "Technical round scheduled"

    # Remove
    deleted = tracker_service.remove_job(user_id, "track_1")
    assert deleted is True
    assert len(tracker_service.get_user_applications(user_id)) == 0
