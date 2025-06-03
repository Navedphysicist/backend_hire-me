from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from db.database import get_db
from typing import Optional
from jose import jwt, JWTError,ExpiredSignatureError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from core.config import settings
from models.user import DbUser
from schemas.token import TokenData
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # or your login route

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.

    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(
            timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get the current user from the JWT token.

    Args:
        token (str): JWT token (injected via Depends)
        db (Session): DB session (injected via Depends)

    Returns:
        DbUser: Authenticated user

    Raises:
        HTTPException: If token is invalid or user is not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired, Please login again",
        headers={"WWW-Authenticate": "Bearer"},
    )
    except JWTError:
        raise credentials_exception

    user = db.query(DbUser).filter(DbUser.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user