from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    clear_auth_cookie,
    hash_password,
    issue_token,
    set_auth_cookie,
    verify_password,
)
from app.db import get_db
from app.models import User

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _safe_next(next_path: Optional[str]) -> str:
    """Only allow same-site relative paths so /login?next=... can't open-redirect."""
    if not next_path:
        return "/"
    if not next_path.startswith("/") or next_path.startswith("//"):
        return "/"
    return next_path


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, next: str = "/", error: Optional[str] = None):
    return templates.TemplateResponse(
        request,
        "login.html",
        context={"next": _safe_next(next), "error": error, "user": None},
    )


@router.post("/login")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: AsyncSession = Depends(get_db),
):
    target = _safe_next(next)
    user = (
        await db.execute(select(User).where(User.email == email.strip().lower()))
    ).scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            context={"next": target, "error": "Invalid email or password.", "user": None},
            status_code=401,
        )
    response = RedirectResponse(url=target, status_code=303)
    set_auth_cookie(response, issue_token(user.id, user.email))
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request, next: str = "/", error: Optional[str] = None):
    return templates.TemplateResponse(
        request,
        "register.html",
        context={"next": _safe_next(next), "error": error, "user": None, "form": {}},
    )


@router.post("/register")
async def register_post(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    next: str = Form("/"),
    db: AsyncSession = Depends(get_db),
):
    target = _safe_next(next)
    email_norm = email.strip().lower()
    username_norm = username.strip()
    form_state = {"email": email_norm, "username": username_norm}

    def render_error(msg: str, status_code: int = 400) -> Response:
        return templates.TemplateResponse(
            request,
            "register.html",
            context={"next": target, "error": msg, "user": None, "form": form_state},
            status_code=status_code,
        )

    if password != confirm_password:
        return render_error("Passwords do not match.")
    if len(password) < 8:
        return render_error("Password must be at least 8 characters.")
    if not username_norm or len(username_norm) > 50:
        return render_error("Username must be between 1 and 50 characters.")
    if len(email_norm) > 255:
        return render_error("Email is too long.")

    user = User(
        email=email_norm,
        username=username_norm,
        password_hash=hash_password(password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return render_error("That email or username is already taken.", status_code=409)
    await db.refresh(user)

    response = RedirectResponse(url=target, status_code=303)
    set_auth_cookie(response, issue_token(user.id, user.email))
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    clear_auth_cookie(response)
    return response
