from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.analysis import AnalysisResult, analyze_text
from app.auth import require_user_html
from app.dictionary import list_entries

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# TOPIK grade → JLPT-family hex (ground rule 3 in doc/ui.md).
_SEGMENT_ORDER = ("초급", "중급", "고급", "unknown")
_SEGMENT_COLORS = {
    "초급": "#16A34A",
    "중급": "#EA580C",
    "고급": "#2563EB",
    "unknown": "#9CA3AF",
}
_SEGMENT_LABELS = {
    "초급": "초급",
    "중급": "중급",
    "고급": "고급",
    "unknown": "Unknown",
}


def _pie_segments(analysis: AnalysisResult) -> list[dict]:
    total = analysis.counts["total"]
    if not total:
        return []
    segments: list[dict] = []
    offset = 25.0  # SVG donut starts at 12 o'clock when offset=25
    for key in _SEGMENT_ORDER:
        count = analysis.counts[key]
        if not count:
            continue
        pct = count / total * 100
        segments.append(
            {
                "key": key,
                "label": _SEGMENT_LABELS[key],
                "color": _SEGMENT_COLORS[key],
                "pct": round(pct, 1),
                "dasharray": f"{pct:.4f} {100 - pct:.4f}",
                "dashoffset": f"{offset:.4f}",
            }
        )
        offset = (offset - pct) % 100
    return segments


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: dict = Depends(require_user_html)):
    return templates.TemplateResponse(request, "index.html", context={"user": user})


@router.get("/analyze", response_class=HTMLResponse)
async def analyze_get(request: Request, user: dict = Depends(require_user_html)):
    return templates.TemplateResponse(
        request,
        "analyze.html",
        context={
            "analysis": None,
            "submitted_text": "",
            "pie_segments": [],
            "user": user,
        },
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
        context={
            "analysis": analysis,
            "submitted_text": text,
            "pie_segments": _pie_segments(analysis),
            "user": user,
        },
    )


@router.get("/dictionary", response_class=HTMLResponse)
async def dictionary(
    request: Request,
    page: int = 1,
    user: dict = Depends(require_user_html),
):
    rows, page, total_pages, total_count = list_entries(page=page)
    return templates.TemplateResponse(
        request,
        "dictionary.html",
        context={
            "rows": rows,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "user": user,
        },
    )
