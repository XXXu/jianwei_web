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
- Docker Compose deployment

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
- Docker Compose: single-server deployment
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
