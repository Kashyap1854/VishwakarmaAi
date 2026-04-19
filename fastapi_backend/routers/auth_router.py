"""
routers/auth_router.py — /api/auth  endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from models import UserRegister, UserLogin, TokenResponse, UserOut, MessageResponse
from database import users_col
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ── POST /api/auth/register ───────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: UserRegister):
    # Check duplicate
    existing = await users_col().find_one({"email": body.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user_doc = {
        "name":        body.name,
        "email":       body.email,
        "password":    hash_password(body.password),
        "created_at":  datetime.utcnow(),
    }
    result = await users_col().insert_one(user_doc)

    token = create_access_token({"sub": body.email})
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=str(result.inserted_id),
            name=body.name,
            email=body.email,
            created_at=user_doc["created_at"],
        ),
    )


# ── POST /api/auth/login ──────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    user = await users_col().find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": user["email"]})
    return TokenResponse(
        access_token=token,
        user=UserOut(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
        ),
    )


# ── GET /api/auth/me ──────────────────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    return UserOut(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user["created_at"],
    )


# ── DELETE /api/auth/account ──────────────────────────────────────────────────
@router.delete("/account", response_model=MessageResponse)
async def delete_account(current_user: dict = Depends(get_current_user)):
    await users_col().delete_one({"email": current_user["email"]})
    return MessageResponse(message="Account deleted successfully")
