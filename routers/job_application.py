from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from models.user import DbUser
from models.job import DbJob
from models.job_application import DbJobApplication
from schemas.job_application import JobApplicationCreate, JobApplication
from utils.token_utils import get_current_user
from routers.auth import oauth2_scheme


router = APIRouter(
    prefix="/applications",
    tags=["Job Applications"]
)


@router.post("/", response_model=JobApplication)
async def create_application(
    application: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    # Check if job exists
    job = db.query(DbJob).filter(DbJob.id == application.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check if user has already applied
    existing_application = db.query(DbJobApplication).filter(
        DbJobApplication.job_id == application.job_id,
        DbJobApplication.applicant_id == current_user.id
    ).first()
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )

    db_application = DbJobApplication(
        **application.dict(),
        applicant_id=current_user.id
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
    applications = db.query(DbJobApplication).filter(
        DbJobApplication.applicant_id == current_user.id
    ).offset(skip).limit(limit).all()
    return applications
