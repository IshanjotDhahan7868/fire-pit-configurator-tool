# Fire Pit Configurator Platform

Production-style white-label multi-tenant SaaS MVP for fire pit businesses.

## Tech Stack
- Monorepo: pnpm + turbo
- Frontend: Next.js (App Router), TypeScript, Tailwind, Zustand, React Three Fiber
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT auth
- DB: PostgreSQL recommended (SQLite supported for fast local dev)
- PDF: ReportLab

## Version Requirements
- Python: **3.11.x**
- Node: **20+**
- pnpm: **9+**

## Quick Start (Local)

### 1) Start PostgreSQL (recommended)
```bash
docker compose up -d postgres
```

### 2) API
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3) Web
```bash
cd apps/web
cp .env.example .env.local
pnpm install
pnpm dev
```

### 4) Open
- Home: `http://localhost:3000`
- Onboarding guide: `http://localhost:3000/onboarding`
- Configurator: `http://localhost:3000/t/ember-outdoor/configurator`
- Embed preview: `http://localhost:3000/t/ember-outdoor/configurator?embed=1`
- Admin: `http://localhost:3000/admin`

## Demo Tenant + Credentials
- Tenant slug: `ember-outdoor`
- User: `owner@ember-demo.com`
- Password: `Demo1234!`

## Migrations + Seed
- Migrations run automatically on API startup (`apps/api/app/migrations.py`).
- Initial migration SQL: `apps/api/alembic/versions/0001_initial.sql`.
- Seed is idempotent (`apps/api/app/seed.py`).

## Deployment Notes
1. Use managed PostgreSQL and set `DATABASE_URL` accordingly.
2. Set strong `SECRET_KEY` (32+ chars).
3. Restrict `CORS_ORIGINS` to production domains.
4. Put API/web behind HTTPS reverse proxy.
5. Replace local email/PDF file storage with cloud providers (SES/SendGrid + S3).
6. Add observability (Sentry, logs, metrics) and backups.

## API Highlights
- Auth: `POST /auth/token`, `GET /auth/me`
- Public: tenant/products/pricing/config save+load/quote request
- Admin: overview analytics, onboarding progress, leads, quotes/detail + PDF, products, pricing rules, branding, subscription, embed info

---

## Implemented vs Stubbed Checklist

### ✅ Implemented
- [x] Multi-tenant schema foundation (tenants/users/products/configurations/leads/quotes/subscriptions)
- [x] Role-based auth and admin role gating
- [x] Tenant-scoped admin queries and updates
- [x] Public configurable fire pit flow with full visible option controls
- [x] Live line-item pricing + compatibility/safety notes
- [x] Save config + share link + load from shared `public_id`
- [x] Quote request form with validated input
- [x] Lead + quote lifecycle basics (stages/statuses + notes)
- [x] Quote PDF generation with tenant branding colors
- [x] Admin navigation + information hierarchy with overview analytics
- [x] Admin editing: products, pricing rules, branding, embed snippet
- [x] Embed mode route (`?embed=1`)
- [x] Automated API tests for pricing, happy path, tenant isolation

### 🟡 Partially Implemented (MVP Scaffolding)
- [ ] Self-serve tenant signup/onboarding UI
- [ ] Stripe checkout + webhook sync (domain scaffold exists)
- [ ] Rich no-code rule editor UX (JSON editor exists)
- [ ] Full CRM workflow automation/reporting
- [ ] Production cloud storage/email providers

### 🔜 Next Recommended Steps
- [ ] Add Playwright e2e for web flows
- [ ] Add audit/event log model + admin history views
- [ ] Add background job queue for async email/PDF tasks
- [ ] Add hardened rate limits, anti-abuse, and secrets management
- [ ] Improve admin visual polish with design system components

## Testing
From `apps/api`:
```bash
pytest
```

Current tests cover:
- pricing/rules calculations
- public configuration save/load/share + quote flow
- tenant scoping in admin API
