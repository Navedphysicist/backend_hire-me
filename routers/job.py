from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import String
from typing import List, Optional
from db.database import get_db
from models.user import DbUser
from models.job import DbJob
from models.company import DbCompany
from schemas.job import JobCreate, Job as JobSchema
from models.job_application import DbJobApplication
from utils.token_utils import get_current_user


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.get("", response_model=List[JobSchema])
def get_jobs(
    role: Optional[str] = Query(None, description="Filter by job role/title"),
    location: Optional[str] = Query(None, description="Filter by job location"),
    search: Optional[str] = Query(None, description="Search jobs by keywords"),
    db: Session = Depends(get_db)
):
    query = db.query(DbJob)

    if role and role.strip():
        query = query.filter(DbJob.job_title.ilike(f"%{role}%"))
    if location and location.strip():
        query = query.filter(DbJob.place.ilike(f"%{location}%"))
    if search and search.strip():
        query = query.filter(
            (DbJob.job_title.ilike(f"%{search}%")) |
            (DbJob.job_description.ilike(f"%{search}%")) |
            (DbJob.skills.cast(String).ilike(f"%{search}%"))
        )

    return query.all()


@router.get("/posted_jobs",response_model=List[JobSchema])
def get_posted_jobs(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    return db.query(DbJob).filter(DbJob.creator_id == current_user.id).all()


@router.get("/applied_jobs", response_model=List[JobSchema])
def get_applied_jobs(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    jobs = db.query(DbJob).join(DbJobApplication).filter(
        DbJobApplication.applicant_id == current_user.id
    ).all()

    return jobs



@router.get("/{job_id}", response_model=JobSchema)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DbJob).filter(DbJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobSchema)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    # First, check if the company exists
    company = db.query(DbCompany).filter(
        DbCompany.company_name == job.company_name,
        DbCompany.owner_id == current_user.id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Company not found",
                "error": "You need to register your company first before posting jobs",
                "solution": "Please create your company profile."
            }
        )

    # Check if company has required fields
    if not company.company_description or not company.company_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Incomplete company profile",
                "error": "Your company profile is incomplete",
                "solution": "Please complete your company profile before posting jobs",
                "missing_fields": ["company_description", "company_location"]
            }
        )

    # Create the job with the company_id
    db_job = DbJob(
        company_name=job.company_name,
        company_avatar=job.company_avatar,
        company_id=company.id,
        job_title=job.job_title,
        job_description=job.job_description,
        salary=job.salary,
        place=job.place,
        skills=job.skills,
        job_type=job.job_type,
        work_mode=job.work_mode,
        experience_level=job.experience_level,
        creator_id=current_user.id
    )

    try:
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to create job",
                "error": str(e),
                "solution": "Please try again or contact support if the issue persists"
            }
        )


