"""
Jarvis AIOS — Resume Parser Service
------------------------------------
Extracts structured CandidateProfile from PDF, DOCX, and TXT resume files.
Combines high-accuracy LLM structured schema parsing with resilient heuristic fallbacks.
Strict policy: Never assumes extracted info is 100% correct; flags for user confirmation.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.RAG.extractors import DocumentExtractorFactory
from app.Jobs.models.candidate_profile import (
    CandidateProfile,
    EducationItem,
    ProjectItem,
    ExperienceItem,
)
from app.Jobs.services.skill_normalizer import skill_normalizer, CANONICAL_SKILL_MAP
from app.LLM.client import LLMClient

logger = logging.getLogger(__name__)


RESUME_EXTRACTION_SYSTEM_PROMPT = """You are an expert technical resume parser for Lisa AIOS.
Analyze the provided resume text and extract candidate details in strictly valid JSON format matching this schema:

{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "education": [
    {
      "college": "University Name",
      "degree": "B.Tech / B.S. / M.S.",
      "branch": "Computer Science / Information Technology",
      "graduation_year": 2025,
      "cgpa": 8.8,
      "current_semester": "8th semester"
    }
  ],
  "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Machine Learning"],
  "projects": [
    {
      "title": "Project Name",
      "description": "Summary of what was built and impact",
      "tech_stack": ["Python", "PyTorch"],
      "github_url": "link if available"
    }
  ],
  "experiences": [
    {
      "company": "Company Name",
      "role": "Role Title",
      "duration": "June 2024 - Aug 2024",
      "description": "Key contributions",
      "is_internship": true,
      "skills_used": ["Python", "FastAPI"]
    }
  ],
  "certifications": ["AWS Certified Cloud Practitioner"],
  "achievements": ["1st place in Hackathon 2024"],
  "preferred_roles": ["AI Engineer", "Software Engineer", "Backend Developer"],
  "preferred_locations": ["Bangalore", "Remote"],
  "experience_level": "entry_level"
}

