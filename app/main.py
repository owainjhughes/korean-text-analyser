from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dictionary import get_word_grade, list_entries
from app.tokenizer import tokenize

app = FastAPI(title="Korean Difficulty Classifier")

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", context={})


@app.get("/analyze", response_class=HTMLResponse)
async def analyze_get(request: Request):
    return templates.TemplateResponse(
        request, "analyze.html", context={"result": [], "submitted_text": ""}
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_post(request: Request, text: str = Form("")):
    words = tokenize(text)
    # sequential calls — KRDict rate-limits burst concurrent requests
    result = []
    for word in words:
        grade = await get_word_grade(word)
        result.append({"word": word, "grade": grade})
    return templates.TemplateResponse(
        request, "analyze.html", context={"result": result, "submitted_text": text}
    )


@app.get("/dictionary", response_class=HTMLResponse)
async def dictionary(request: Request, page: int = 1):
    rows, page, total_pages = list_entries(page=page)
    return templates.TemplateResponse(
        request,
        "dictionary.html",
        context={"rows": rows, "page": page, "total_pages": total_pages},
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(request, "about.html", context={})


@app.get("/health")
async def health():
    return {"status": "ok"}
