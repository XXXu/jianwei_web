# 见微 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建见微第一版可运行网站：支持角色选择、情报列表、情报详情、历史归档、邮箱订阅、SQLite 持久化、JSON API、Jinja2 页面、PWA 基础能力和 worker 导入链路。

**Architecture:** 见微作为独立 FastAPI 单体网站项目运行，Horizon 保持独立情报引擎项目。第一版通过 `app/integrations/horizon_adapter.py` 定义适配层，把 Horizon 或示例 artifact 转换为见微自己的数据库记录；Web 请求只读数据库，不现场抓取或调用 AI。

**Tech Stack:** Python 3.11+, FastAPI, Jinja2, SQLAlchemy 2.x, SQLite, Alembic, pytest, HTTPX TestClient, Uvicorn, Docker Compose, Nginx, PWA manifest/service worker.

---

## Scope

本计划实现第一版产品骨架和可演示数据链路。它不实现真实支付、登录、完整后台管理、React 前端、PostgreSQL、复杂全文搜索，也不把 Web 代码写入 Horizon 项目。

## File Structure

```text
jianwei_web/
  pyproject.toml
  .env.example
  alembic.ini
  README.md
  README_zh.md
  app/
    __init__.py
    main.py
    settings.py
    db.py
    models.py
    schemas.py
    seed.py
    services/
      __init__.py
      personas.py
      intelligence.py
      subscriptions.py
      runs.py
    routes/
      __init__.py
      pages.py
      api.py
    integrations/
      __init__.py
      horizon_adapter.py
    worker/
      __init__.py
      import_artifact.py
    templates/
      base.html
      index.html
      persona.html
      item_detail.html
      archive.html
    static/
      css/app.css
      manifest.webmanifest
      service-worker.js
  alembic/
    env.py
    versions/
      20260512_0001_initial_schema.py
  tests/
    conftest.py
    test_health.py
    test_models.py
    test_api.py
    test_pages.py
    test_horizon_adapter.py
    test_worker_import.py
  deploy/
    nginx.conf
  docker-compose.yml
  Dockerfile
```

Boundary rules:

- `app/models.py` contains persistence models only.
- `app/schemas.py` contains API response/request schemas only.
- `app/services/*` contains business reads/writes.
- `app/routes/*` contains HTTP route glue only.
- `app/integrations/horizon_adapter.py` is the only place that knows how Horizon artifacts map into Jianwei records.
- `app/worker/*` is the only place that performs background import/generation actions.
- Templates display data passed by services; templates do not query the database.

---

### Task 1: Project Scaffold And Health Check

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/settings.py`
- Create: `app/main.py`
- Create: `tests/conftest.py`
- Create: `tests/test_health.py`

- [ ] **Step 1: Create failing health-check test**

Create `tests/test_health.py`:

```python
from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "jianwei"}
```

- [ ] **Step 2: Create test fixture**

Create `tests/conftest.py`:

```python
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
```

- [ ] **Step 3: Run test to verify it fails**

Run:

```bash
pytest tests/test_health.py -q
```

Expected: FAIL because `app.main` does not exist.

- [ ] **Step 4: Add package dependencies**

Create `pyproject.toml`:

```toml
[project]
name = "jianwei-web"
version = "0.1.0"
description = "Role-based AI intelligence website powered by Horizon"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "alembic>=1.13.0",
    "email-validator>=2.1.0",
    "fastapi>=0.115.0",
    "jinja2>=3.1.0",
    "pydantic-settings>=2.6.0",
    "python-dotenv>=1.0.0",
    "python-multipart>=0.0.9",
    "sqlalchemy>=2.0.0",
    "uvicorn[standard]>=0.30.0",
]

[project.optional-dependencies]
dev = [
    "httpx>=0.27.0",
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.ruff]
line-length = 100
target-version = "py311"
```

Create `.env.example`:

```text
APP_ENV=development
DATABASE_URL=sqlite:///./data/jianwei.db
HORIZON_PATH=../Horizon
```

- [ ] **Step 5: Add settings and app factory**

Create `app/__init__.py`:

```python
"""Jianwei web application package."""
```

Create `app/settings.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./data/jianwei.db"
    horizon_path: str = "../Horizon"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Create `app/main.py`:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Jianwei", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "jianwei"}

    return app


app = create_app()
```

- [ ] **Step 6: Run test to verify it passes**

Run:

```bash
pytest tests/test_health.py -q
```

Expected: PASS.

- [ ] **Step 7: Run formatter/linter check**

Run:

```bash
ruff check app tests
```

Expected: PASS.

- [ ] **Step 8: Commit scaffold**

```bash
git add pyproject.toml .env.example app tests
git commit -m "chore: scaffold FastAPI app"
```

---

### Task 2: Database Models And Session Layer

**Files:**
- Create: `app/db.py`
- Create: `app/models.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/20260512_0001_initial_schema.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write database model tests**

Create `tests/test_models.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_models.py -q
```

Expected: FAIL because `app.db` and `app.models` do not exist.

- [ ] **Step 3: Implement database session helpers**

Create `app/db.py`:

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.settings import get_settings


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


