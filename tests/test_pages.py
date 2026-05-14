from datetime import UTC, date, datetime
import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Analysis, Briefing, Item, Source
from app.seed import seed_default_personas
from app.services.personas import get_persona_by_slug


def add_sample_analysis(db_session: Session) -> int:
    seed_default_personas(db_session)
    persona = get_persona_by_slug(db_session, "indie-maker")
    assert persona is not None
    source = Source(type="rss", name="Example", url="https://example.com/feed.xml", config={})
    item = Item(
        source=source,
        external_id="demo-1",
        title="AI Agent Builder Launches",
        url="https://example.com/agent",
        content="A new AI agent builder launched.",
        author="Example",
        published_at=datetime(2026, 5, 12, 8, 0, tzinfo=UTC),
        metadata_json={},
    )
    analysis = Analysis(
        item=item,
        persona=persona,
        score=8.7,
        summary="一个新的 Agent 构建器发布。",
        why_it_matters="它说明 Agent 工具仍在升温。",
        opportunities=["为垂直行业做更简单的 Agent 模板"],
        risks=["通用平台竞争强"],
        tags=["agent", "tool"],
        model="test-model",
    )
    db_session.add_all([source, item, analysis])
    db_session.commit()
    return analysis.id


def test_homepage_lists_personas(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.get("/")

    assert response.status_code == 200
    assert "独立开发者" in response.text
    assert "选择你的情报视角" in response.text
    assert "今日高价值信号" in response.text


def test_homepage_shows_role_signal_preview(client: TestClient, db_session: Session) -> None:
    add_sample_analysis(db_session)

    response = client.get("/")

    assert response.status_code == 200
    assert "最近更新：1 条" in response.text
    assert "AI Agent Builder Launches" in response.text
    assert "一个新的 Agent 构建器发布。" in response.text


def test_persona_page_lists_analysis(client: TestClient, db_session: Session) -> None:
    add_sample_analysis(db_session)

    response = client.get("/personas/indie-maker")

    assert response.status_code == 200
    assert "AI Agent Builder Launches" in response.text
    assert "Agent 工具仍在升温" in response.text


def test_subscribe_from_persona_page(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.post(
        "/personas/indie-maker/subscribe",
        data={"email": "USER@example.com", "keywords": "agent, video"},
    )

    assert response.status_code == 200
    assert "订阅成功" in response.text


def test_item_detail_page(client: TestClient, db_session: Session) -> None:
    analysis_id = add_sample_analysis(db_session)

    response = client.get(f"/items/{analysis_id}")

    assert response.status_code == 200
    assert "可做机会" in response.text
    assert "为垂直行业做更简单的 Agent 模板" in response.text


def test_item_detail_not_found(client: TestClient) -> None:
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Analysis not found"}


def test_pwa_manifest(client: TestClient) -> None:
    response = client.get("/static/manifest.webmanifest")

    assert response.status_code == 200
    payload = json.loads(response.text)
    assert payload["name"] == "见微"


def test_service_worker(client: TestClient) -> None:
    response = client.get("/static/service-worker.js")

    assert response.status_code == 200
    assert "jianwei-static-v1" in response.text


def test_archive_page(client: TestClient, db_session: Session) -> None:
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

    response = client.get("/archive")

    assert response.status_code == 200
    assert "历史归档" in response.text
    assert "独立开发者今日情报" in response.text
