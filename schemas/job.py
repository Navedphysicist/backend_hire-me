from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .company import Company


class JobBase(BaseModel):
    job_title: str
    job_description: str
    salary: float
    place: str
    skills: List[str]
    job_type: str
    work_mode: str
    experience_level: str


class JobCreate(JobBase):
    company_name: str
    company_avatar: Optional[str]


class Job(JobBase):
    id: int
    company_id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    company: Company

    class Config:
        from_attributes = True
