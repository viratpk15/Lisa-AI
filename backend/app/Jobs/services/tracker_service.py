"""
Jarvis AIOS — Application Tracker Service
------------------------------------------
Manages candidate-tracked job opportunities across application statuses:
Saved, Applied, Interview, Rejected, Offer.
Strict policy: Only the user can transition status. Lisa never submits automatically.
"""

from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional

from app.Jobs.models.application_tracker import (
    ApplicationStatusEnum,
    ApplicationTrackItem,
    UpdateApplicationStatusRequest,
)
from app.Jobs.models.job_opportunity import JobOpportunity

logger = logging.getLogger(__name__)


class ApplicationTrackerService:
    """In-memory & session-isolated application lifecycle tracking service."""

    def __init__(self) -> None:
        # User ID -> {Job ID -> ApplicationTrackItem}
        self._user_tracks: Dict[str, Dict[str, ApplicationTrackItem]] = {}

    def track_job(
        self, user_id: str, job: JobOpportunity, initial_status: ApplicationStatusEnum = ApplicationStatusEnum.SAVED
    ) -> ApplicationTrackItem:
        """Add or update a job in the user's tracker."""
        if user_id not in self._user_tracks:
            self._user_tracks[user_id] = {}

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        item = ApplicationTrackItem(
            job_id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            apply_url=job.apply_url,
            status=initial_status,
            saved_at=now_str,
            applied_at=now_str if initial_status == ApplicationStatusEnum.APPLIED else None,
            is_user_confirmed=True,
        )

        self._user_tracks[user_id][job.id] = item
        logger.info("[TRACKER] User %s tracked job %s as %s", user_id, job.id, initial_status)
        return item

    def get_user_applications(self, user_id: str) -> List[ApplicationTrackItem]:
        """Return all tracked applications for a user, sorted newest first."""
        user_items = self._user_tracks.get(user_id, {})
        return list(user_items.values())

    def update_application_status(
        self, user_id: str, job_id: str, req: UpdateApplicationStatusRequest
    ) -> Optional[ApplicationTrackItem]:
        """Explicit user-initiated status update."""
        user_items = self._user_tracks.get(user_id, {})
        if job_id not in user_items:
            return None

        item = user_items[job_id]
        item.status = req.status
        if req.notes is not None:
            item.notes = req.notes
        if req.interview_date is not None:
            item.interview_date = req.interview_date
        if req.status == ApplicationStatusEnum.APPLIED and not item.applied_at:
            item.applied_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        logger.info("[TRACKER] User %s updated job %s to %s", user_id, job_id, req.status)
        return item

    def remove_job(self, user_id: str, job_id: str) -> bool:
        """Remove a job from user's tracker."""
        if user_id in self._user_tracks and job_id in self._user_tracks[user_id]:
            del self._user_tracks[user_id][job_id]
            return True
        return False


tracker_service = ApplicationTrackerService()
