from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import (
    BriefingListOut,
    BriefingOut,
    IntelligenceItemOut,
    PersonaFeedOut,
    PersonaListOut,
    PersonaOut,
    SubscriptionIn,
    SubscriptionOut,
)
from app.services.intelligence import list_persona_analyses, list_published_briefings
from app.services.personas import get_persona_by_slug, list_enabled_personas
from app.services.subscriptions import create_or_update_subscription

router = APIRouter(prefix="/api")


@router.get("/personas", response_model=PersonaListOut)
def list_personas(session: Session = Depends(get_session)) -> PersonaListOut:
    personas = list_enabled_personas(session)
    return PersonaListOut(
        items=[
            PersonaOut(
                id=persona.id,
                slug=persona.slug,
                name=persona.name,
                description=persona.description,
            )
            for persona in personas
        ]
    )


@router.get("/personas/{slug}/feed", response_model=PersonaFeedOut)
def get_persona_feed(slug: str, session: Session = Depends(get_session)) -> PersonaFeedOut:
    persona = get_persona_by_slug(session, slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    analyses = list_persona_analyses(session, persona.id)
    return PersonaFeedOut(
        persona=PersonaOut(
            id=persona.id,
            slug=persona.slug,
            name=persona.name,
            description=persona.description,
        ),
        items=[
            IntelligenceItemOut(
                id=analysis.id,
                title=analysis.item.title,
                url=analysis.item.url,
                score=analysis.score,
                summary=analysis.summary,
                why_it_matters=analysis.why_it_matters,
                opportunities=analysis.opportunities,
                risks=analysis.risks,
                tags=analysis.tags,
                published_at=analysis.item.published_at,
            )
            for analysis in analyses
        ],
    )


@router.post("/subscriptions", response_model=SubscriptionOut)
def create_subscription(
    subscription_in: SubscriptionIn,
    session: Session = Depends(get_session),
) -> SubscriptionOut:
    persona = get_persona_by_slug(session, subscription_in.persona_slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    subscription = create_or_update_subscription(
        session,
        email=str(subscription_in.email),
        persona=persona,
        keywords=subscription_in.keywords,
    )
    return SubscriptionOut(
        email=subscription.email,
        persona_slug=persona.slug,
        status=subscription.status,
    )


@router.get("/briefings", response_model=BriefingListOut)
def list_briefings(session: Session = Depends(get_session)) -> BriefingListOut:
    briefings = list_published_briefings(session)
    return BriefingListOut(
        items=[
            BriefingOut(
                id=briefing.id,
                persona_slug=briefing.persona.slug,
                persona_name=briefing.persona.name,
                date=briefing.date,
                title=briefing.title,
                summary=briefing.summary,
            )
            for briefing in briefings
        ]
    )
