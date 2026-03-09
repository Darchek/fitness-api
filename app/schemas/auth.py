from pydantic import BaseModel
from typing import Optional


class AuthRequest(BaseModel):
    username: str
    password: Optional[str] = None


class UserOut(BaseModel):
    username: str
    role: str


class AuthResponse(BaseModel):
    user: Optional[UserOut] = None
    requiresPassword: Optional[bool] = None
