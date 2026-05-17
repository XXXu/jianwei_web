import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Analysis, Item, Run, Source
from app.seed import seed_default_personas
from app.worker.import_artifact import import_artifact_file, import_artifact_path


def write_artifact(path: Path) -> None:
    payload = {
        "source": {
            "type": "rss",
            "name": "Example Feed",
            "url": "https://example.com/feed.xml",
        },
        "item": {
            "external_id": "rss:demo-1",
            "title": "AI Video Agent Released",
            "url": "https://example.com/ai-video-agent",
            "content": "A new AI video agent was released.",
            "author": "Example",
            "published_at": "2026-05-12T08:00:00+00:00",
            "metadata": {"source_score": 88},
        },
        "analysis": {
            "persona_slug": "indie-maker",
            "score": 8.8,
            "summary": "AI 视频 Agent 是一个值得关注的产品信号。",
            "why_it_matters": "视频自动化工具仍在升温。",
            "opportunities": ["面向房产中介做短视频自动生成器"],
            "risks": ["版权和素材授权需要谨慎"],
            "tags": ["video", "agent"],
            "model": "deepseek-test",
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_import_artifact_file(tmp_path: Path, db_session: Session) -> None:
    seed_default_personas(db_session)
    artifact_path = tmp_path / "artifact.json"
    write_artifact(artifact_path)

    result = import_artifact_file(db_session, artifact_path)

    assert result.fetched_count == 1
    assert result.analyzed_count == 1
    assert db_session.query(Source).count() == 1
    assert db_session.query(Item).count() == 1
    assert db_session.query(Analysis).count() == 1
    assert db_session.query(Analysis).one().last_imported_at is not None
    assert db_session.query(Run).count() == 1


def test_import_artifact_file_is_idempotent(tmp_path: Path, db_session: Session) -> None:
    seed_default_personas(db_session)
    artifact_path = tmp_path / "artifact.json"
    write_artifact(artifact_path)

    import_artifact_file(db_session, artifact_path)
    import_artifact_file(db_session, artifact_path)

    assert db_session.query(Source).count() == 1
    assert db_session.query(Item).count() == 1
    assert db_session.query(Analysis).count() == 1
    assert db_session.query(Run).count() == 2


def test_import_artifact_path_uses_explicit_imported_at(
    tmp_path: Path, db_session: Session
) -> None:
    seed_default_personas(db_session)
    artifact_path = tmp_path / "artifact.json"
    write_artifact(artifact_path)
    imported_at = datetime(2026, 5, 17, tzinfo=UTC)

    import_artifact_path(db_session, tmp_path, imported_at=imported_at)

    assert db_session.query(Analysis).one().last_imported_at == imported_at.replace(tzinfo=None)


def test_import_artifact_path_imports_directory(tmp_path: Path, db_session: Session) -> None:
    seed_default_personas(db_session)
    artifact_path = tmp_path / "artifact.json"
    write_artifact(artifact_path)

    result = import_artifact_path(db_session, tmp_path)

    assert result.fetched_count == 1
    assert result.analyzed_count == 1
    assert db_session.query(Source).count() == 1
    assert db_session.query(Item).count() == 1
    assert db_session.query(Analysis).count() == 1
