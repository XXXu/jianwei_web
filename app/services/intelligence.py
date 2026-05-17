from datetime import UTC, date, datetime, time, timedelta, timezone

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import ColumnElement
from sqlalchemy import func

from app.models import Analysis, Briefing, Item, Source

DISPLAY_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")


def _day_bounds(target_date: date) -> tuple[datetime, datetime]:
    start_local = datetime.combine(target_date, time.min, tzinfo=DISPLAY_TIMEZONE)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


def _imported_at_expr() -> ColumnElement[datetime]:
    return func.coalesce(Analysis.last_imported_at, Analysis.created_at)


def to_display_date(value: datetime) -> date:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(DISPLAY_TIMEZONE).date()


def to_display_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(DISPLAY_TIMEZONE)


def format_display_datetime(value: datetime, fmt: str = "%m月%d日 %H:%M") -> str:
    return to_display_datetime(value).strftime(fmt)


def get_display_today() -> date:
    return datetime.now(DISPLAY_TIMEZONE).date()


def list_persona_analyses(session: Session, persona_id: int, limit: int = 20) -> list[Analysis]:
    return (
        session.query(Analysis)
        .options(joinedload(Analysis.item).joinedload(Item.source))
        .filter(Analysis.persona_id == persona_id)
        .order_by(Analysis.score.desc(), Analysis.created_at.desc())
        .limit(limit)
        .all()
    )


def get_latest_persona_analysis_date(session: Session, persona_id: int) -> date | None:
    imported_at = _imported_at_expr()
    latest_imported_at = (
        session.query(imported_at)
        .select_from(Analysis)
        .filter(Analysis.persona_id == persona_id)
        .order_by(imported_at.desc())
        .scalar()
    )
    return to_display_date(latest_imported_at) if latest_imported_at else None


def list_persona_analyses_for_date(
    session: Session,
    persona_id: int,
    target_date: date,
    limit: int | None = None,
) -> list[Analysis]:
    start, end = _day_bounds(target_date)
    imported_at = _imported_at_expr()
    query = (
        session.query(Analysis)
        .join(Analysis.item)
        .options(joinedload(Analysis.item).joinedload(Item.source))
        .filter(Analysis.persona_id == persona_id)
        .filter(imported_at >= start)
        .filter(imported_at < end)
        .order_by(Analysis.score.desc(), Analysis.created_at.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def count_persona_analyses(session: Session, persona_id: int) -> int:
    return session.query(Analysis).filter(Analysis.persona_id == persona_id).count()


def count_persona_analyses_for_date(
    session: Session,
    persona_id: int,
    target_date: date,
) -> int:
    start, end = _day_bounds(target_date)
    imported_at = _imported_at_expr()
    return (
        session.query(Analysis)
        .filter(Analysis.persona_id == persona_id)
        .filter(imported_at >= start)
        .filter(imported_at < end)
        .count()
    )


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
