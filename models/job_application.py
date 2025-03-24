from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from db.database import Base


class DbJobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    applicant_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String)
    phone = Column(String)
    current_ctc = Column(String)
    expected_ctc = Column(String)
    notice_period = Column(String)
    resume_path = Column(String, nullable=True)
    # pending, reviewed, accepted, rejected
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True,
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    job = relationship("DbJob", back_populates="applications")
    applicant = relationship("DbUser", back_populates="applications")
