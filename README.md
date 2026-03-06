# Fire Pit Configurator Platform (MVP)

Production-style white-label multi-tenant SaaS MVP for custom outdoor fire pit businesses.

## Implemented MVP Scope

### Multi-tenant SaaS foundations
- Tenant model with branding fields (`brand_primary`, `brand_secondary`, logo URL hook).
- Tenant-scoped products, configurations, leads, and quotes.
- Role-based users (`owner`, `admin`, `sales`, `viewer`) with JWT auth.
- Demo seeded tenant: **Ember Outdoor Living**.

### Public configurator
- Public tenant route (`/t/[tenantSlug]/configurator`) in Next.js.
- Interactive 3D scene (React Three Fiber + drei OrbitControls).
- Option-driven visuals (shape + material changes the rendered mesh and color).
- Live pricing call to backend pricing API.
- Save configuration and share by generated public id.
- Quote request from saved configuration.

### Pricing/rules engine (MVP)
- Base + size + material + fuel + accessory pricing.
- Compatibility/safety note hooks:
  - Wood requires manual ignition note.
  - Gas requires burner note if missing.
  - Stone round fabrication surcharge.
- Persisted pricing snapshot on configurations and quotes.

### Quote + lead system
- Quote request endpoint creates:
  1) Lead record
  2) Quote record with pricing snapshot
- PDF quote generation via ReportLab.
- Email service abstraction with local file output fallback.

### Admin dashboard (MVP)
- Admin page at `/admin`:
  - Demo login action
  - Load tenant leads and quotes
  - Displays CRM-style list basics

### DevOps/readiness
- Monorepo layout (`apps/web`, `apps/api`, `packages/*`) with pnpm + turbo config.
- Docker Compose for PostgreSQL local dependency.
- `.env.example` files for API and Web.

## Repository Structure

- `apps/web`: Next.js frontend (App Router, TS, Tailwind, R3F)
- `apps/api`: FastAPI backend (SQLAlchemy, Pydantic, JWT auth)
- `packages/config-engine`: shared pricing utility scaffold
- `packages/types`: shared type scaffolding
- `docker-compose.yml`: local postgres service

## Local Run

### 1) Start database (optional for sqlite default)
```bash
docker compose up -d postgres
```

### 2) API setup
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3) Web setup
```bash
cd apps/web
cp .env.example .env.local
pnpm install
pnpm dev
```

Open:
- Public configurator: `http://localhost:3000/t/ember-outdoor/configurator`
- Admin dashboard: `http://localhost:3000/admin`

## Seeded Demo Credentials
- Email: `owner@ember-demo.com`
- Password: `Demo1234!`

## API Endpoints (core)
- `GET /health`
- `POST /auth/token`
- `GET /public/tenant/{slug}`
- `GET /public/tenant/{slug}/products`
- `POST /public/pricing`
- `POST /public/configurations`
- `GET /public/configurations/{public_id}`
- `POST /public/quote-request`
- `GET /admin/leads` (auth)
- `GET /admin/quotes` (auth)

## Implemented vs Stubbed

### Implemented
- End-to-end public config -> save -> quote -> admin visibility -> PDF generation
- JWT auth + tenant role on user records
- Core pricing and compatibility notes
- Local email fallback writer

### Stubbed / next-up
- Full onboarding flow UI
- Stripe checkout/webhooks integration (domain model placeholder only)
- Rich rule editor UI and advanced rule DSL
- Full audit logs and analytics dashboards
- Alembic migrations (currently startup `create_all`)
- Production cloud storage/email provider adapters

## Testing
From `apps/api`:
```bash
pytest
```

Covers:
- Pricing engine behavior
- API happy path from pricing to quote request

## Deployment Notes
- Replace sqlite with PostgreSQL by setting `DATABASE_URL`.
- Lock CORS allow-list in production.
- Rotate `SECRET_KEY`.
- Replace file-based email/PDF storage with cloud adapters (S3 + ESP).
- Add reverse proxy + HTTPS termination (e.g., Nginx/Caddy).
