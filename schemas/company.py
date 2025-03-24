from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    company_name: str
    company_description: Optional[str] = None
    remote: Optional[str] = None
    company_location: Optional[str] = None
    company_type: Optional[str] = None
    industry_type: Optional[str] = None
    business_nature: Optional[str] = None
    employee_count: Optional[str] = None


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
