from sqlalchemy.orm import Session

from app.models import Persona, Subscription


def create_or_update_subscription(
    session: Session,
    email: str,
    persona: Persona,
    keywords: list[str],
) -> Subscription:
    normalized_email = email.strip().lower()
    subscription = (
        session.query(Subscription)
        .filter(Subscription.email == normalized_email, Subscription.persona_id == persona.id)
        .one_or_none()
    )
    if subscription is None:
        subscription = Subscription(
            email=normalized_email,
            persona=persona,
            keywords=keywords,
            status="active",
        )
        session.add(subscription)
    else:
        subscription.keywords = keywords
        subscription.status = "active"

    session.commit()
    session.refresh(subscription)
    return subscription
