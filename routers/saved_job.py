from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from db.database import get_db
from models.user import DbUser
from models.job import DbJob
from models.saved_job import DbSavedJob
from schemas.saved_job import SavedJobCreate, SavedJob
from utils.token_utils import get_current_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    prefix="/saved-jobs",
    tags=["Saved Jobs"]
)


@router.post("/", response_model=SavedJob)
def save_job(
    saved_job: SavedJobCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    # Check if job exists
    job = db.query(DbJob).filter(DbJob.id == saved_job.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check if job is already saved
    existing_saved_job = db.query(DbSavedJob).filter(
        DbSavedJob.job_id == saved_job.job_id,
        DbSavedJob.user_id == current_user.id
    ).first()
    if existing_saved_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is already saved"
        )

    db_saved_job = DbSavedJob(
        **saved_job.model_dump(),
        user_id=current_user.id
    )
    db.add(db_saved_job)
    db.commit()
    db.refresh(db_saved_job)
    return db_saved_job


@router.get("/", response_model=List[SavedJob])
def read_saved_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    saved_jobs = db.query(DbSavedJob).options(
        joinedload(DbSavedJob.job)
    ).filter(
        DbSavedJob.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return saved_jobs


@router.delete("/{saved_job_id}")
def delete_saved_job(
    saved_job_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    saved_job = db.query(DbSavedJob).filter(
        DbSavedJob.id == saved_job_id,
        DbSavedJob.user_id == current_user.id
    ).first()
    if not saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved job not found"
        )

    db.delete(saved_job)
    db.commit()
    return {"message": "Saved job deleted successfully"}
