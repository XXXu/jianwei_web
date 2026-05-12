# Jianwei

Jianwei is a role-based AI intelligence website powered by the Horizon intelligence engine.

It is not meant to be a generic news aggregator. Its goal is to turn scattered information from news sites, RSS feeds, GitHub, communities, product launches, funding updates, and industry channels into actionable intelligence for different user roles.

## Positioning

> See direction in the signal.

The first version will be a free public website with a lightweight subscription entry point. Users first choose who they are, then enter an intelligence feed tailored to that role.

Planned initial roles include:

- Indie developers / AI product builders
- Cross-border sellers / global product operators
- Investment / fundraising observers
- Enterprise AI adoption leads

## Relationship With Horizon

`Horizon` is an independent intelligence collection and AI analysis engine.

`jianwei_web` is an independent web product project responsible for the user-facing product layer.

Responsibilities:

```text
Horizon
Owns: source fetching, deduplication, AI scoring, AI enrichment, summary generation, source extensions

jianwei_web
Owns: homepage, persona pages, detail pages, archives, subscription entry, database, API, PWA, deployment entry
```

This project will use an adapter layer to call Horizon and convert Horizon outputs into Jianwei's own database records.

## First Version Goals

The first version is designed to validate:

1. Which roles actually need this kind of intelligence.
2. Whether role-based AI analysis is valuable enough.
3. Whether users are willing to revisit or leave a subscription contact.

The first version will include:

- Homepage with persona selection
- Persona intelligence pages
- Intelligence detail pages
- Historical archive pages
- Email subscription entry
- SQLite persistence
- JSON API
- Server-rendered pages
- Basic PWA support
- Nginx reverse proxy deployment

The first version will not include:

- User registration or login
- Paid subscription
- Personal custom sources
- Complex admin dashboard
- Bookmarks
- Comments
- Native mobile apps
- Minute-level real-time fetching

## Technical Direction

The planned architecture is a lightweight single-server setup suitable for a 2-core 4 GB cloud server:

```text
Nginx
→ FastAPI web app
→ SQLite database
→ Worker scheduled jobs
→ Horizon engine
→ AI APIs / data sources
```

Planned stack:

- FastAPI: web backend, JSON API, subscription submission
- Jinja2: first-version server-side rendered pages
- SQLite: first-version data storage
- SQLAlchemy: database access layer
- Alembic: database migrations
- cron or APScheduler: scheduled jobs
- Docker Compose: starts the Nginx reverse proxy only
- Nginx: reverse proxy, HTTPS, static assets
- PWA: lightweight app-like experience from the browser

## Replaceable Frontend Principle

The first version may use Jinja2 for fast delivery, but the architecture must allow a future React / Next.js frontend.

Principles:

- Business logic should not live in templates.
- Every core page should have a corresponding JSON API.
- Data models should be independent from the presentation layer.
- Jinja2 pages are only the first-version presentation layer.
- A future React / Next.js frontend should be able to consume the existing APIs directly.

## Project Status

This project is currently in the initial productization stage. Implementation has not started yet.

The design document lives in this project:

```text
docs/superpowers/specs/2026-05-11-horizon-product-design.md
```

## Linux 直接部署 Web 应用

当前 MVP 已经具备 FastAPI 应用、SQLite 数据模型、角色化页面、JSON API、PWA 基础文件、Horizon artifact 导入链路和历史归档基础。

在 Linux 服务器上进入项目目录后，先创建虚拟环境并安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

准备环境变量：

```bash
cp .env.example .env
```

初始化数据库和默认角色：

```bash
mkdir -p data
python -m alembic upgrade head
python -m app.seed
```

启动 Web 应用：

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

验证健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## Docker Compose 启动 Nginx

当前 `docker-compose.yml` 只启动 Nginx 容器。`jianwei_web` 应用直接运行在 Linux 宿主机的 `8000` 端口。

确认 Docker Compose 文件可以解析：

```bash
sudo docker compose config
```

启动 Nginx：

```bash
sudo docker compose up -d
```

查看日志：

```bash
sudo docker compose logs -f
```

验证 Nginx 代理：

```bash
curl http://127.0.0.1/health
```

预期返回：

```json
{"status":"ok","service":"jianwei"}
```

浏览器访问：

```text
http://服务器公网 IP
```

如果公网无法访问，请在腾讯云控制台检查安全组入站规则，至少开放 TCP `80` 端口。

直接部署时，需要手动执行数据库迁移和默认角色初始化：

```bash
python -m alembic upgrade head
python -m app.seed
```

SQLite 数据库会保存在宿主机项目目录的 `data/` 目录中。
