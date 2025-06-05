from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List
from db.database import get_db
from models.user import DbUser
from models.job import DbJob
from models.job_application import DbJobApplication
from schemas.job_application import JobApplication
from utils.token_utils import get_current_user
from utils.file_storage import save_upload_file
from datetime import datetime, timezone
from pathlib import Path


router = APIRouter(
    tags=["Job Applications"]
)

# Allowed file extensions for resumes
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}

def is_valid_resume(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


@router.post("/apply", response_model=JobApplication)
def create_application(
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

    # Validate and save resume file
    if not is_valid_resume(resume.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Invalid file type",
                "error": "Only PDF, DOC, and DOCX files are allowed",
                "solution": "Please upload a valid resume file"
            }
        )

    # Generate unique filename
    file_ext = Path(resume.filename).suffix.lower()
    email_prefix = email.split("@")[0] 
    filename = f"{email_prefix}{file_ext}"
    folder_path = "resumes"
    resource_type = "raw"

    try:
        resume_url = save_upload_file(resume, filename, folder_path, resource_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error uploading resume",
                "error": str(e)
            }
        )
    try:
        # Create application record
        db_application = DbJobApplication(
            job_id=job_id,
            applicant_id=current_user.id,
            email=email,
            phone=phone,
            current_ctc=current_ctc,
            expected_ctc=expected_ctc,
            notice_period=notice_period,
            resume_path=resume_url,  # Use the URL from file storage
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error creating job application",
                "error": str(e)
            }
        )


@router.get("/applications/{job_id}", response_model=List[JobApplication])
def get_applications_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    applications = db.query(DbJobApplication).filter(
        DbJobApplication.job_id == job_id
    ).all()

    if not applications:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No application found for this Job"
        )
    return applications
