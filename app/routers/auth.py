from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.auth import AuthRequest, AuthResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def get_current_user(request: Request) -> dict:
    """Extract user info from Authentik headers."""
    email = request.headers.get("X-authentik-email")
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "uid": request.headers.get("X-authentik-uid"),
        "username": request.headers.get("X-authentik-username"),
        "name": request.headers.get("X-authentik-name"),
        "email": email,
        "groups": request.headers.get("X-authentik-groups", "").split("|"),
    }

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


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user