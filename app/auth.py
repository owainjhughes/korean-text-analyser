from typing import Optional

from fastapi import Cookie, Header, HTTPException, status
from jose import JWTError, jwt

from app.config import settings

ALGORITHM = "HS256"


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
    # user_id is a json number — jose decodes it as int already, but guard anyway
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
