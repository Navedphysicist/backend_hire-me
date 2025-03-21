from pydantic import BaseModel
from datetime import datetime


class SavedJobBase(BaseModel):
    job_id: int


class SavedJobCreate(SavedJobBase):
    pass


class SavedJob(SavedJobBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
