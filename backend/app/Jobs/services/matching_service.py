"""
Jarvis AIOS — Skill Matching & Gap Analysis Service
----------------------------------------------------
Provides deterministic, transparent, and fully documented matching calculations
between candidate profiles and real job opportunities.
No arbitrary scores: Score is strictly computed based on verified skill overlap (60%),
experience alignment (20%), and location/remote compatibility (20%).
"""

import re
from typing import Any, Dict, List, Set
from app.Jobs.models.candidate_profile import CandidateProfile
from app.Jobs.models.job_opportunity import JobOpportunity
from app.Jobs.models.skill_matching import SkillMatchResult, SkillGapAnalysis
from app.Jobs.services.skill_normalizer import skill_normalizer


class MatchingService:
    """Service evaluating candidate compatibility with job opportunities."""

    def compute_match(
        self, profile: CandidateProfile, job: JobOpportunity
    ) -> SkillMatchResult:
        """
        Compute transparent match result.

        Formula:
          Total Score (100) = Skill Overlap (60%) + Experience Match (20%) + Location/Remote Match (20%)
        """
        user_skills_set: Set[str] = {s.lower() for s in profile.all_normalized_skills}
        job_req_skills: List[str] = job.required_skills or []
        job_pref_skills: List[str] = job.preferred_skills or []

        # If job has no structured required skills, scan job description for known tech skills
        if not job_req_skills and job.description:
            desc_lower = job.description.lower()
            detected_in_desc = []
            for skill in profile.all_normalized_skills:
                if re.search(r"\b" + re.escape(skill.lower()) + r"\b", desc_lower):
                    detected_in_desc.append(skill)
            job_req_skills = detected_in_desc[:6]

        # 1. Skill Overlap
        matched_required: List[str] = []
        missing_required: List[str] = []
        for s in job_req_skills:
            norm_s = skill_normalizer.normalize_single(s)
            if norm_s.lower() in user_skills_set:
                matched_required.append(norm_s)
            else:
                missing_required.append(norm_s)

        matched_preferred: List[str] = []
        missing_preferred: List[str] = []
        for s in job_pref_skills:
            norm_s = skill_normalizer.normalize_single(s)
            if norm_s.lower() in user_skills_set:
                matched_preferred.append(norm_s)
            else:
                missing_preferred.append(norm_s)

        total_req_count = len(job_req_skills)
        if total_req_count > 0:
            skill_pct = len(matched_required) / total_req_count
        else:
            skill_pct = 0.5  # Neutral when no skills specified

        skill_score = skill_pct * 60.0

        # 2. Experience Level Compatibility (20 pts)
        exp_score = 0.0
        candidate_lvl = (profile.experience_level or "entry_level").lower()
        job_lvl = (job.experience_level or "entry_level").lower()
        job_emp_type = (job.employment_type or "full_time").lower()

        if candidate_lvl in ["student", "intern", "entry_level"] and (job_lvl in ["intern", "entry_level"] or job_emp_type == "internship"):
            exp_score = 20.0
        elif candidate_lvl == job_lvl:
            exp_score = 20.0
        elif candidate_lvl in ["junior", "mid"] and job_lvl in ["entry_level", "junior"]:
            exp_score = 20.0
        else:
            exp_score = 10.0

        # 3. Location / Remote Compatibility (20 pts)
        loc_score = 0.0
        user_remote_pref = (profile.remote_preference or "any").lower()
        if job.is_remote and user_remote_pref in ["any", "remote_only", "hybrid"]:
            loc_score = 20.0
        elif not job.is_remote and user_remote_pref == "remote_only":
            loc_score = 0.0
        else:
            # Check location match
            job_loc_lower = job.location.lower()
            matched_loc = any(loc.lower() in job_loc_lower for loc in profile.preferred_locations)
            if matched_loc:
                loc_score = 20.0
            else:
                loc_score = 10.0 if user_remote_pref == "any" else 5.0

        total_score = min(100.0, max(0.0, round(skill_score + exp_score + loc_score, 1)))

        # Construct Transparent Reasons and Gaps
        match_reasons: List[str] = []
        if matched_required:
            match_reasons.append(f"✓ Matched required skills: {', '.join(matched_required[:5])}")
        if matched_preferred:
            match_reasons.append(f"✓ Matched preferred skills: {', '.join(matched_preferred[:3])}")
        if exp_score >= 18.0:
            match_reasons.append(f"✓ Experience alignment: {job.employment_type.replace('_', ' ').title()} matches your profile level")
        if job.is_remote:
            match_reasons.append("✓ Location flexibility: Verified remote opportunity")
        elif loc_score >= 18.0:
            match_reasons.append(f"✓ Location compatible: {job.location}")

        potential_gaps: List[str] = []
        for miss in missing_required:
            potential_gaps.append(f"△ Required skill gap: {miss}")
        for miss in missing_preferred:
            potential_gaps.append(f"△ Preferred skill gap: {miss}")
        if not job.is_remote and user_remote_pref == "remote_only":
            potential_gaps.append(f"△ On-site location requirement ({job.location}) does not match remote preference")

        score_breakdown: Dict[str, Any] = {
            "skill_overlap_pts": round(skill_score, 1),
            "skill_overlap_max": 60,
            "experience_match_pts": round(exp_score, 1),
            "experience_match_max": 20,
            "location_match_pts": round(loc_score, 1),
            "location_match_max": 20,
            "algorithm": "60% verified skill overlap + 20% experience compatibility + 20% location/remote fit",
        }

        return SkillMatchResult(
            job_id=job.id,
            matched_required_skills=matched_required,
            missing_required_skills=missing_required,
            matched_preferred_skills=matched_preferred,
            missing_preferred_skills=missing_preferred,
            match_score=total_score,
            match_reasons=match_reasons,
            potential_gaps=potential_gaps,
            score_breakdown=score_breakdown,
        )

    def analyze_skill_gaps(
        self, profile: CandidateProfile, job: JobOpportunity
    ) -> SkillGapAnalysis:
        """Detailed gap analysis identifying missing skills, candidate projects, and preparation roadmap."""
        match_res = self.compute_match(profile, job)
        all_missing = match_res.missing_required_skills + match_res.missing_preferred_skills

        # Find relevant existing projects from candidate's profile
        relevant_projects: List[str] = []
        user_skills_lower = {s.lower() for s in profile.all_normalized_skills}
        for proj in profile.projects:
            proj_skills = {s.lower() for s in proj.tech_stack}
            if proj_skills.intersection(user_skills_lower) or any(
                m.lower() in proj.description.lower() for m in match_res.matched_required_skills
            ):
                relevant_projects.append(f"{proj.title}: {proj.description[:120]}")

        # Construct recommended preparation roadmap for missing skills
        recommended_prep: List[str] = []
        for miss in all_missing[:4]:
            recommended_prep.append(f"Study core concepts of {miss} and implement a practical reference component.")

        if not recommended_prep:
            recommended_prep.append("Review company interview fundamentals and domain-specific system design.")

        return SkillGapAnalysis(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            user_skills=profile.all_normalized_skills,
            required_skills=job.required_skills,
            matched_skills=match_res.matched_required_skills,
            missing_skills=all_missing,
            relevant_projects=relevant_projects[:3],
            recommended_preparation=recommended_prep,
        )


matching_service = MatchingService()