Do NOT invent fake skills, jobs, or credentials. Only extract what is present in the resume.
Return pure JSON only, without any markdown formatting or explanations.
"""


class ResumeParserService:
    """Service for extracting text and structured profiles from resumes."""

    def __init__(self) -> None:
        self._llm_client: Optional[LLMClient] = None

    def _get_llm_client(self) -> LLMClient:
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """Extract text content from file bytes using RAG document extractors."""
        extractor = DocumentExtractorFactory.get_extractor(filename)
        doc = extractor.extract(file_bytes, filename)
        return doc.full_text or ""

    def parse_resume(self, file_bytes: bytes, filename: str) -> CandidateProfile:
        """Parse resume file bytes into an unconfirmed, editable CandidateProfile."""
        raw_text = self.extract_text_from_file(file_bytes, filename)
        if not raw_text.strip():
            logger.warning("[RESUME-PARSER] No text could be extracted from '%s'", filename)
            profile = CandidateProfile(name="Candidate", raw_resume_text="")
            profile.extracted_from_resume = True
            profile.is_confirmed_by_user = False
            return profile

        # Attempt structured extraction via LLM
        profile = self._extract_with_llm(raw_text)
        if profile is None:
            # Fallback to deterministic regex heuristics
            logger.info("[RESUME-PARSER] Using heuristic fallback for '%s'", filename)
            profile = self._extract_with_heuristics(raw_text)

        profile.raw_resume_text = raw_text
        profile.extracted_from_resume = True
        profile.is_confirmed_by_user = False

        # Normalize all skills
        profile.all_normalized_skills = skill_normalizer.normalize_list(profile.all_normalized_skills)
        profile.skills = skill_normalizer.categorize_skills(profile.all_normalized_skills)

        return profile

    def _extract_with_llm(self, resume_text: str) -> Optional[CandidateProfile]:
        """Extract structured resume profile using the LLM provider abstraction."""
        try:
            client = self._get_llm_client()
            prompt = f"{RESUME_EXTRACTION_SYSTEM_PROMPT}\n\nRESUME TEXT:\n{resume_text[:4000]}"
            resp = client.invoke(prompt)
            response_text = str(getattr(resp, "content", resp))

            # Strip possible markdown code fence
            clean_json = response_text.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            elif clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            data: Dict[str, Any] = json.loads(clean_json)

            education = [EducationItem(**item) for item in data.get("education", [])]
            projects = [ProjectItem(**item) for item in data.get("projects", [])]
            experiences = [ExperienceItem(**item) for item in data.get("experiences", [])]
            raw_skills = data.get("skills", [])

            return CandidateProfile(
                name=data.get("name", "Candidate"),
                email=data.get("email"),
                phone=data.get("phone"),
                education=education,
                projects=projects,
                experiences=experiences,
                certifications=data.get("certifications", []),
                achievements=data.get("achievements", []),
                preferred_roles=data.get("preferred_roles", []),
                preferred_locations=data.get("preferred_locations", []),
                experience_level=data.get("experience_level", "entry_level"),
                all_normalized_skills=raw_skills,
            )
        except Exception as exc:
            logger.warning("[RESUME-PARSER] LLM structured extraction failed: %s", exc)
            return None

    def _extract_with_heuristics(self, text: str) -> CandidateProfile:
        """Deterministic heuristic extraction based on regular expressions and dictionary scanning."""
        # 1. Email extraction
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        email = email_match.group(0) if email_match else None

        # 2. Phone extraction
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        phone = phone_match.group(0) if phone_match else None

        # 3. Name heuristic (first clean header line before email or section labels, ignoring page markers)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        name = "Candidate"
        for line in lines[:10]:
            # Skip page headers, dashes, symbols
            if line.startswith("---") or re.match(r"^[-=_\s*#]+$", line):
                continue
            if re.search(r"\bpage\s*\d+\b", line, re.IGNORECASE):
                continue
            if "@" in line or re.search(r"\b(email|phone|curriculum|resume|cv|contact|portfolio|github|linkedin|professional summary)\b", line, re.IGNORECASE):
                continue
            if 2 <= len(line) <= 50 and any(c.isalpha() for c in line):
                clean_name = re.sub(r"[^a-zA-Z\s\.]", "", line).strip().title()
                if clean_name and len(clean_name.split()) >= 1:
                    name = clean_name
                    break

        # 4. CGPA extraction (e.g. "CGPA: 8.9" or "GPA 3.8/4.0")
        cgpa = None
        cgpa_match = re.search(r"(?:cgpa|gpa)[\s:]*([0-9]\.[0-9]+)", text, re.IGNORECASE)
        if cgpa_match:
            try:
                cgpa = float(cgpa_match.group(1))
            except ValueError:
                pass

        # 5. Graduation year (e.g. 2024, 2025, 2026)
        grad_year = None
        year_match = re.search(r"\b(202[0-9]|201[8-9])\b", text)
        if year_match:
            grad_year = int(year_match.group(1))

        # 6. Education item
        college = "University / College"
        degree = "B.Tech / Bachelor's"
        branch = "Computer Science"

        if re.search(r"\b(b\.?tech|bachelor|b\.?s|b\.?e)\b", text, re.IGNORECASE):
            degree = "B.Tech / B.E."
        elif re.search(r"\b(m\.?tech|master|m\.?s)\b", text, re.IGNORECASE):
            degree = "M.Tech / M.S."

        if re.search(r"\b(artificial intelligence|machine learning|ai\s*&?\s*ml)\b", text, re.IGNORECASE):
            branch = "Computer Science (AI & ML)"
        elif re.search(r"\b(information technology|it)\b", text, re.IGNORECASE):
            branch = "Information Technology"

        for line in lines[:25]:
            if any(term in line.lower() for term in ["institute", "university", "college", "iit", "nit", "bits", "vidyavardhaka"]):
                if "student at" in line.lower():
                    parts = re.split(r"student\s+at\s+", line, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        college = parts[1].strip()
                        break
                college = line.strip()
                break

        education = [EducationItem(college=college, degree=degree, branch=branch, graduation_year=grad_year, cgpa=cgpa)]

        # 7. Scan skills from canonical skills map
        detected_skills: List[str] = []
        text_lower = text.lower()
        for alias, canonical in CANONICAL_SKILL_MAP.items():
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower) and canonical not in detected_skills:
                detected_skills.append(canonical)

        # 8. Detect project mentions & links
        projects: List[ProjectItem] = []
        github_match = re.search(r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+", text)
        github_url = github_match.group(0) if github_match else None

        project_headers = ["projects", "personal projects", "academic projects"]
        for idx, line in enumerate(lines):
            if any(h in line.lower() for h in project_headers) and idx + 1 < len(lines):
                # Next few lines might be project names
                for next_line in lines[idx + 1: idx + 4]:
                    if 5 < len(next_line) < 80:
                        projects.append(ProjectItem(title=next_line, description=next_line, tech_stack=[], github_url=github_url))
                break

        # Career Preferences inferred from skills
        preferred_roles: List[str] = []
        if any(s in detected_skills for s in ["Machine Learning", "Deep Learning", "LLMs", "RAG", "LangChain", "LangGraph"]):
            preferred_roles.extend(["AI Engineer", "Machine Learning Engineer", "GenAI Engineer"])
        if any(s in detected_skills for s in ["Python", "FastAPI", "React", "SQL"]):
            preferred_roles.append("Full Stack Developer")
        if not preferred_roles:
            preferred_roles = ["Software Engineer"]

        preferred_locations: List[str] = []
        if "bangalore" in text_lower or "bengaluru" in text_lower or "mysore" in text_lower:
            preferred_locations = ["Bangalore", "Remote"]
        else:
            preferred_locations = ["Remote"]

        return CandidateProfile(
            name=name,
            email=email,
            phone=phone,
            education=education,
            projects=projects,
            all_normalized_skills=detected_skills,
            preferred_roles=preferred_roles,
            preferred_locations=preferred_locations,
            experience_level="entry_level" if (grad_year and grad_year >= 2024) else "junior",
        )


resume_parser = ResumeParserService()
