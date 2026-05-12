from sqlalchemy.orm import Session

from app.models import Persona


def list_enabled_personas(session: Session) -> list[Persona]:
    return (
        session.query(Persona)
        .filter(Persona.enabled.is_(True))
        .order_by(Persona.id.asc())
        .all()
    )


def get_persona_by_slug(session: Session, slug: str) -> Persona | None:
    return (
        session.query(Persona)
        .filter(Persona.slug == slug, Persona.enabled.is_(True))
        .one_or_none()
    )
