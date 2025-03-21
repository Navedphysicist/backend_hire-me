from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import String
from typing import List, Optional
from db.database import get_db
from models.user import DbUser
from models.job import DbJob
from models.company import DbCompany
from schemas.job import JobCreate, Job as JobSchema
from utils.token_utils import get_current_user

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.get("/", response_model=List[JobSchema])
def get_jobs(
    role: Optional[str] = Query(None, description="Filter by job role/title"),
    location: Optional[str] = Query(
        None, description="Filter by job location"),
    search: Optional[str] = Query(None, description="Search jobs by keywords"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(DbJob).join(DbCompany)

    if role:
        query = query.filter(DbJob.job_title.ilike(f"%{role}%"))
    if location:
        query = query.filter(DbJob.place.ilike(f"%{location}%"))
    if search:
        query = query.filter(
            (DbJob.job_title.ilike(f"%{search}%")) |
            (DbJob.job_description.ilike(f"%{search}%")) |
            (DbJob.skills.cast(String).ilike(f"%{search}%"))
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{job_id}", response_model=JobSchema)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DbJob).filter(DbJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=JobSchema)
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    # First, create or get the company
    company = db.query(DbCompany).filter(
        DbCompany.company_name == job.company_name,
        DbCompany.owner_id == current_user.id
    ).first()

    if not company:
        # Create new company if it doesn't exist
        company = DbCompany(
            name=job.company_name,
            avatar=job.company_avatar,
            owner_id=current_user.id
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    # Create the job with the company_id
    db_job = DbJob(
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

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/posted_jobs", response_model=List[JobSchema])
async def get_posted_jobs(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    return db.query(DbJob).options(
        joinedload(DbJob.applications)
    ).filter(
        DbJob.creator_id == current_user.id
    ).all()
