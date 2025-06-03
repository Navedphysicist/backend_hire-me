from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class DbCompany(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String,unique=True,nullable=False ,index=True)
    company_avatar = Column(String)
    company_description = Column(String)
    remote = Column(String)
    company_location = Column(String)
    company_type = Column(String)
    industry_type = Column(String)
    business_nature = Column(String)
    employee_count = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("DbUser", back_populates="companies")
    jobs = relationship("DbJob", back_populates="company")
