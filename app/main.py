from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dictionary import get_word_grade
from app.tokenizer import tokenize

app = FastAPI(title="Korean Difficulty Classifier")

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", context={"result": [], "submitted_text": ""}
    )


@app.post("/", response_class=HTMLResponse)
async def index_post(request: Request, text: str = Form("")):
    words = tokenize(text)
    # sequential calls — KRDict rate-limits burst concurrent requests
    result = []
    for word in words:
        grade = await get_word_grade(word)
        result.append({"word": word, "grade": grade})
    return templates.TemplateResponse(
        request, "index.html", context={"result": result, "submitted_text": text}
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(request, "about.html")


@app.get("/health")
async def health():
    return {"status": "ok"}
