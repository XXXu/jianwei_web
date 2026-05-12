from sqlalchemy.orm import Session, joinedload

from app.models import Analysis, Briefing


def list_persona_analyses(session: Session, persona_id: int, limit: int = 20) -> list[Analysis]:
    return (
        session.query(Analysis)
        .options(joinedload(Analysis.item))
        .filter(Analysis.persona_id == persona_id)
        .order_by(Analysis.score.desc(), Analysis.created_at.desc())
        .limit(limit)
        .all()
    )


def list_published_briefings(session: Session, limit: int = 30) -> list[Briefing]:
    return (
        session.query(Briefing)
        .options(joinedload(Briefing.persona))
        .filter(Briefing.status == "published")
        .order_by(Briefing.date.desc(), Briefing.created_at.desc())
        .limit(limit)
        .all()
    )
