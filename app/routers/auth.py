from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.auth import AuthRequest, AuthResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("", response_model=AuthResponse)
async def authenticate(payload: AuthRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT username, role, password_hash FROM users WHERE username = :username"),
        {"username": payload.username},
    )
    user = result.mappings().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] == "user":
        return AuthResponse(user=UserOut(username=user["username"], role=user["role"]))

    # admin requires password
    if not payload.password:
        return AuthResponse(requiresPassword=True)

    # Verify password with pgcrypto
    verify = await db.execute(
        text("SELECT (password_hash = crypt(:password, password_hash)) AS valid FROM users WHERE username = :username"),
        {"password": payload.password, "username": payload.username},
    )
    verify_row = verify.mappings().first()
    if not verify_row or not verify_row["valid"]:
        raise HTTPException(status_code=401, detail="Invalid password")

    return AuthResponse(user=UserOut(username=user["username"], role=user["role"]))
