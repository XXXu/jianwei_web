# Jianwei

Jianwei is an AI intelligence website for indie developers and AI product builders, powered by the Horizon intelligence engine.

It is not meant to be a generic news aggregator. Its goal is to turn scattered information from news sites, RSS feeds, GitHub, communities, product launches, and industry channels into actionable product signals for indie developers.

## Positioning

> See direction in the signal.

The first version will be a free public website with a lightweight subscription entry point, focused on indie developers and AI product builders.

The first version focuses on:

- AI product opportunities
- Indie-build feasibility
- Open-source project and tooling changes
- Acquisition channels, pricing signals, and competitor movement

## Relationship With Horizon

`Horizon` is an independent intelligence collection and AI analysis engine.

`jianwei_web` is an independent web product project responsible for the user-facing product layer.

Responsibilities:

```text
Horizon
Owns: source fetching, deduplication, AI scoring, AI enrichment, summary generation, source extensions

jianwei_web
Owns: homepage, indie-maker intelligence pages, detail pages, archives, subscription entry, database, API, PWA, deployment entry
```

This project will use an adapter layer to call Horizon and convert Horizon outputs into Jianwei's own database records.

## First Version Goals

The first version is designed to validate:

1. Whether indie developers actually need this kind of AI intelligence.
2. Whether AI-generated opportunity and risk analysis is valuable enough.
3. Whether users are willing to revisit or leave a subscription contact.

The first version will include:

- Homepage intelligence entry
- Indie-maker intelligence pages
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

给脚本增加执行权限：

```bash
chmod +x bin/start.sh bin/stop.sh bin/import_artifacts.sh
```

启动 Web 应用：

```bash
./bin/start.sh
```

脚本会自动执行数据库迁移、初始化默认角色，并把服务放到后台运行。默认监听 `0.0.0.0:8000`，日志写入：

```text
logs/jianwei.log
```

查看日志：

```bash
tail -f logs/jianwei.log
```

停止 Web 应用：

```bash
./bin/stop.sh
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

## 导入 Horizon 真实数据

先在 `Horizon` 项目中运行：

```bash
uv run horizon-jianwei --persona-slug indie-maker --hours 24 --limit 20
```

该命令会输出 JSON 到：

```text
../Horizon/data/jianwei_artifacts/YYYY-MM-DD/indie-maker/
```

回到 `jianwei_web` 项目，导入这些 artifact：

```bash
./bin/import_artifacts.sh ../Horizon/data/jianwei_artifacts/YYYY-MM-DD/indie-maker
```

其中 `YYYY-MM-DD` 替换为实际日期。导入完成后，访问：

```text
http://服务器公网 IP/personas/indie-maker
```

直接部署时，`bin/start.sh` 会自动执行数据库迁移和默认角色初始化：

```bash
python -m alembic upgrade head
python -m app.seed
```

SQLite 数据库会保存在宿主机项目目录的 `data/` 目录中。
