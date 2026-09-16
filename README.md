# RemontHub — backend

Python API + Telegram bot + PostgreSQL for the RemontHub site
(`../service-for-building-home`).

| Service | Stack | Port (host) | Purpose |
|---------|-------|-------------|---------|
| `db`    | PostgreSQL 16 | `5433` | data store |
| `redis` | Redis 7 | `6380` | cache + notification feed |
| `api`   | FastAPI + SQLAlchemy 2 (async) + Alembic | `8000` | REST API, OpenAPI docs at `/docs` |
| `bot`   | aiogram 3 | — | Telegram front door, creates leads via the API |

Each service has its own image (`docker/api.Dockerfile`, `docker/bot.Dockerfile`)
and its own entry in `docker-compose.yml`.

## Quick start

```bash
cd remonthub-backend
cp .env.example .env          # edit SECRET_KEY / admin creds / bot token
docker compose up --build -d  # or: make up
```

On first boot the `api` container runs `alembic upgrade head` and then seeds the
database from the frontend mock data (`app/seed_data.py`): 8 categories,
~50 products, 12 masters, 8 services, 8 vacancies, 6 articles, 29 reviews,
21 CRM deals, plus an admin + manager user.

- API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>
- Admin login: `admin@remonthub.kz` / `admin12345` (from `.env`)
- Manager login: `manager@remonthub.kz` / `manager12345`

`make` targets: `up`, `down`, `nuke` (drop volumes), `logs`, `api-logs`,
`shell`, `psql`, `migrate`, `revision m="…"`, `seed`.

## Running the API without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/api.txt
# point at the published container ports (or a local Postgres):
export DATABASE_URL=postgresql+asyncpg://remonthub:remonthub@localhost:5433/remonthub
export REDIS_URL=redis://localhost:6380/0
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## API surface (`/api`)

| Group | Endpoints |
|-------|-----------|
| `auth` | `POST /register`, `POST /login` (OAuth2 form), `POST /refresh`, `GET/PATCH /me` |
| `catalog` | `GET /categories`, `GET /categories/{slug}`, `GET /brands`, `GET /products` (filters: `q`, `category`, `brand`, `price_min/max`, `badge`, `in_stock`, `sort`, `page`), `GET /products/{id|slug}` |
| `masters` | `GET /` (filters + pagination), `GET /districts`, `GET /{id|slug}` |
| `services` | `GET /`, `GET /{id|slug}` |
| `vacancies` | `GET /`, `GET /{id|slug}` |
| `blog` | `GET /` (paged), `GET /categories`, `GET /{slug}` |
| `reviews` | `GET /?target_type&target_id`, `GET /stats`, `POST /` (→ moderation), staff: `GET /moderation`, `POST /{id}/publish`, `POST /{id}/reject` |
| `orders` | `POST /` (checkout), `GET /mine`, `GET /{number}`, staff: `GET /`, `PATCH /{number}/status` |
| `leads` | `POST /` (site form), staff: `GET /`, `PATCH /{id}/status` |
| `calculator` | `POST /` — renovation estimate; creates a `calculator` lead when a phone is supplied |
| `crm` | staff: `GET /board` (kanban), `GET /`, `POST /`, `GET/PATCH/DELETE /{id}`, `GET /stages`, `GET /managers` |
| `telegram` | `POST /webhook` — optional; the bot uses long-polling by default |
| `admin` | staff: `GET /dashboard`, `GET /notifications`, `POST /notifications/{id}/read`, `GET /notifications/feed`; admin: `GET /users` |
| `manage` | staff-only CRUD for every content entity: `GET/POST /manage/{categories,brands,products,masters,services,vacancies,articles,faq}`, `GET/PATCH/DELETE /manage/<entity>/{id}`. Powers the Next.js admin panel. |

Roles: `customer` (default), `manager`, `admin`. Staff = manager + admin.

## Wiring the frontend

The sibling Next app (`../service-for-building-home`) already reads from this API:

- `.env.local` → `NEXT_PUBLIC_API_URL=http://localhost:8000/api`
- `lib/api/public.ts` (server components) and `lib/api/browser.ts` (client) call the
  public routers; `lib/api/map.ts` maps snake_case → the camelCase frontend types.
  Every server fetcher falls back to the bundled `lib/data/*` mock if the API is down.
- The admin panel (`/admin/*`) is fully API-backed: it logs in via `/api/auth/login`
  (admin or manager) and manages the catalog, services, masters, vacancies, articles
  and FAQ through `/api/manage/*`.

`CORS_ORIGINS` already allows `http://localhost:3030`.

## Migrations

The baseline migration (`0001_initial`) builds the schema straight from the
models. After changing a model:

```bash
make revision m="add discount column"
make migrate
```
# ales-for-building-backend
