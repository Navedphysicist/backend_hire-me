from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class JobApplicationBase(BaseModel):
    email: EmailStr
    phone: str
    current_ctc: str
    expected_ctc: str
    notice_period: str
    resume_path: str


class JobApplicationCreate(JobApplicationBase):
    job_id: int


class JobApplication(JobApplicationBase):
    id: int
    job_id: int
    applicant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
