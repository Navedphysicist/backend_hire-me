from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class DbJob(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    company_avatar = Column(String)
    job_description = Column(String)
    salary = Column(Float)
    place = Column(String)
    skills = Column(JSON) 
    job_type = Column(String)
    work_mode = Column(String)
    experience_level = Column(String)
    job_title = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("DbCompany", back_populates="jobs")
    creator = relationship("DbUser", back_populates="jobs")
    applications = relationship("DbJobApplication", back_populates="job")
    saved_by_users = relationship("DbSavedJob", back_populates="job")
