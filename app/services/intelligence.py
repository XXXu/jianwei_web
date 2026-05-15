from sqlalchemy.orm import Session, joinedload

from app.models import Analysis, Briefing, Item, Source


def list_persona_analyses(session: Session, persona_id: int, limit: int = 20) -> list[Analysis]:
    return (
        session.query(Analysis)
        .options(joinedload(Analysis.item).joinedload(Item.source))
        .filter(Analysis.persona_id == persona_id)
        .order_by(Analysis.score.desc(), Analysis.created_at.desc())
        .limit(limit)
        .all()
    )


def count_persona_analyses(session: Session, persona_id: int) -> int:
    return session.query(Analysis).filter(Analysis.persona_id == persona_id).count()


def count_items(session: Session) -> int:
    return session.query(Item).count()


def count_sources(session: Session) -> int:
    return session.query(Source).count()


def list_top_analyses(session: Session, limit: int = 3) -> list[Analysis]:
    return (
        session.query(Analysis)
        .options(joinedload(Analysis.item).joinedload(Item.source), joinedload(Analysis.persona))
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
