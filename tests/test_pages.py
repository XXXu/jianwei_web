from datetime import UTC, date, datetime, time, timedelta
import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Analysis, Briefing, Item, Source
from app.seed import seed_default_personas
from app.services.intelligence import DISPLAY_TIMEZONE, get_display_today
from app.services.personas import get_persona_by_slug


def today_at(hour: int, minute: int = 0) -> datetime:
    local_value = datetime.combine(get_display_today(), time(hour, minute), tzinfo=DISPLAY_TIMEZONE)
    return local_value.astimezone(UTC)


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
        published_at=today_at(8),
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


def add_analysis(
    db_session: Session,
    *,
    external_id: str,
    title: str,
    score: float,
    published_at: datetime,
) -> int:
    seed_default_personas(db_session)
    persona = get_persona_by_slug(db_session, "indie-maker")
    assert persona is not None
    source = Source(type="rss", name=f"Example {external_id}", url="https://example.com/feed.xml", config={})
    item = Item(
        source=source,
        external_id=external_id,
        title=title,
        url=f"https://example.com/{external_id}",
        content=f"{title} content",
        author="Example",
        published_at=published_at,
        metadata_json={},
    )
    analysis = Analysis(
        item=item,
        persona=persona,
        score=score,
        summary=f"{title} 摘要",
        why_it_matters=f"{title} 重要原因",
        opportunities=[f"{title} 的可做机会"],
        risks=[f"{title} 的风险提醒"],
        tags=["demo"],
        model="test-model",
    )
    db_session.add_all([source, item, analysis])
    db_session.commit()
    return analysis.id


def test_homepage_lists_personas(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.get("/")

    assert response.status_code == 200
    assert "见微知著" in response.text
    assert "值得独立开发者关注的信号" in response.text


def test_homepage_shows_role_signal_preview(client: TestClient, db_session: Session) -> None:
    add_sample_analysis(db_session)

    response = client.get("/")

    assert response.status_code == 200
    assert "AI Agent Builder Launches" in response.text
    assert 'href="#signal-' in response.text
    assert 'id="signal-' in response.text
    assert 'target="_blank"' in response.text
    assert "原文" not in response.text
    assert "一个新的 Agent 构建器发布。" in response.text
    assert "关键信号" in response.text
    assert f"/days/{get_display_today().isoformat()}" in response.text
    assert "查看今日全部" in response.text


def test_homepage_uses_top_10_for_latest_day(client: TestClient, db_session: Session) -> None:
    add_analysis(
        db_session,
        external_id="older-high",
        title="昨天的高分内容",
        score=9.9,
        published_at=today_at(8) - timedelta(days=1),
    )
    for index in range(12):
        add_analysis(
            db_session,
            external_id=f"today-{index}",
            title=f"今日内容 {index}",
            score=8.0 + index / 10,
            published_at=today_at(8, index),
        )

    response = client.get("/")

    assert response.status_code == 200
    assert "从 12 条内容中，筛出 10 条值得独立开发者关注的信号" in response.text
    assert "昨天的高分内容" not in response.text
    assert "今日内容 11" in response.text
    assert "今日内容 0" not in response.text
    assert "查看今日全部 12 条" in response.text
    assert 'class="digest-footer-link"' in response.text
    assert "#signal-" in response.text


def test_day_page_shows_all_analyses_for_date(client: TestClient, db_session: Session) -> None:
    add_analysis(
        db_session,
        external_id="older-high",
        title="昨天的高分内容",
        score=9.9,
        published_at=today_at(8) - timedelta(days=1),
    )
    add_analysis(
        db_session,
        external_id="today-low",
        title="今日低分内容",
        score=7.1,
        published_at=today_at(8),
    )
    add_analysis(
        db_session,
        external_id="today-high",
        title="今日高分内容",
        score=9.2,
        published_at=today_at(9),
    )

    response = client.get(f"/days/{get_display_today().isoformat()}")

    assert response.status_code == 200
    assert f"{get_display_today().isoformat()} 全部信号" in response.text
    assert "共 2 条" in response.text
    assert "今日高分内容" in response.text
    assert "今日低分内容" in response.text
    assert "昨天的高分内容" not in response.text
    assert "历史归档" not in response.text
    assert 'class="all-signal-score"' not in response.text
    assert 'class="score-badge large' in response.text
    assert 'id="signal-' in response.text
    assert "可做机会" in response.text
    assert "风险提醒" in response.text
    assert "标签：" in response.text
    assert response.text.index("今日高分内容") < response.text.index("今日低分内容")


def test_day_page_invalid_date(client: TestClient) -> None:
    response = client.get("/days/not-a-date")

    assert response.status_code == 404


def test_homepage_groups_days_by_china_timezone(client: TestClient, db_session: Session) -> None:
    add_analysis(
        db_session,
        external_id="utc-evening",
        title="北京时间 15 号的内容",
        score=8.8,
        published_at=today_at(2),
    )

    response = client.get("/")

    assert response.status_code == 200
    assert f"见微知著：{get_display_today().isoformat()}" in response.text
    assert f"/days/{get_display_today().isoformat()}" in response.text
    assert "北京时间 15 号的内容" in response.text


def test_pages_display_published_time_in_china_timezone(client: TestClient, db_session: Session) -> None:
    add_analysis(
        db_session,
        external_id="utc-midnight",
        title="北京时间展示测试",
        score=8.8,
        published_at=today_at(8),
    )

    expected_time = f"{get_display_today().strftime('%m月%d日')} 08:00"

    home_response = client.get("/")
    day_response = client.get(f"/days/{get_display_today().isoformat()}")

    assert home_response.status_code == 200
    assert day_response.status_code == 200
    assert expected_time in home_response.text
    assert expected_time in day_response.text


def test_homepage_falls_back_to_latest_data_date(client: TestClient, db_session: Session) -> None:
    latest_data_date = get_display_today() - timedelta(days=1)
    local_value = datetime.combine(latest_data_date, time(8), tzinfo=DISPLAY_TIMEZONE)
    add_analysis(
        db_session,
        external_id="latest-day",
        title="最近一天的数据",
        score=8.6,
        published_at=local_value.astimezone(UTC),
    )

    response = client.get("/")

    assert response.status_code == 200
    assert f"见微知著：{latest_data_date.isoformat()}" in response.text
    assert f"/days/{latest_data_date.isoformat()}" in response.text
    assert "最近一天的数据" in response.text
    assert "从 1 条内容中，筛出 1 条值得独立开发者关注的信号" in response.text


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
    assert "jianwei-static-v3" in response.text


def test_stylesheet_uses_cache_busting_version(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert '/static/css/app.css?v=20260515' in response.text


def test_digest_layout_uses_horizon_reading_width() -> None:
    stylesheet = Path("app/static/css/app.css").read_text(encoding="utf-8")

    assert "--reading-width: 832px;" in stylesheet
    assert "max-width: var(--reading-width);" in stylesheet


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
