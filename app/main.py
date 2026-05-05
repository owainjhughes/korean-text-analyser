from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.auth import get_optional_user
from app.dictionary import get_word_grade, list_entries
from app.exceptions import RedirectToLogin
from app.tokenizer import tokenize

app = FastAPI(title="Korean Difficulty Classifier")


@app.exception_handler(RedirectToLogin)
async def _redirect_to_login(request: Request, exc: RedirectToLogin) -> RedirectResponse:
    return RedirectResponse(url=f"/login?next={quote(exc.next_path)}", status_code=303)

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/public", StaticFiles(directory=str(BASE_DIR / "templates" / "public")), name="public")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse(request, "index.html", context={"user": user})


@app.get("/analyze", response_class=HTMLResponse)
async def analyze_get(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse(
        request, "analyze.html", context={"result": [], "submitted_text": "", "user": user}
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_post(request: Request, text: str = Form(""), user: Optional[dict] = Depends(get_optional_user)):
    words = tokenize(text)
    # sequential calls — KRDict rate-limits burst concurrent requests
    result = []
    for word in words:
        grade = await get_word_grade(word)
        result.append({"word": word, "grade": grade})
    return templates.TemplateResponse(
        request, "analyze.html", context={"result": result, "submitted_text": text, "user": user}
    )


@app.get("/dictionary", response_class=HTMLResponse)
async def dictionary(request: Request, page: int = 1, user: Optional[dict] = Depends(get_optional_user)):
    rows, page, total_pages = list_entries(page=page)
    return templates.TemplateResponse(
        request,
        "dictionary.html",
        context={"rows": rows, "page": page, "total_pages": total_pages, "user": user},
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, user: Optional[dict] = Depends(get_optional_user)):
    return templates.TemplateResponse(request, "about.html", context={"user": user})


@app.get("/health")
async def health():
    return {"status": "ok"}
