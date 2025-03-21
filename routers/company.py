from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from models.user import DbUser
from models.company import DbCompany
from models.job import DbJob
from schemas.company import CompanyCreate, Company as CompanySchema
from schemas.job import Job as JobSchema
from schemas.user import UserBase
from utils.token_utils import get_current_user
from routers.auth import oauth2_scheme

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)



@router.get("/", response_model=List[CompanySchema])
async def read_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)

):
    companies = db.query(DbCompany).filter(
        DbCompany.owner_id == current_user.id).offset(skip).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=CompanySchema)
async def read_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    company = db.query(DbCompany).filter(
        DbCompany.id == company_id, DbCompany.owner_id == current_user.id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/{company_id}/jobs", response_model=List[JobSchema])
def get_company_jobs(
    company_id: int,
    db: Session = Depends(get_db)
):
    company = db.query(DbCompany).filter(DbCompany.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db.query(DbJob).filter(DbJob.company_id == company_id).all()


@router.post("/", response_model=CompanySchema)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    db_company = DbCompany(**company.dict(), owner_id=current_user.id)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.get("/get_companies", response_model=List[CompanySchema])
def get_all_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(DbCompany).offset(skip).limit(limit).all()
