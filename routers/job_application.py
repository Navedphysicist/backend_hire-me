from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from db.database import get_db
from models.user import DbUser
from models.job import DbJob
from models.job_application import DbJobApplication
from schemas.job_application import JobApplicationCreate, JobApplication
from utils.token_utils import get_current_user
from routers.auth import oauth2_scheme
import os
from datetime import datetime
import uuid


router = APIRouter(
    prefix="/applications",
    tags=["Job Applications"]
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=JobApplication)
async def create_application(
    job_id: int = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    current_ctc: str = Form(...),
    expected_ctc: str = Form(...),
    notice_period: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    # Check if job exists
    job = db.query(DbJob).filter(DbJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check if user has already applied
    existing_application = db.query(DbJobApplication).filter(
        DbJobApplication.job_id == job_id,
        DbJobApplication.applicant_id == current_user.id
    ).first()
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )

    # Save resume file
    file_extension = os.path.splitext(resume.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    resume_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(resume_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save resume file"
        )

    # Create application record
    db_application = DbJobApplication(
        job_id=job_id,
        applicant_id=current_user.id,
        email=email,
        phone=phone,
        current_ctc=current_ctc,
        expected_ctc=expected_ctc,
        notice_period=notice_period,
        resume_path=resume_path,
        status="pending"
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("/", response_model=List[JobApplication])
async def read_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    applications = db.query(DbJobApplication).options(
        joinedload(DbJobApplication.job),
        joinedload(DbJobApplication.applicant)
    ).filter(
        DbJobApplication.applicant_id == current_user.id
    ).offset(skip).limit(limit).all()
    return applications
