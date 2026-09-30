"""
Jarvis AIOS — Application Tracker Models
-----------------------------------------
Data models for tracking user-selected jobs across life cycle statuses:
Saved, Applied, Interview, Rejected, Offer.
Strict policy: Only user actions can transition status. Lisa never submits automatically.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ApplicationStatusEnum(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"


class ApplicationTrackItem(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    apply_url: str
    status: ApplicationStatusEnum = ApplicationStatusEnum.SAVED
    saved_at: str
    applied_at: Optional[str] = None
    interview_date: Optional[str] = None
    notes: Optional[str] = None
    is_user_confirmed: bool = True


class UpdateApplicationStatusRequest(BaseModel):
    status: ApplicationStatusEnum
    notes: Optional[str] = None
    interview_date: Optional[str] = None
