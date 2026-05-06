from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.exceptions import RedirectToLogin
from app.routers import auth as auth_router
from app.routers import pages as pages_router
from app.routers import profile as profile_router

app = FastAPI(title="Korean Difficulty Classifier")

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/public",
    StaticFiles(directory=str(BASE_DIR / "templates" / "public")),
    name="public",
)


@app.exception_handler(RedirectToLogin)
async def _redirect_to_login(request: Request, exc: RedirectToLogin) -> RedirectResponse:
    return RedirectResponse(url=f"/login?next={quote(exc.next_path)}", status_code=303)


app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(pages_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
