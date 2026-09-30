"""
Jarvis AIOS — Resume-to-Job Deep Analysis Service
--------------------------------------------------
Compares a candidate's resume/profile against a specific job opportunity.
Returns strengths, missing requirements, resume keywords, potential weaknesses,
and targeted interview preparation topics.
Strict Zero-Fabrication: Does not fabricate experience or rewrite false claims.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from app.Jobs.models.candidate_profile import CandidateProfile
from app.Jobs.models.job_opportunity import JobOpportunity
from app.Jobs.models.skill_matching import ResumeJobAnalysisResponse
from app.Jobs.services.matching_service import matching_service
from app.LLM.client import LLMClient

logger = logging.getLogger(__name__)

ANALYSIS_SYSTEM_PROMPT = """You are an objective, honest technical recruiter and career evaluator for Lisa AIOS.
Evaluate the candidate's profile against the target job opportunity.

CRITICAL RULES:
- Never fabricate experience or claim the candidate did something they did not do.
- Be constructive and rigorous: identify genuine strengths, real skill gaps, and actionable interview topics.
- Return ONLY valid JSON matching this schema:

{
  "strengths": ["List of 3-5 verified strengths"],
  "missing_requirements": ["List of missing requirements/qualifications"],
  "relevant_projects": ["Titles and relevance of candidate's existing projects"],
  "resume_keywords_to_consider": ["Keywords from job description the candidate can honestly emphasize"],
  "potential_weaknesses": ["Honest assessment of candidate's weak areas for this role"],
  "interview_preparation_topics": ["4-5 specific technical or behavioral questions/topics to prepare"],
  "transparent_assessment": "2-3 sentence executive assessment summarizing overall fit."
}
"""


class ResumeAnalyzerService:
    """Service performing deep comparative analysis between a candidate profile and a job."""

    def __init__(self) -> None:
        self._llm_client: Optional[LLMClient] = None

    def _get_llm_client(self) -> LLMClient:
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    def analyze(
        self, profile: CandidateProfile, job: JobOpportunity
    ) -> ResumeJobAnalysisResponse:
        """Perform deep comparative analysis."""
        match_result = matching_service.compute_match(profile, job)

        # Attempt structured analysis via LLM
        llm_analysis = self._analyze_with_llm(profile, job, match_result.match_score)
        if llm_analysis:
            return llm_analysis

        # Fallback to deterministic heuristic analysis
        return self._analyze_with_heuristics(profile, job, match_result)

    def _analyze_with_llm(
        self, profile: CandidateProfile, job: JobOpportunity, match_score: float
    ) -> Optional[ResumeJobAnalysisResponse]:
        """Query LLM for deep resume-to-job comparative evaluation."""
        try:
            client = self._get_llm_client()

            candidate_summary = {
                "name": profile.name,
                "education": [e.model_dump() for e in profile.education],
                "skills": profile.all_normalized_skills,
                "projects": [p.model_dump() for p in profile.projects],
                "experiences": [x.model_dump() for x in profile.experiences],
                "experience_level": profile.experience_level,
            }

            job_summary = {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "is_remote": job.is_remote,
                "required_skills": job.required_skills,
                "preferred_skills": job.preferred_skills,
                "description_excerpt": job.description[:1000],
            }

            prompt = (
                f"{ANALYSIS_SYSTEM_PROMPT}\n\n"
                f"CANDIDATE PROFILE:\n{json.dumps(candidate_summary, indent=2)}\n\n"
                f"TARGET JOB OPPORTUNITY:\n{json.dumps(job_summary, indent=2)}\n\n"
                f"CALCULATED FIT SCORE: {match_score}/100"
            )

            resp = client.invoke(prompt)
            response_text = str(getattr(resp, "content", resp))

            clean_json = response_text.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            elif clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            data: Dict[str, Any] = json.loads(clean_json)

            return ResumeJobAnalysisResponse(
                job_id=job.id,
                job_title=job.title,
                company=job.company,
                strengths=data.get("strengths", []),
                missing_requirements=data.get("missing_requirements", []),
                relevant_projects=data.get("relevant_projects", []),
                resume_keywords_to_consider=data.get("resume_keywords_to_consider", []),
                potential_weaknesses=data.get("potential_weaknesses", []),
                interview_preparation_topics=data.get("interview_preparation_topics", []),
                transparent_assessment=data.get("transparent_assessment", ""),
            )
        except Exception as exc:
            logger.warning("[RESUME-ANALYZER] LLM deep analysis fallback triggered: %s", exc)
            return None

    def _analyze_with_heuristics(
        self, profile: CandidateProfile, job: JobOpportunity, match_res: Any
    ) -> ResumeJobAnalysisResponse:
        """Deterministic heuristic fallback when LLM is unavailable."""
        strengths: List[str] = []
        for s in match_res.matched_required_skills[:4]:
            strengths.append(f"Demonstrated competence in core required skill: {s}")
        if match_res.matched_preferred_skills:
            strengths.append(f"Bonus alignment with preferred skills: {', '.join(match_res.matched_preferred_skills)}")

        missing: List[str] = []
        for m in match_res.missing_required_skills:
            missing.append(f"Required technology not verified in profile: {m}")
        for m in match_res.missing_preferred_skills:
            missing.append(f"Preferred skill gap: {m}")

        relevant_projects: List[str] = []
        for proj in profile.projects[:2]:
            relevant_projects.append(f"{proj.title} ({', '.join(proj.tech_stack)})")

        keywords = [s for s in job.required_skills if s.lower() in (profile.raw_resume_text or "").lower()]

        weaknesses = []
        if missing:
            weaknesses.append(f"Missing direct experience with {missing[0].split(': ')[-1]}")
        if not job.is_remote and profile.remote_preference == "remote_only":
            weaknesses.append("Geographic mismatch: On-site work required but candidate prefers remote")

        interview_topics = [
            f"Technical architecture and lifecycle of {job.required_skills[0]}" if job.required_skills else "System Design & REST API implementation",
            "Walkthrough of candidate's technical projects and problem-solving methodology",
            "Concurrency, error handling, and testing strategies in production environments",
            f"Team collaboration and engineering practices at {job.company}",
        ]

        assessment = (
            f"Candidate matches {len(match_res.matched_required_skills)} required skill(s) for the {job.title} role at {job.company}. "
            f"Overall algorithmic fit score is {match_res.match_score}/100."
        )

        return ResumeJobAnalysisResponse(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            strengths=strengths or ["General engineering background"],
            missing_requirements=missing,
            relevant_projects=relevant_projects,
            resume_keywords_to_consider=keywords or job.required_skills[:3],
            potential_weaknesses=weaknesses or ["No major red flags identified"],
            interview_preparation_topics=interview_topics,
            transparent_assessment=assessment,
        )


resume_analyzer = ResumeAnalyzerService()
