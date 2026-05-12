from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Briefing, Subscription
from app.seed import seed_default_personas
from app.services.personas import get_persona_by_slug


def test_list_personas(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.get("/api/personas")

    assert response.status_code == 200
    payload = response.json()
    assert [item["slug"] for item in payload["items"]] == [
        "indie-maker",
        "cross-border-operator",
        "funding-observer",
        "enterprise-ai-lead",
    ]


def test_get_persona_feed_empty_state(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.get("/api/personas/indie-maker/feed")

    assert response.status_code == 200
    payload = response.json()
    assert payload["persona"]["slug"] == "indie-maker"
    assert payload["items"] == []


def test_get_persona_feed_unknown_persona(client: TestClient) -> None:
    response = client.get("/api/personas/unknown/feed")

    assert response.status_code == 404
    assert response.json() == {"detail": "Persona not found"}


def test_create_subscription(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.post(
        "/api/subscriptions",
        json={
            "email": " USER@Example.COM ",
            "persona_slug": "indie-maker",
            "keywords": ["agent", "video"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "email": "user@example.com",
        "persona_slug": "indie-maker",
        "status": "active",
    }
    subscription = db_session.query(Subscription).one()
    assert subscription.email == "user@example.com"
    assert subscription.keywords == ["agent", "video"]
    assert subscription.status == "active"


def test_create_subscription_reuses_existing_record(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_default_personas(db_session)

    first_response = client.post(
        "/api/subscriptions",
        json={
            "email": "user@example.com",
            "persona_slug": "indie-maker",
            "keywords": ["agent"],
        },
    )
    second_response = client.post(
        "/api/subscriptions",
        json={
            "email": "USER@example.com",
            "persona_slug": "indie-maker",
            "keywords": ["video"],
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert db_session.query(Subscription).count() == 1
    subscription = db_session.query(Subscription).one()
    assert subscription.keywords == ["video"]
    assert subscription.status == "active"


def test_create_subscription_rejects_unknown_persona(client: TestClient) -> None:
    response = client.post(
        "/api/subscriptions",
        json={
            "email": "user@example.com",
            "persona_slug": "unknown",
            "keywords": [],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Persona not found"}


def test_list_briefings(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)
    persona = get_persona_by_slug(db_session, "indie-maker")
    assert persona is not None
    db_session.add(
        Briefing(
            persona=persona,
            date=date(2026, 5, 12),
            title="独立开发者今日情报",
            summary="今日有 1 条重要机会。",
            content="完整日报内容",
            status="published",
        )
    )
    db_session.commit()

    response = client.get("/api/briefings")

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["title"] == "独立开发者今日情报"
    assert payload["items"][0]["persona_slug"] == "indie-maker"
