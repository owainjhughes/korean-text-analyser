from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password, require_user_html, verify_password
from app.db import get_db
from app.models import User

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


async def _load(db: AsyncSession, user_id: int) -> User:
    return (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one()


def _render(
    request: Request,
    user: dict,
    db_user: User,
    *,
    error: Optional[str] = None,
    notice: Optional[str] = None,
    status_code: int = 200,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "profile.html",
        context={
            "user": user,
            "db_user": db_user,
            "error": error,
            "notice": notice,
        },
        status_code=status_code,
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_get(
    request: Request,
    user: dict = Depends(require_user_html),
    db: AsyncSession = Depends(get_db),
):
    db_user = await _load(db, user["user_id"])
    return _render(request, user, db_user)


@router.post("/profile", response_class=HTMLResponse)
async def profile_post(
    request: Request,
    username: str = Form(...),
    current_password: str = Form(""),
    new_password: str = Form(""),
    confirm_new_password: str = Form(""),
    user: dict = Depends(require_user_html),
    db: AsyncSession = Depends(get_db),
):
    db_user = await _load(db, user["user_id"])

    new_username = username.strip()
    if not new_username or len(new_username) > 50:
        return _render(request, user, db_user,
                       error="Username must be between 1 and 50 characters.",
                       status_code=400)

    changed = False

    if new_username != db_user.username:
        db_user.username = new_username
        changed = True

    if new_password:
        if not current_password or not verify_password(current_password, db_user.password_hash):
            return _render(request, user, db_user,
                           error="Current password is incorrect.",
                           status_code=400)
        if new_password != confirm_new_password:
            return _render(request, user, db_user,
                           error="New passwords do not match.",
                           status_code=400)
        if len(new_password) < 8:
            return _render(request, user, db_user,
                           error="New password must be at least 8 characters.",
                           status_code=400)
        db_user.password_hash = hash_password(new_password)
        changed = True

    if not changed:
        return _render(request, user, db_user, notice="Nothing to update.")

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return _render(request, user, db_user,
                       error="That username is already taken.",
                       status_code=409)
    await db.refresh(db_user)
    return _render(request, user, db_user, notice="Profile updated.")