engine = make_engine(get_settings().database_url)
SessionLocal = make_session_factory(engine)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
```

- [ ] **Step 4: Implement SQLAlchemy models**

Create `app/models.py`:

```python
from datetime import UTC, date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    prompt_profile: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    analyses: Mapped[list["Analysis"]] = relationship(back_populates="persona")
    briefings: Mapped[list["Briefing"]] = relationship(back_populates="persona")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="persona")
    runs: Mapped[list["Run"]] = relationship(back_populates="persona")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(160))
    url: Mapped[str] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    items: Mapped[list["Item"]] = relationship(back_populates="source")


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_items_source_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(240))
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, index=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    source: Mapped[Source] = relationship(back_populates="items")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="item")


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (UniqueConstraint("item_id", "persona_id", name="uq_analysis_item_persona"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(Text)
    why_it_matters: Mapped[str] = mapped_column(Text)
    opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    model: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    item: Mapped[Item] = relationship(back_populates="analyses")
    persona: Mapped[Persona] = relationship(back_populates="analyses")


class Briefing(Base):
    __tablename__ = "briefings"
    __table_args__ = (UniqueConstraint("persona_id", "date", name="uq_briefing_persona_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    title: Mapped[str] = mapped_column(String(180))
    summary: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    persona: Mapped[Persona] = relationship(back_populates="briefings")


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("email", "persona_id", name="uq_subscription_email_persona"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(240), index=True)
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), index=True)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    persona: Mapped[Persona] = relationship(back_populates="subscriptions")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_type: Mapped[str] = mapped_column(String(80), index=True)
    persona_id: Mapped[Optional[int]] = mapped_column(ForeignKey("personas.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    analyzed_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    persona: Mapped[Optional[Persona]] = relationship(back_populates="runs")
```

- [ ] **Step 5: Add Alembic configuration**

Create `alembic.ini`:

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = sqlite:///./data/jianwei.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

Create `alembic/env.py`:

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db import Base
from app import models  # noqa: F401
from app.settings import get_settings

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Create `alembic/versions/20260512_0001_initial_schema.py`:

```python
"""initial schema

Revision ID: 20260512_0001
Revises:
Create Date: 2026-05-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260512_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "personas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("prompt_profile", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_personas_slug", "personas", ["slug"])

    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sources_type", "sources", ["type"])

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("external_id", sa.String(length=240), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=160), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_id", "external_id", name="uq_items_source_external"),
    )
    op.create_index("ix_items_source_id", "items", ["source_id"])
    op.create_index("ix_items_published_at", "items", ["published_at"])

    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("items.id"), nullable=False),
        sa.Column("persona_id", sa.Integer(), sa.ForeignKey("personas.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("why_it_matters", sa.Text(), nullable=False),
        sa.Column("opportunities", sa.JSON(), nullable=False),
        sa.Column("risks", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("item_id", "persona_id", name="uq_analysis_item_persona"),
    )
    op.create_index("ix_analyses_item_id", "analyses", ["item_id"])
    op.create_index("ix_analyses_persona_id", "analyses", ["persona_id"])

    op.create_table(
        "briefings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("persona_id", sa.Integer(), sa.ForeignKey("personas.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("persona_id", "date", name="uq_briefing_persona_date"),
    )
    op.create_index("ix_briefings_persona_id", "briefings", ["persona_id"])
    op.create_index("ix_briefings_date", "briefings", ["date"])
    op.create_index("ix_briefings_status", "briefings", ["status"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=240), nullable=False),
        sa.Column("persona_id", sa.Integer(), sa.ForeignKey("personas.id"), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", "persona_id", name="uq_subscription_email_persona"),
    )
    op.create_index("ix_subscriptions_email", "subscriptions", ["email"])
    op.create_index("ix_subscriptions_persona_id", "subscriptions", ["persona_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])

    op.create_table(
        "runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("persona_id", sa.Integer(), sa.ForeignKey("personas.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("fetched_count", sa.Integer(), nullable=False),
        sa.Column("analyzed_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
    )
    op.create_index("ix_runs_job_type", "runs", ["job_type"])
    op.create_index("ix_runs_status", "runs", ["status"])


def downgrade() -> None:
    op.drop_table("runs")
    op.drop_table("subscriptions")
    op.drop_table("briefings")
    op.drop_table("analyses")
    op.drop_table("items")
    op.drop_table("sources")
    op.drop_table("personas")
```

- [ ] **Step 6: Run model tests**

Run:

```bash
pytest tests/test_models.py -q
```

Expected: PASS.

- [ ] **Step 7: Run all tests and lint**

Run:

```bash
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 8: Commit database foundation**

```bash
git add app/db.py app/models.py alembic.ini alembic tests/test_models.py
git commit -m "feat: add database schema"
```

---

### Task 3: Seed Personas And Core Read Services

**Files:**
- Create: `app/seed.py`
- Create: `app/services/__init__.py`
- Create: `app/services/personas.py`
- Create: `app/services/intelligence.py`
- Modify: `tests/conftest.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Extend test fixture with isolated database**

Replace `tests/conftest.py` with:

```python
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.db import Base, get_session
from app.main import create_app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        yield session


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
```

- [ ] **Step 2: Write API tests for personas and empty feed**

Create `tests/test_api.py`:

```python
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.seed import seed_default_personas


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
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```bash
pytest tests/test_api.py -q
```

Expected: FAIL because services and API routes are missing.

- [ ] **Step 4: Add seed data and persona service**

Create `app/services/__init__.py`:

```python
"""Business service layer for Jianwei."""
```

Create `app/seed.py`:

```python
from sqlalchemy.orm import Session

from app.models import Persona


DEFAULT_PERSONAS = [
    {
        "slug": "indie-maker",
        "name": "独立开发者 / AI 产品创业者",
        "description": "寻找适合小团队或个人执行的 AI 产品机会。",
        "prompt_profile": "关注 MVP、获客渠道、收费点、竞品、独立开发可行性。",
    },
    {
        "slug": "cross-border-operator",
        "name": "跨境卖家 / 出海产品人",
        "description": "关注海外增长工具、平台变化、营销自动化和出海机会。",
        "prompt_profile": "关注海外需求、平台政策、广告营销、Shopify、TikTok 和工具机会。",
    },
    {
        "slug": "funding-observer",
        "name": "投资 / 融资观察者",
        "description": "关注 AI 赛道融资、公司动态、趋势信号和竞争格局。",
        "prompt_profile": "关注融资金额、投资机构、赛道变化、公司壁垒和风险。",
    },
    {
        "slug": "enterprise-ai-lead",
        "name": "企业 AI 应用负责人",
        "description": "关注企业 AI 落地、效率工具、安全合规和采购风险。",
        "prompt_profile": "关注落地场景、团队效率、合规风险、安全风险和采购判断。",
    },
]


def seed_default_personas(session: Session) -> None:
    for item in DEFAULT_PERSONAS:
        existing = session.query(Persona).filter(Persona.slug == item["slug"]).one_or_none()
        if existing:
            continue
        session.add(Persona(**item))
    session.commit()
```

Create `app/services/personas.py`:

```python
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
```

- [ ] **Step 5: Add intelligence service for empty feed**

Create `app/services/intelligence.py`:

```python
from sqlalchemy.orm import Session, joinedload

from app.models import Analysis


def list_persona_analyses(session: Session, persona_id: int, limit: int = 20) -> list[Analysis]:
    return (
        session.query(Analysis)
        .options(joinedload(Analysis.item))
        .filter(Analysis.persona_id == persona_id)
        .order_by(Analysis.score.desc(), Analysis.created_at.desc())
        .limit(limit)
        .all()
    )
```

- [ ] **Step 6: Add API schemas and routes**

Create `app/schemas.py`:

```python
from datetime import datetime

from pydantic import BaseModel, EmailStr


class PersonaOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str


class PersonaListOut(BaseModel):
    items: list[PersonaOut]


class IntelligenceItemOut(BaseModel):
    id: int
    title: str
    url: str
    score: float
    summary: str
    why_it_matters: str
    opportunities: list[str]
    risks: list[str]
    tags: list[str]
    published_at: datetime


class PersonaFeedOut(BaseModel):
    persona: PersonaOut
    items: list[IntelligenceItemOut]


class SubscriptionIn(BaseModel):
    email: EmailStr
    persona_slug: str
    keywords: list[str] = []


class SubscriptionOut(BaseModel):
    email: EmailStr
    persona_slug: str
    status: str
```

Create `app/routes/__init__.py`:

```python
"""HTTP routes for Jianwei."""
```

Create `app/routes/api.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import IntelligenceItemOut, PersonaFeedOut, PersonaListOut, PersonaOut
from app.services.intelligence import list_persona_analyses
from app.services.personas import get_persona_by_slug, list_enabled_personas

router = APIRouter(prefix="/api")


@router.get("/personas", response_model=PersonaListOut)
def list_personas(session: Session = Depends(get_session)) -> PersonaListOut:
    personas = list_enabled_personas(session)
    return PersonaListOut(
        items=[
            PersonaOut(
                id=persona.id,
                slug=persona.slug,
                name=persona.name,
                description=persona.description,
            )
            for persona in personas
        ]
    )


@router.get("/personas/{slug}/feed", response_model=PersonaFeedOut)
def get_persona_feed(slug: str, session: Session = Depends(get_session)) -> PersonaFeedOut:
    persona = get_persona_by_slug(session, slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    analyses = list_persona_analyses(session, persona.id)
    return PersonaFeedOut(
        persona=PersonaOut(
            id=persona.id,
            slug=persona.slug,
            name=persona.name,
            description=persona.description,
        ),
        items=[
            IntelligenceItemOut(
                id=analysis.id,
                title=analysis.item.title,
                url=analysis.item.url,
                score=analysis.score,
                summary=analysis.summary,
                why_it_matters=analysis.why_it_matters,
                opportunities=analysis.opportunities,
                risks=analysis.risks,
                tags=analysis.tags,
                published_at=analysis.item.published_at,
            )
            for analysis in analyses
        ],
    )
```

Modify `app/main.py`:

```python
from fastapi import FastAPI

from app.routes.api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Jianwei", version="0.1.0")
    app.include_router(api_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "jianwei"}

    return app


app = create_app()
```

- [ ] **Step 7: Run API tests**

Run:

```bash
pytest tests/test_api.py -q
```

Expected: PASS.

- [ ] **Step 8: Run regression tests and lint**

Run:

```bash
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 9: Commit persona API foundation**

```bash
git add app tests
git commit -m "feat: add persona feed API"
```

---

### Task 4: Subscription API

**Files:**
- Create: `app/services/subscriptions.py`
- Modify: `app/routes/api.py`
- Modify: `tests/test_api.py`

- [ ] **Step 1: Add subscription tests**

Append to `tests/test_api.py`:

```python
def test_create_subscription(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.post(
        "/api/subscriptions",
        json={
            "email": "reader@example.com",
            "persona_slug": "indie-maker",
            "keywords": ["agent", "video"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "email": "reader@example.com",
        "persona_slug": "indie-maker",
        "status": "active",
    }


def test_create_subscription_reuses_existing_record(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)
    payload = {
        "email": "reader@example.com",
        "persona_slug": "indie-maker",
        "keywords": ["agent"],
    }

    first = client.post("/api/subscriptions", json=payload)
    second = client.post("/api/subscriptions", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["status"] == "active"


def test_create_subscription_rejects_unknown_persona(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.post(
        "/api/subscriptions",
        json={"email": "reader@example.com", "persona_slug": "missing", "keywords": []},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Persona not found"
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_api.py -q
```

Expected: FAIL because `POST /api/subscriptions` is missing.

- [ ] **Step 3: Implement subscription service**

Create `app/services/subscriptions.py`:

```python
from sqlalchemy.orm import Session

from app.models import Persona, Subscription


def create_or_update_subscription(
    session: Session,
    *,
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
```

- [ ] **Step 4: Add subscription API route**

Modify `app/routes/api.py` imports:

```python
from app.schemas import (
    IntelligenceItemOut,
    PersonaFeedOut,
    PersonaListOut,
    PersonaOut,
    SubscriptionIn,
    SubscriptionOut,
)
from app.services.subscriptions import create_or_update_subscription
```

Append to `app/routes/api.py`:

```python
@router.post("/subscriptions", response_model=SubscriptionOut)
def create_subscription(
    payload: SubscriptionIn,
    session: Session = Depends(get_session),
) -> SubscriptionOut:
    persona = get_persona_by_slug(session, payload.persona_slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    subscription = create_or_update_subscription(
        session,
        email=str(payload.email),
        persona=persona,
        keywords=payload.keywords,
    )
    return SubscriptionOut(
        email=subscription.email,
        persona_slug=persona.slug,
        status=subscription.status,
    )
```

- [ ] **Step 5: Run tests**

Run:

```bash
pytest tests/test_api.py -q
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 6: Commit subscription API**

```bash
git add app tests
git commit -m "feat: add subscription API"
```

---

### Task 5: Server-Rendered Pages

**Files:**
- Create: `app/routes/pages.py`
- Create: `app/templates/base.html`
- Create: `app/templates/index.html`
- Create: `app/templates/persona.html`
- Create: `app/templates/item_detail.html`
- Create: `app/templates/archive.html`
- Create: `app/static/css/app.css`
- Modify: `app/main.py`
- Create: `tests/test_pages.py`

- [ ] **Step 1: Write page route tests**

Create `tests/test_pages.py`:

```python
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Analysis, Item, Source
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
    assert "从信息里看见方向" in response.text


def test_persona_page_lists_analysis(client: TestClient, db_session: Session) -> None:
    add_sample_analysis(db_session)

    response = client.get("/personas/indie-maker")

    assert response.status_code == 200
    assert "AI Agent Builder Launches" in response.text
    assert "Agent 工具仍在升温" in response.text


def test_item_detail_page(client: TestClient, db_session: Session) -> None:
    analysis_id = add_sample_analysis(db_session)

    response = client.get(f"/items/{analysis_id}")

    assert response.status_code == 200
    assert "可做机会" in response.text
    assert "为垂直行业做更简单的 Agent 模板" in response.text


def test_archive_page(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)

    response = client.get("/archive")

    assert response.status_code == 200
    assert "历史归档" in response.text
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_pages.py -q
```

Expected: FAIL because page routes/templates are missing.

- [ ] **Step 3: Add page route handlers**

Create `app/routes/pages.py`:

```python
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import Analysis
from app.schemas import SubscriptionIn
from app.services.intelligence import list_persona_analyses
from app.services.personas import get_persona_by_slug, list_enabled_personas
from app.services.subscriptions import create_or_update_subscription

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"personas": list_enabled_personas(session)},
    )


@router.get("/personas/{slug}", response_class=HTMLResponse)
def persona_page(slug: str, request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    persona = get_persona_by_slug(session, slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")
    analyses = list_persona_analyses(session, persona.id)
    return templates.TemplateResponse(
        request,
        "persona.html",
        {"persona": persona, "analyses": analyses, "subscription_message": None},
    )


@router.post("/personas/{slug}/subscribe", response_class=HTMLResponse)
def subscribe_from_persona_page(
    slug: str,
    request: Request,
    email: str = Form(...),
    keywords: str = Form(""),
    session: Session = Depends(get_session),
) -> HTMLResponse:
    persona = get_persona_by_slug(session, slug)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")
    payload = SubscriptionIn(
        email=email,
        persona_slug=slug,
        keywords=[part.strip() for part in keywords.split(",") if part.strip()],
    )
    create_or_update_subscription(
        session,
        email=str(payload.email),
        persona=persona,
        keywords=payload.keywords,
    )
    analyses = list_persona_analyses(session, persona.id)
    return templates.TemplateResponse(
        request,
        "persona.html",
        {"persona": persona, "analyses": analyses, "subscription_message": "订阅成功"},
    )


@router.get("/items/{analysis_id}", response_class=HTMLResponse)
def item_detail(
    analysis_id: int,
    request: Request,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    analysis = (
        session.query(Analysis)
        .options(joinedload(Analysis.item), joinedload(Analysis.persona))
        .filter(Analysis.id == analysis_id)
        .one_or_none()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return templates.TemplateResponse(request, "item_detail.html", {"analysis": analysis})


@router.get("/archive", response_class=HTMLResponse)
def archive(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    personas = list_enabled_personas(session)
    return templates.TemplateResponse(request, "archive.html", {"personas": personas})


@router.get("/subscribe/success")
def subscribe_success() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)
```

- [ ] **Step 4: Add templates**

Create `app/templates/base.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#111827">
    <title>{% block title %}见微{% endblock %}</title>
    <link rel="manifest" href="/static/manifest.webmanifest">
    <link rel="stylesheet" href="/static/css/app.css">
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="/">见微</a>
      <nav>
        <a href="/archive">历史归档</a>
      </nav>
    </header>
    <main>
      {% block content %}{% endblock %}
    </main>
    <footer class="site-footer">
      <span>从信息里看见方向</span>
    </footer>
    <script>
      if ("serviceWorker" in navigator) {
        navigator.serviceWorker.register("/static/service-worker.js");
      }
    </script>
  </body>
</html>
```

Create `app/templates/index.html`:

```html
{% extends "base.html" %}
{% block title %}见微 - 从信息里看见方向{% endblock %}
{% block content %}
<section class="hero">
  <p class="eyebrow">角色化 AI 情报雷达</p>
  <h1>从信息里看见方向</h1>
  <p>选择你的角色，查看为你重新加工的机会、风险和关键变化。</p>
</section>

<section class="persona-grid" aria-label="角色选择">
  {% for persona in personas %}
    <a class="persona-card" href="/personas/{{ persona.slug }}">
      <h2>{{ persona.name }}</h2>
      <p>{{ persona.description }}</p>
    </a>
  {% endfor %}
</section>
{% endblock %}
```

Create `app/templates/persona.html`:

```html
{% extends "base.html" %}
{% block title %}{{ persona.name }} - 见微{% endblock %}
{% block content %}
<section class="page-heading">
  <p class="eyebrow">今日情报</p>
  <h1>{{ persona.name }}</h1>
  <p>{{ persona.description }}</p>
</section>

<section class="subscription-panel">
  <h2>订阅这个角色</h2>
  {% if subscription_message %}
    <p class="notice">{{ subscription_message }}</p>
  {% endif %}
  <form method="post" action="/personas/{{ persona.slug }}/subscribe">
    <label>
      邮箱
      <input type="email" name="email" required>
    </label>
    <label>
      关键词
      <input type="text" name="keywords">
    </label>
    <button type="submit">订阅</button>
  </form>
</section>

<section class="feed-list">
  {% if analyses %}
    {% for analysis in analyses %}
      <article class="feed-item">
        <div class="score">{{ "%.1f"|format(analysis.score) }}</div>
        <div>
          <h2><a href="/items/{{ analysis.id }}">{{ analysis.item.title }}</a></h2>
          <p>{{ analysis.summary }}</p>
          <p class="muted">{{ analysis.why_it_matters }}</p>
          <div class="tags">
            {% for tag in analysis.tags %}
              <span>{{ tag }}</span>
            {% endfor %}
          </div>
        </div>
      </article>
    {% endfor %}
  {% else %}
    <p class="empty-state">这个角色还没有生成情报。后台任务运行后会显示内容。</p>
  {% endif %}
</section>
{% endblock %}
```

Create `app/templates/item_detail.html`:

```html
{% extends "base.html" %}
{% block title %}{{ analysis.item.title }} - 见微{% endblock %}
{% block content %}
<article class="detail">
  <p class="eyebrow">{{ analysis.persona.name }}</p>
  <h1>{{ analysis.item.title }}</h1>
  <p class="summary">{{ analysis.summary }}</p>

  <section>
    <h2>为什么重要</h2>
    <p>{{ analysis.why_it_matters }}</p>
  </section>

  <section>
    <h2>可做机会</h2>
    <ul>
      {% for opportunity in analysis.opportunities %}
        <li>{{ opportunity }}</li>
      {% endfor %}
    </ul>
  </section>

  <section>
    <h2>风险提醒</h2>
    <ul>
      {% for risk in analysis.risks %}
        <li>{{ risk }}</li>
      {% endfor %}
    </ul>
  </section>

  <p><a href="{{ analysis.item.url }}" rel="noreferrer">查看原始来源</a></p>
</article>
{% endblock %}
```

Create `app/templates/archive.html`:

```html
{% extends "base.html" %}
{% block title %}历史归档 - 见微{% endblock %}
{% block content %}
<section class="page-heading">
  <p class="eyebrow">Archive</p>
  <h1>历史归档</h1>
  <p>后续会按日期和角色展示历史情报。</p>
</section>

<section class="persona-grid">
  {% for persona in personas %}
    <a class="persona-card" href="/personas/{{ persona.slug }}">
      <h2>{{ persona.name }}</h2>
      <p>{{ persona.description }}</p>
    </a>
  {% endfor %}
</section>
{% endblock %}
```

- [ ] **Step 5: Add CSS**

Create `app/static/css/app.css`:

```css
:root {
  color-scheme: light;
  --bg: #f7f8fb;
  --surface: #ffffff;
  --text: #172033;
  --muted: #647084;
  --line: #d9dee8;
  --accent: #0f766e;
  --accent-strong: #115e59;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.6;
}

a {
  color: inherit;
}

.site-header,
.site-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1120px;
  margin: 0 auto;
  padding: 20px;
}

.brand {
  font-weight: 800;
  text-decoration: none;
}

main {
  max-width: 1120px;
  margin: 0 auto;
  padding: 24px 20px 56px;
}

.hero,
.page-heading {
  padding: 48px 0 32px;
}

.hero h1,
.page-heading h1 {
  margin: 0;
  font-size: 44px;
  line-height: 1.15;
}

.eyebrow {
  color: var(--accent);
  font-weight: 700;
}

.persona-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.persona-card,
.subscription-panel,
.feed-item,
.detail {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 20px;
}

.persona-card {
  text-decoration: none;
}

.feed-list {
  display: grid;
  gap: 14px;
  margin-top: 24px;
}

.feed-item {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 16px;
}

.score {
  color: var(--accent-strong);
  font-size: 24px;
  font-weight: 800;
}

.muted,
.empty-state {
  color: var(--muted);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tags span {
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
  font-size: 13px;
  padding: 2px 8px;
}

form {
  display: grid;
  gap: 12px;
  max-width: 520px;
}

label {
  display: grid;
  gap: 6px;
  font-weight: 700;
}

input {
  border: 1px solid var(--line);
  border-radius: 6px;
  font: inherit;
  padding: 10px 12px;
}

button {
  background: var(--accent);
  border: 0;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  padding: 10px 14px;
}

.notice {
  color: var(--accent-strong);
  font-weight: 700;
}

@media (max-width: 640px) {
  .hero h1,
  .page-heading h1 {
    font-size: 34px;
  }

  .feed-item {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 6: Wire routes and static files**

Modify `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.api import router as api_router
from app.routes.pages import router as pages_router


def create_app() -> FastAPI:
    app = FastAPI(title="Jianwei", version="0.1.0")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(api_router)
    app.include_router(pages_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "jianwei"}

    return app


app = create_app()
```

- [ ] **Step 7: Run page tests**

Run:

```bash
pytest tests/test_pages.py -q
```

Expected: PASS.

- [ ] **Step 8: Run all tests and lint**

Run:

```bash
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 9: Commit server-rendered pages**

```bash
git add app tests
git commit -m "feat: add server-rendered pages"
```

---

### Task 6: PWA Assets

**Files:**
- Create: `app/static/manifest.webmanifest`
- Create: `app/static/service-worker.js`
- Modify: `tests/test_pages.py`

- [ ] **Step 1: Add PWA asset tests**

Append to `tests/test_pages.py`:

```python
def test_pwa_manifest(client: TestClient) -> None:
    response = client.get("/static/manifest.webmanifest")

    assert response.status_code == 200
    assert response.json()["name"] == "见微"


def test_service_worker(client: TestClient) -> None:
    response = client.get("/static/service-worker.js")

    assert response.status_code == 200
    assert "jianwei-static-v1" in response.text
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_pages.py::test_pwa_manifest tests/test_pages.py::test_service_worker -q
```

Expected: FAIL because PWA files do not exist.

- [ ] **Step 3: Add manifest**

Create `app/static/manifest.webmanifest`:

```json
{
  "name": "见微",
  "short_name": "见微",
  "description": "从信息里看见方向",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f7f8fb",
  "theme_color": "#111827",
  "icons": []
}
```

- [ ] **Step 4: Add service worker**

Create `app/static/service-worker.js`:

```javascript
const CACHE_NAME = "jianwei-static-v1";
const STATIC_ASSETS = ["/", "/static/css/app.css", "/static/manifest.webmanifest"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
```

- [ ] **Step 5: Run PWA tests**

Run:

```bash
pytest tests/test_pages.py::test_pwa_manifest tests/test_pages.py::test_service_worker -q
```

Expected: PASS.

- [ ] **Step 6: Run all tests and lint**

Run:

```bash
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 7: Commit PWA assets**

```bash
git add app/static tests/test_pages.py
git commit -m "feat: add basic PWA assets"
```

---

### Task 7: Horizon Artifact Adapter

**Files:**
- Create: `app/integrations/__init__.py`
- Create: `app/integrations/horizon_adapter.py`
- Create: `tests/test_horizon_adapter.py`

- [ ] **Step 1: Write adapter tests**

Create `tests/test_horizon_adapter.py`:

```python
from app.integrations.horizon_adapter import HorizonArtifact, parse_horizon_artifact


def test_parse_horizon_artifact() -> None:
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

    artifact = parse_horizon_artifact(payload)

    assert isinstance(artifact, HorizonArtifact)
    assert artifact.source.name == "Example Feed"
    assert artifact.item.external_id == "rss:demo-1"
    assert artifact.analysis.persona_slug == "indie-maker"
    assert artifact.analysis.opportunities == ["面向房产中介做短视频自动生成器"]
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_horizon_adapter.py -q
```

Expected: FAIL because adapter does not exist.

- [ ] **Step 3: Implement adapter dataclasses**

Create `app/integrations/__init__.py`:

```python
"""Integration adapters for external intelligence engines."""
```

Create `app/integrations/horizon_adapter.py`:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class HorizonSourcePayload:
    type: str
    name: str
    url: str
    config: dict[str, Any]


@dataclass(frozen=True)
class HorizonItemPayload:
    external_id: str
    title: str
    url: str
    content: str | None
    author: str | None
    published_at: datetime
    metadata: dict[str, Any]


@dataclass(frozen=True)
class HorizonAnalysisPayload:
    persona_slug: str
    score: float
    summary: str
    why_it_matters: str
    opportunities: list[str]
    risks: list[str]
    tags: list[str]
    model: str


@dataclass(frozen=True)
class HorizonArtifact:
    source: HorizonSourcePayload
    item: HorizonItemPayload
    analysis: HorizonAnalysisPayload


def parse_horizon_artifact(payload: dict[str, Any]) -> HorizonArtifact:
    source = payload["source"]
    item = payload["item"]
    analysis = payload["analysis"]
    return HorizonArtifact(
        source=HorizonSourcePayload(
            type=source["type"],
            name=source["name"],
            url=source["url"],
            config=source.get("config", {}),
        ),
        item=HorizonItemPayload(
            external_id=item["external_id"],
            title=item["title"],
            url=item["url"],
            content=item.get("content"),
            author=item.get("author"),
            published_at=datetime.fromisoformat(item["published_at"]),
            metadata=item.get("metadata", {}),
        ),
        analysis=HorizonAnalysisPayload(
            persona_slug=analysis["persona_slug"],
            score=float(analysis["score"]),
            summary=analysis["summary"],
            why_it_matters=analysis["why_it_matters"],
            opportunities=list(analysis.get("opportunities", [])),
            risks=list(analysis.get("risks", [])),
            tags=list(analysis.get("tags", [])),
            model=analysis["model"],
        ),
    )
```

- [ ] **Step 4: Run adapter tests**

Run:

```bash
pytest tests/test_horizon_adapter.py -q
```

Expected: PASS.

- [ ] **Step 5: Run all tests and lint**

Run:

```bash
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 6: Commit Horizon artifact adapter**

```bash
git add app/integrations tests/test_horizon_adapter.py
git commit -m "feat: add Horizon artifact adapter"
```

---

### Task 8: Worker Artifact Import

**Files:**
- Create: `app/worker/__init__.py`
- Create: `app/worker/import_artifact.py`
- Create: `app/services/runs.py`
- Create: `tests/test_worker_import.py`

- [ ] **Step 1: Write worker import test**

Create `tests/test_worker_import.py`:

```python
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Analysis, Item, Run, Source
from app.seed import seed_default_personas
from app.worker.import_artifact import import_artifact_file


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
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_worker_import.py -q
```

Expected: FAIL because worker import code is missing.

- [ ] **Step 3: Implement run service**

Create `app/services/runs.py`:

```python
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Persona, Run


def create_run(
    session: Session,
    *,
    job_type: str,
    persona: Persona | None,
    status: str,
    fetched_count: int,
    analyzed_count: int,
    error_message: str | None = None,
) -> Run:
    run = Run(
        job_type=job_type,
        persona=persona,
        status=status,
        fetched_count=fetched_count,
        analyzed_count=analyzed_count,
        error_message=error_message,
        finished_at=datetime.now(UTC),
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run
```

- [ ] **Step 4: Implement artifact importer**

Create `app/worker/__init__.py`:

```python
"""Background worker tasks for Jianwei."""
```

Create `app/worker/import_artifact.py`:

```python
import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.integrations.horizon_adapter import HorizonArtifact, parse_horizon_artifact
from app.models import Analysis, Item, Persona, Source
from app.services.runs import create_run


@dataclass(frozen=True)
class ImportResult:
    fetched_count: int
    analyzed_count: int


def import_artifact_file(session: Session, path: Path) -> ImportResult:
    payload = json.loads(path.read_text(encoding="utf-8"))
    artifact = parse_horizon_artifact(payload)
    persona = _get_persona(session, artifact)
    source = _get_or_create_source(session, artifact)
    item = _get_or_create_item(session, artifact, source)
    _get_or_create_analysis(session, artifact, item, persona)
    create_run(
        session,
        job_type="import_artifact",
        persona=persona,
        status="success",
        fetched_count=1,
        analyzed_count=1,
    )
    return ImportResult(fetched_count=1, analyzed_count=1)


def _get_persona(session: Session, artifact: HorizonArtifact) -> Persona:
    persona = (
        session.query(Persona)
        .filter(Persona.slug == artifact.analysis.persona_slug, Persona.enabled.is_(True))
        .one_or_none()
    )
    if persona is None:
        raise ValueError(f"Persona not found: {artifact.analysis.persona_slug}")
    return persona


def _get_or_create_source(session: Session, artifact: HorizonArtifact) -> Source:
    source = (
        session.query(Source)
        .filter(Source.type == artifact.source.type, Source.url == artifact.source.url)
        .one_or_none()
    )
    if source is None:
        source = Source(
            type=artifact.source.type,
            name=artifact.source.name,
            url=artifact.source.url,
            config=artifact.source.config,
        )
        session.add(source)
        session.flush()
    return source


def _get_or_create_item(session: Session, artifact: HorizonArtifact, source: Source) -> Item:
    item = (
        session.query(Item)
        .filter(Item.source_id == source.id, Item.external_id == artifact.item.external_id)
        .one_or_none()
    )
    if item is None:
        item = Item(
            source=source,
            external_id=artifact.item.external_id,
            title=artifact.item.title,
            url=artifact.item.url,
            content=artifact.item.content,
            author=artifact.item.author,
            published_at=artifact.item.published_at,
            metadata_json=artifact.item.metadata,
        )
        session.add(item)
        session.flush()
    return item


def _get_or_create_analysis(
    session: Session,
    artifact: HorizonArtifact,
    item: Item,
    persona: Persona,
) -> Analysis:
    analysis = (
        session.query(Analysis)
        .filter(Analysis.item_id == item.id, Analysis.persona_id == persona.id)
        .one_or_none()
    )
    if analysis is None:
        analysis = Analysis(
            item=item,
            persona=persona,
            score=artifact.analysis.score,
            summary=artifact.analysis.summary,
            why_it_matters=artifact.analysis.why_it_matters,
            opportunities=artifact.analysis.opportunities,
            risks=artifact.analysis.risks,
            tags=artifact.analysis.tags,
            model=artifact.analysis.model,
        )
        session.add(analysis)
    else:
        analysis.score = artifact.analysis.score
        analysis.summary = artifact.analysis.summary
        analysis.why_it_matters = artifact.analysis.why_it_matters
        analysis.opportunities = artifact.analysis.opportunities
        analysis.risks = artifact.analysis.risks
        analysis.tags = artifact.analysis.tags
        analysis.model = artifact.analysis.model
    session.commit()
    session.refresh(analysis)
    return analysis
```

- [ ] **Step 5: Run worker import tests**

Run:

```bash
pytest tests/test_worker_import.py -q
```

Expected: PASS.

- [ ] **Step 6: Run all tests and lint**

Run:

```bash
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 7: Commit worker import path**

```bash
git add app tests
git commit -m "feat: import Horizon artifacts"
```

---

### Task 9: Briefing Archive Foundation

**Files:**
- Modify: `app/services/intelligence.py`
- Modify: `app/routes/api.py`
- Modify: `app/routes/pages.py`
- Modify: `app/templates/archive.html`
- Modify: `tests/test_api.py`
- Modify: `tests/test_pages.py`

- [ ] **Step 1: Add briefing API test**

Append to `tests/test_api.py`:

```python
from datetime import date

from app.models import Briefing
from app.services.personas import get_persona_by_slug


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
```

- [ ] **Step 2: Update archive page test**

Replace `test_archive_page` in `tests/test_pages.py` with:

```python
def test_archive_page(client: TestClient, db_session: Session) -> None:
    seed_default_personas(db_session)
    persona = get_persona_by_slug(db_session, "indie-maker")
    assert persona is not None
    from datetime import date
    from app.models import Briefing

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
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```bash
pytest tests/test_api.py::test_list_briefings tests/test_pages.py::test_archive_page -q
```

Expected: FAIL because briefing list route/service is missing.

- [ ] **Step 4: Add briefing service and schemas**

Append to `app/services/intelligence.py`:

```python
from app.models import Briefing


def list_published_briefings(session: Session, limit: int = 30) -> list[Briefing]:
    return (
        session.query(Briefing)
        .filter(Briefing.status == "published")
        .order_by(Briefing.date.desc(), Briefing.created_at.desc())
        .limit(limit)
        .all()
    )
```

Modify the first import in `app/schemas.py`:

```python
from datetime import date, datetime
```

Append to `app/schemas.py`:

```python

class BriefingOut(BaseModel):
    id: int
    persona_slug: str
    persona_name: str
    date: date
    title: str
    summary: str


class BriefingListOut(BaseModel):
    items: list[BriefingOut]
```

- [ ] **Step 5: Add briefing API route**

Modify `app/routes/api.py` imports:

```python
from app.schemas import BriefingListOut, BriefingOut
from app.services.intelligence import list_persona_analyses, list_published_briefings
```

Append to `app/routes/api.py`:

```python
@router.get("/briefings", response_model=BriefingListOut)
def list_briefings(session: Session = Depends(get_session)) -> BriefingListOut:
    briefings = list_published_briefings(session)
    return BriefingListOut(
        items=[
            BriefingOut(
                id=briefing.id,
                persona_slug=briefing.persona.slug,
                persona_name=briefing.persona.name,
                date=briefing.date,
                title=briefing.title,
                summary=briefing.summary,
            )
            for briefing in briefings
        ]
    )
```

- [ ] **Step 6: Update archive route and template**

Modify `app/routes/pages.py` import:

```python
from app.services.intelligence import list_persona_analyses, list_published_briefings
```

Replace archive route in `app/routes/pages.py`:

```python
@router.get("/archive", response_class=HTMLResponse)
def archive(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    briefings = list_published_briefings(session)
    return templates.TemplateResponse(request, "archive.html", {"briefings": briefings})
```

Replace `app/templates/archive.html`:

```html
{% extends "base.html" %}
{% block title %}历史归档 - 见微{% endblock %}
{% block content %}
<section class="page-heading">
  <p class="eyebrow">Archive</p>
  <h1>历史归档</h1>
  <p>按日期和角色查看已经发布的情报。</p>
</section>

<section class="feed-list">
  {% if briefings %}
    {% for briefing in briefings %}
      <article class="feed-item">
        <div class="score">{{ briefing.date.strftime("%m-%d") }}</div>
        <div>
          <h2>{{ briefing.title }}</h2>
          <p>{{ briefing.summary }}</p>
          <p class="muted">{{ briefing.persona.name }}</p>
        </div>
      </article>
    {% endfor %}
  {% else %}
    <p class="empty-state">还没有历史情报。后台任务发布日报后会显示在这里。</p>
  {% endif %}
</section>
{% endblock %}
```

- [ ] **Step 7: Run archive tests**

Run:

```bash
pytest tests/test_api.py::test_list_briefings tests/test_pages.py::test_archive_page -q
```

Expected: PASS.

- [ ] **Step 8: Run all tests and lint**

Run:

```bash
pytest -q
ruff check app tests
```

Expected: PASS.

- [ ] **Step 9: Commit archive foundation**

```bash
git add app tests
git commit -m "feat: add briefing archive"
```

---

### Task 10: Container And Local Deployment

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `deploy/nginx.conf`
- Modify: `README_zh.md`
- Modify: `README.md`

- [ ] **Step 1: Add Dockerfile**

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml README.md README_zh.md ./
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

RUN uv sync --no-dev

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Add Docker Compose**

Create `docker-compose.yml`:

```yaml
services:
  web:
    build: .
    container_name: jianwei-web
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    command: ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

  nginx:
    image: nginx:1.27-alpine
    container_name: jianwei-nginx
    depends_on:
      - web
    ports:
      - "8080:80"
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    restart: unless-stopped
```

- [ ] **Step 3: Add Nginx config**

Create `deploy/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- [ ] **Step 4: Update README run instructions**

Append to `README_zh.md`:

```markdown
## 本地运行

```bash
uv sync --extra dev
cp .env.example .env
alembic upgrade head
uv run uvicorn app.main:app --reload
```

访问：

```text
http://127.0.0.1:8000
```

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

访问：

```text
http://127.0.0.1:8080
```
```

Append to `README.md`:

```markdown
## Local Run

```bash
uv sync --extra dev
cp .env.example .env
alembic upgrade head
uv run uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
http://127.0.0.1:8080
```
```

- [ ] **Step 5: Run local verification**

Run:

```bash
pytest -q
ruff check app tests
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expected: tests and lint PASS; server starts and logs Uvicorn startup. Stop server with Ctrl+C after confirming startup.

- [ ] **Step 6: Run Docker verification**

Run:

```bash
docker compose config
```

Expected: Compose config renders without errors.

If Docker is available locally, run:

```bash
docker compose up --build
```

Expected: web and nginx services start; `http://127.0.0.1:8080/health` returns `{"status":"ok","service":"jianwei"}`. Stop with Ctrl+C.

- [ ] **Step 7: Commit deployment files**

```bash
git add Dockerfile docker-compose.yml deploy README.md README_zh.md
git commit -m "chore: add local deployment setup"
```

---

## Final Verification

- [ ] **Step 1: Run all tests**

```bash
pytest -q
```

Expected: PASS.

- [ ] **Step 2: Run lint**

```bash
ruff check app tests
```

Expected: PASS.

- [ ] **Step 3: Check routes manually**

Start server:

```bash
uv run uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/api/personas
http://127.0.0.1:8000/archive
http://127.0.0.1:8000/static/manifest.webmanifest
```

Expected:

- `/` renders the persona selection homepage.
- `/api/personas` returns four personas.
- `/archive` renders the archive page.
- `/static/manifest.webmanifest` returns JSON with `"name": "见微"`.

- [ ] **Step 4: Verify Git state**

```bash
git status --short
```

Expected: clean working tree.

