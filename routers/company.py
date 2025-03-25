from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from models.user import DbUser
from models.company import DbCompany
from models.job import DbJob
from schemas.company import CompanyCreate, Company as CompanySchema
from schemas.job import Job as JobSchema
from utils.token_utils import get_current_user
import shutil
import os
from uuid import uuid4

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.get("/", response_model=List[CompanySchema])
async def read_companies(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None, description="Filter by company type"),
    location: Optional[str] = Query(
        None, description="Filter by company location"),
    db: Session = Depends(get_db)
):
    query = db.query(DbCompany)

    if type:
        query = query.filter(DbCompany.company_type.ilike(f"%{type}%"))
    if location:
        query = query.filter(DbCompany.company_location.ilike(f"%{location}%"))

    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/get_companies", response_model=List[CompanySchema])
def get_all_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(DbCompany).offset(skip).limit(limit).all()


@router.get("/{company_id}", response_model=CompanySchema)
async def read_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    company = db.query(DbCompany).filter(DbCompany.id == company_id).first()
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




# Add this at the top of the file with other imports
AVATAR_DIR = "static/company_avatars"
ALLOWED_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg"}

def is_valid_image(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

@router.post("/register_company", response_model=CompanySchema)
async def create_company(
    company_name: str = Form(...),
    company_description: str = Form(None),
    remote: str = Form(None),
    company_location: str = Form(None),
    company_type: str = Form(None),
    industry_type: str = Form(None),
    business_nature: str = Form(None),
    employee_count: str = Form(None),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    # Check if company with same name already exists
    existing_company = db.query(DbCompany).filter(
        DbCompany.company_name == company_name
    ).first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Company already exists",
                "error": "A company with this name is already registered",
                "solution": "Please use a different company name or contact the existing company owner"
            }
        )

    # Handle avatar upload
    avatar_url = None
    if avatar:
        if not is_valid_image(avatar.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Invalid file type",
                    "error": "Only SVG, PNG, and JPEG files are allowed",
                    "solution": "Please upload a valid image file"
                }
            )
        
        # Create unique filename
        file_ext = get_file_extension(avatar.filename)
        filename = f"{uuid4()}{file_ext}"
        filepath = os.path.join(AVATAR_DIR, filename)
        
        # Ensure directory exists
        os.makedirs(AVATAR_DIR, exist_ok=True)
        
        # Save the file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        
        # Generate URL for the avatar
        avatar_url = f"/static/company_avatars/{filename}"

    try:
        # Create company with form data
        db_company = DbCompany(
            company_name=company_name,
            company_description=company_description,
            remote=remote,
            company_location=company_location,
            company_type=company_type,
            industry_type=industry_type,
            business_nature=business_nature,
            employee_count=employee_count,
            company_avatar=avatar_url,
            owner_id=current_user.id
        )
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to create company",
                "error": str(e),
                "solution": "Please try again or contact support if the issue persists"
            }
        )
