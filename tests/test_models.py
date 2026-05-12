from datetime import UTC, date, datetime

from app.db import Base, make_engine, make_session_factory
from app.models import Analysis, Briefing, Item, Persona, Run, Source, Subscription


def test_create_core_records_in_sqlite_memory() -> None:
    engine = make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = make_session_factory(engine)

    with SessionLocal() as session:
        persona = Persona(
            slug="indie-maker",
            name="独立开发者",
            description="寻找可执行的 AI 产品机会",
            prompt_profile="关注 MVP、获客渠道、收费点和竞品。",
        )
        source = Source(
            type="rss",
            name="Example Feed",
            url="https://example.com/feed.xml",
            config={"category": "ai"},
        )
        item = Item(
            source=source,
            external_id="rss:1",
            title="Example AI Product",
            url="https://example.com/product",
            content="A new AI product was released.",
            author="Example",
            published_at=datetime(2026, 5, 12, 8, 0, tzinfo=UTC),
            metadata_json={"score": 10},
        )
        analysis = Analysis(
            item=item,
            persona=persona,
            score=8.5,
            summary="一个值得关注的 AI 产品信号。",
            why_it_matters="它说明垂直工具仍有需求。",
            opportunities=["做一个更垂直的轻量版本"],
            risks=["同质化竞争"],
            tags=["ai-product", "opportunity"],
            model="test-model",
        )
        briefing = Briefing(
            persona=persona,
            date=date(2026, 5, 12),
            title="独立开发者今日情报",
            summary="今日有 1 条重要机会。",
            content="完整日报内容",
            status="published",
        )
        subscription = Subscription(
            email="user@example.com",
            persona=persona,
            keywords=["agent", "video"],
            status="active",
        )
        run = Run(
            job_type="import_artifact",
            persona=persona,
            status="success",
            fetched_count=1,
            analyzed_count=1,
        )

        session.add_all([persona, source, item, analysis, briefing, subscription, run])
        session.commit()

        assert session.query(Persona).count() == 1
        assert session.query(Source).count() == 1
        assert session.query(Item).count() == 1
        assert session.query(Analysis).count() == 1
        assert session.query(Briefing).count() == 1
        assert session.query(Subscription).count() == 1
        assert session.query(Run).count() == 1
