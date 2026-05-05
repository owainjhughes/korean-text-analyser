from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Cookie, Header, HTTPException, Request, Response, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions import RedirectToLogin

ALGORITHM = "HS256"
COOKIE_NAME = "auth_token"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def issue_token(user_id: int, email: str) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(user_id),
        "user_id": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.jwt_ttl_days)).timestamp()),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm=ALGORITHM)


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
        max_age=settings.jwt_ttl_days * 86400,
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")


def _extract_token(
    authorization: Optional[str],
    auth_token: Optional[str],
) -> str:
    """pull jwt from bearer header, falling back to the auth_token cookie."""
    if authorization:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid authorization header format",
            )
        return parts[1]
    if auth_token:
        return auth_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="missing authorization token",
    )


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    auth_token: Optional[str] = Cookie(default=None),
) -> dict:
    """fastapi dependency — returns decoded claims or raises 401."""
    token = _extract_token(authorization, auth_token)
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )
    user_id = claims.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token claims",
        )
    return {
        "user_id": int(user_id),
        "email": claims.get("email", ""),
    }


def get_optional_user(
    authorization: Optional[str] = Header(default=None),
    auth_token: Optional[str] = Cookie(default=None),
) -> Optional[dict]:
    """like get_current_user but returns None instead of raising on missing/invalid token."""
    try:
        token = _extract_token(authorization, auth_token)
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        user_id = claims.get("user_id")
        if user_id is None:
            return None
        return {"user_id": int(user_id), "email": claims.get("email", "")}
    except (HTTPException, JWTError):
        return None


def require_user_html(request: Request) -> dict:
    """For HTML routes: redirect to /login when unauthenticated instead of returning 401.

    Wired up via the RedirectToLogin exception handler in app.main.
    """
    user = get_optional_user(
        authorization=request.headers.get("authorization"),
        auth_token=request.cookies.get(COOKIE_NAME),
    )
    if user is None:
        next_path = request.url.path
        if request.url.query:
            next_path = f"{next_path}?{request.url.query}"
        raise RedirectToLogin(next_path=next_path)
    return user
