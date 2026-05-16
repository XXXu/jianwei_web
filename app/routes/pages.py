from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import Analysis
from app.services.intelligence import (
    count_persona_analyses_for_date,
    format_display_datetime,
    get_display_today,
    get_latest_persona_analysis_date,
    list_persona_analyses_for_date,
    list_persona_analyses,
    list_published_briefings,
)
from app.services.personas import get_persona_by_slug
from app.services.subscriptions import create_or_update_subscription

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["display_datetime"] = format_display_datetime


@router.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", _build_home_context(request, session))


def _build_home_context(request: Request, session: Session) -> dict:
    persona = get_persona_by_slug(session, "indie-maker")
    if persona:
        today = get_display_today()
        summary_date = (
            today
            if count_persona_analyses_for_date(session, persona.id, today) > 0
            else get_latest_persona_analysis_date(session, persona.id)
        )
    else:
        summary_date = None
    analyses = (
        list_persona_analyses_for_date(session, persona.id, summary_date, limit=10)
        if persona and summary_date
        else []
    )
    total_count = (
        count_persona_analyses_for_date(session, persona.id, summary_date)
        if persona and summary_date
        else 0
    )
    return {
        "request": request,
        "persona": persona,
        "analyses": analyses,
        "top_analyses": analyses,
        "selected_count": len(analyses),
        "total_count": total_count,
        "summary_date": summary_date,
    }


@router.get("/days/{day}", response_class=HTMLResponse)
def day_page(
    day: str,
    request: Request,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    try:
        target_date = date.fromisoformat(day)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Day not found") from exc

    persona = get_persona_by_slug(session, "indie-maker")
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    analyses = list_persona_analyses_for_date(session, persona.id, target_date)
    return templates.TemplateResponse(
        request,
        "day.html",
        {
            "request": request,
            "persona": persona,
            "analyses": analyses,
            "summary_date": target_date,
            "total_count": len(analyses),
        },
    )


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
