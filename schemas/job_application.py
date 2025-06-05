from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.job import Job
from .user import User


class JobApplicationBase(BaseModel):
    job_id: int
    email: str
    phone: str
    current_ctc: str
    expected_ctc: str
    notice_period: str


class JobApplicationCreate(JobApplicationBase):
    pass


class JobApplication(JobApplicationBase):
    id: int
    applicant_id: int
    resume_path: str
    status: str = "pending"  # pending, reviewed, accepted, rejected
    created_at: datetime
    updated_at: Optional[datetime] = None
    job: Job
    applicant: User

    class Config:
        from_attributes = True
