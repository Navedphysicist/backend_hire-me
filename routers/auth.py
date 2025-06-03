from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from db.database import get_db
from models.user import DbUser
from schemas.user import UserCreate,VerifyEmail
from schemas.token import Token
from utils.password_utils import get_password_hash, verify_password
from utils.email_utils import generate_otp, send_verification_email
from utils.token_utils import create_access_token
from core.config import settings
from typing import Dict


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Temporary storage for unverified users
unverified_users: Dict[str, dict] = {}

# OTP expiration time in minutes
OTP_EXPIRY_MINUTES = 5

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(DbUser).filter(DbUser.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def is_otp_expired(timestamp: datetime) -> bool:
    """Check if OTP has expired based on the timestamp"""
    now = datetime.now(timezone.utc)
    return (now - timestamp).total_seconds() > (OTP_EXPIRY_MINUTES * 60)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists in verified users
    if db.query(DbUser).filter(DbUser.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists in verified users
    if db.query(DbUser).filter(DbUser.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if email exists in unverified users
    if user.email in unverified_users:
        user_data = unverified_users[user.email]
        # If OTP is expired, allow new registration
        if is_otp_expired(user_data["timestamp"]):
            unverified_users.pop(user.email)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered but not verified. Please check your email for verification code. If you haven't received the code or it has expired, please register again."
            )

    # Generate OTP
    otp = generate_otp()

    # Store user data temporarily with timestamp
    unverified_users[user.email] = {
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "verification_code": otp,
        "timestamp": datetime.now(timezone.utc)
    }

    # Send verification email
    email_sent = await send_verification_email(user.email, otp)
    if not email_sent:
        # Remove from unverified users if email sending fails
        unverified_users.pop(user.email, None)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try registering again."
        )

    return {
        "message": "Signup successful! Please check your email for verification code. If you don't receive the code or it expires, please register again."
    }


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(verify_data: VerifyEmail, db: Session = Depends(get_db)):
    # Check if email exists in unverified users
    if verify_data.email not in unverified_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already verified. Please register again if you haven't completed the verification process."
        )

    user_data = unverified_users[verify_data.email]

    # Check if OTP has expired
    if is_otp_expired(user_data["timestamp"]):
        unverified_users.pop(verify_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please register again to receive a new verification code."
        )

    if user_data["verification_code"] != verify_data.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    # Create verified user in database
    db_user = DbUser(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Remove from unverified users after successful verification
    unverified_users.pop(verify_data.email)

    return {"message": "Email verified successfully"}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email
    }