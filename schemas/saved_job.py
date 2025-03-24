from pydantic import BaseModel
from datetime import datetime
from schemas.job import Job


class SavedJobBase(BaseModel):
    job_id: int


class SavedJobCreate(SavedJobBase):
    pass


class SavedJob(SavedJobBase):
    id: int
    user_id: int
    created_at: datetime
    job: Job

    class Config:
        from_attributes = True
