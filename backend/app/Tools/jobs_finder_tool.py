"""
Jarvis AIOS — Jobs & Internship Finder Tool
--------------------------------------------
Tool Engine integration allowing Lisa Assistant to search authentic tech jobs and internships,
evaluate profile compatibility, and identify skill gaps with transparent explanations.
Strict Zero-Fabrication: Never invents fake companies, salaries, or phantom opportunities.
"""

from typing import Any, Dict, List, Optional
from app.Tools.tool import Tool
from app.Tools.metadata import ToolMetadata, PermissionLevel
from app.Jobs.models.job_opportunity import JobSearchFilters
from app.Jobs.services.jobs_service import jobs_service
from app.Jobs.services.skill_normalizer import skill_normalizer


class JobsFinderTool(Tool):
    """Integrated Jobs and Internships search tool for Lisa AIOS."""

    def __init__(self) -> None:
        self.metadata = ToolMetadata(
            name="jobs_finder",
            description=(
                "Search verified live tech jobs and internships, analyze candidate skill matches, "
                "and identify skill gaps with verified application links."
            ),
            permission_level=PermissionLevel.PUBLIC,
        )

    def execute(
        self,
        role: str = "",
        location: str = "",
        is_remote: Optional[bool] = None,
        employment_type: str = "any",
        skills: Any = None,
        user_id: str = "1",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute live job search with profile match scoring."""
        # Normalize skill parameters
        skill_list: List[str] = []
        if isinstance(skills, list):
            skill_list = skill_normalizer.normalize_list([str(s) for s in skills])
        elif isinstance(skills, str) and skills.strip():
            skill_list = skill_normalizer.normalize_list([s.strip() for s in skills.split(",")])

        filters = JobSearchFilters(
            role=role.strip() or None,
            location=location.strip() or None,
            is_remote=is_remote,
            employment_type=employment_type if employment_type != "any" else None,
            skills=skill_list,
            limit=10,
        )

        search_resp, matches = jobs_service.search_jobs(filters, user_id=user_id)

        if not search_resp.jobs:
            return {
                "status": "success",
                "total_results": 0,
                "jobs": [],
                "summary": "No matching opportunities were found for your criteria on verified provider feeds. Try broadening your location or role terms.",
            }

        # Build readable, transparent markdown for Lisa Assistant
        summary_lines = [
            f"### Verified Opportunities for {filters.role or 'Software & AI Roles'}",
            f"*Source: {search_resp.provider_used} (Strictly verified live postings)*\n",
        ]

        for idx, job in enumerate(search_resp.jobs[:5], start=1):
            match_res = matches.get(job.id)
            salary_str = f" | **Compensation**: {job.salary_or_stipend}" if job.salary_or_stipend else ""
            remote_tag = "🌐 Remote" if job.is_remote else f"📍 {job.location}"

            summary_lines.append(f"**{idx}. [{job.title}]({job.apply_url})** — **{job.company}**")
            summary_lines.append(f"- **Type**: {job.employment_type.replace('_', ' ').title()} | **Location**: {remote_tag}{salary_str}")

            if match_res:
                if match_res.match_reasons:
                    reasons_str = " • ".join(match_res.match_reasons[:2])
                    summary_lines.append(f"- **Why it matches**: {reasons_str}")
                if match_res.potential_gaps:
                    gaps_str = " • ".join(match_res.potential_gaps[:2])
                    summary_lines.append(f"- **Skill Gaps**: {gaps_str}")

            summary_lines.append(f"- **Apply**: [Official Application Portal]({job.apply_url})\n")

        summary_lines.append(
            "> [!NOTE]\n"
            "> Lisa AIOS does not submit applications autonomously. Click the official link to apply directly with the employer."
        )

        return {
            "status": "success",
            "total_results": len(search_resp.jobs),
            "jobs": [j.model_dump() for j in search_resp.jobs],
            "summary": "\n".join(summary_lines),
        }
