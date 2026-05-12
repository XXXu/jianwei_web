from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import Analysis
from app.services.intelligence import list_persona_analyses, list_published_briefings
from app.services.personas import get_persona_by_slug, list_enabled_personas
from app.services.subscriptions import create_or_update_subscription

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    personas = list_enabled_personas(session)
    return templates.TemplateResponse(request, "index.html", {"personas": personas})


@router.get("/personas/{slug}", response_class=HTMLResponse)
def persona_page(
    slug: str,
    request: Request,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    persona = get_persona_by_slug(session, slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    analyses = list_persona_analyses(session, persona.id)
    return templates.TemplateResponse(
        request,
        "persona.html",
        {"persona": persona, "analyses": analyses, "subscription_message": None},
    )


@router.post("/personas/{slug}/subscribe", response_class=HTMLResponse)
def subscribe_from_persona_page(
    slug: str,
    request: Request,
    email: str = Form(...),
    keywords: str = Form(""),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    persona = get_persona_by_slug(session, slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    create_or_update_subscription(
        session,
        email=email,
        persona=persona,
        keywords=[part.strip() for part in keywords.split(",") if part.strip()],
    )
    analyses = list_persona_analyses(session, persona.id)
    return templates.TemplateResponse(
        request,
        "persona.html",
        {"persona": persona, "analyses": analyses, "subscription_message": "订阅成功"},
    )


@router.get("/items/{analysis_id}", response_class=HTMLResponse)
def item_detail(
    analysis_id: int,
    request: Request,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    analysis = (
        session.query(Analysis)
        .options(joinedload(Analysis.item), joinedload(Analysis.persona))
        .filter(Analysis.id == analysis_id)
        .one_or_none()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return templates.TemplateResponse(request, "item_detail.html", {"analysis": analysis})


@router.get("/archive", response_class=HTMLResponse)
def archive(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    briefings = list_published_briefings(session)
    return templates.TemplateResponse(request, "archive.html", {"briefings": briefings})
