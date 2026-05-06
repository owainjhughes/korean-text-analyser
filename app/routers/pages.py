from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.analysis import analyze_text
from app.auth import get_optional_user, require_user_html
from app.dictionary import list_entries

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: dict = Depends(require_user_html)):
    return templates.TemplateResponse(request, "index.html", context={"user": user})


@router.get("/analyze", response_class=HTMLResponse)
async def analyze_get(request: Request, user: dict = Depends(require_user_html)):
    return templates.TemplateResponse(
        request,
        "analyze.html",
        context={"analysis": None, "submitted_text": "", "user": user},
    )


@router.post("/analyze", response_class=HTMLResponse)
async def analyze_post(
    request: Request,
    text: str = Form(""),
    user: dict = Depends(require_user_html),
):
    analysis = await analyze_text(text)
    return templates.TemplateResponse(
        request,
        "analyze.html",
        context={"analysis": analysis, "submitted_text": text, "user": user},
    )


@router.get("/dictionary", response_class=HTMLResponse)
async def dictionary(
    request: Request,
    page: int = 1,
    user: dict = Depends(require_user_html),
):
    rows, page, total_pages = list_entries(page=page)
    return templates.TemplateResponse(
        request,
        "dictionary.html",
        context={"rows": rows, "page": page, "total_pages": total_pages, "user": user},
    )


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse(request, "about.html", context={"user": user})
