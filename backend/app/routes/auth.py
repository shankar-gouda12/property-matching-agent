from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import authenticate_user, create_access_token, require_authenticated_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=1024)


@router.post("/login")
def login(request: LoginRequest):
    if not settings.AUTH_JWT_SECRET or not settings.AUTH_USERS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured on the server.",
        )
    username = authenticate_user(request.username, request.password)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    return {"access_token": create_access_token(username), "token_type": "bearer", "username": username}


@router.get("/me")
def get_current_user(username: str = Depends(require_authenticated_user)):
    return {"username": username}
