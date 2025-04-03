from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str
    username : str
    email : str


class TokenData(BaseModel):
    username: Optional[str] = None
