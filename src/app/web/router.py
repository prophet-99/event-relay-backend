from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter()
jinjaTemplate = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/home")


@router.get("/home", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request) -> HTMLResponse:
    return jinjaTemplate.TemplateResponse(
        request=request, name="home.html", context={"title": "Fast API | Schedules"}
    )
