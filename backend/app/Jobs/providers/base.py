"""
Jarvis AIOS — Base Job Provider Interface
------------------------------------------
Abstract base class for all job and internship search providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.Jobs.models.job_opportunity import JobOpportunity, JobSearchFilters


class BaseJobProvider(ABC):
    """Abstract interface for querying job search services."""

    @abstractmethod
    def search_jobs(self, filters: JobSearchFilters) -> List[JobOpportunity]:
        """Search job opportunities matching criteria."""
        pass

    @abstractmethod
    def get_job_by_id(self, job_id: str) -> Optional[JobOpportunity]:
        """Retrieve full details of a specific job by unique ID."""
        pass

    def get_status_summary(self, total_jobs: int) -> str:
        """Provide honest status description for search results."""
        if total_jobs > 0:
            return f"Found {total_jobs} verified opportunities."
        return "No matching opportunities were found."
