import hmac
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"


def _configured_users() -> dict[str, str]:
    users = {}
    for entry in settings.AUTH_USERS.split(","):
        username, separator, password = entry.strip().partition(":")
        if username and separator and password:
            users[username.strip().lower()] = password
    return users


def authenticate_user(username: str, password: str) -> str | None:
    expected_password = _configured_users().get(username.strip().lower())
    if expected_password and hmac.compare_digest(password, expected_password):
        return username.strip().lower()
    return None


def create_access_token(username: str) -> str:
    if not settings.AUTH_JWT_SECRET:
        raise RuntimeError("AUTH_JWT_SECRET must be configured before login is enabled.")
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.AUTH_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expires_at}, settings.AUTH_JWT_SECRET, algorithm=ALGORITHM)


def require_authenticated_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    try:
        payload = jwt.decode(credentials.credentials, settings.AUTH_JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or username not in _configured_users():
            raise ValueError("Unknown user")
        return username
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session.")
