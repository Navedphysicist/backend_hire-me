from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    company_name: str
    company_description: str
    remote: str
    company_location: str
    company_type: str
    industry_type: str
    business_nature: str
    employee_count: str


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    id: int
    company_avatar: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
