# Alfa Caçambas — Web Management System

Flask-based web system for managing clients, dumpsters, and rentals.

## Stack

- **Flask** — web framework
- **Flask-SQLAlchemy** — ORM
- **Flask-Login** — session-based authentication
- **Flask-WTF** — forms, validation, CSRF protection
- **python-dotenv** — environment variables
- **SQLite** — file-based database (`instance/app.db`)
- **Bootstrap 5** (CDN) — UI

## Conventions

- Application factory pattern (`create_app`).
- Blueprints by resource (`auth`, `main`, `clients`, `dumpsters`, `rentals`).
- Configuration via classes selected by `FLASK_ENV`.
- All code, identifiers, comments, and UI text in **English**.
- Type hints on function signatures.
- Password hashing via `werkzeug.security`.
- Snake_case for Python, kebab-case for templates/CSS classes.
- Secrets read from `.env` (never committed).

## Domain model

### User
`id`, `username` (unique), `email` (unique), `password_hash`, `created_at`.

### Client
`id`, `name`, `document` (CPF/CNPJ, unique), `phone`, `email`, `address`, `city`, `state`, `zip_code`, `created_at`.

### Dumpster
`id`, `identifier` (unique label, e.g. "C-001"), `size` (m³), `daily_rate`, `status` (`available` / `rented` / `maintenance`), `created_at`.

### Rental
`id`, `client_id` (FK), `dumpster_id` (FK), `delivery_address`, `start_date`, `expected_end_date`, `return_date` (nullable), `daily_rate` (snapshot from dumpster at rental time), `total_amount` (computed on close), `status` (`active` / `completed`), `created_at`.

**Rules:**
- Opening a rental: dumpster must be `available` → flips to `rented`; snapshot `daily_rate` into the rental.
- Closing a rental: sets `return_date`, computes `total_amount = daily_rate × max(1, days_between(start_date, return_date))`, dumpster flips back to `available`, status → `completed`.
- Overdue: `active` rentals where `expected_end_date < today`.

## Project structure

```
p3/
├── .venv/
├── app/
│   ├── __init__.py          # create_app factory
│   ├── config.py            # Config classes
│   ├── extensions.py        # db, login_manager, csrf
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── dumpster.py
│   │   └── rental.py
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── dumpster.py
│   │   └── rental.py
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── clients.py
│   │   ├── dumpsters.py
│   │   └── rentals.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── clients/
│   │   ├── dumpsters/
│   │   ├── rentals/
│   │   └── errors/
│   └── static/css/style.css
├── instance/                # auto-created; holds app.db
├── .env.example
├── .gitignore
├── requirements.txt
├── seed.py
├── run.py
└── ROADMAP.md
```

## Phases

### Phase 1 — Foundation
- [x] Install dependencies inside `.venv`
- [x] Create `requirements.txt`
- [x] Create `.gitignore` and `.env.example`
- [x] Create folder skeleton

### Phase 2 — App factory & config
- [x] `app/config.py` (Base, Development, Production)
- [x] `app/extensions.py` (db, login_manager, csrf)
- [x] `app/__init__.py` (`create_app`, blueprint registration, error handlers, CLI commands)
- [x] `run.py` entry point

### Phase 3 — Models
- [x] `User` with password hashing and Flask-Login mixin
- [x] `Client`
- [x] `Dumpster`
- [x] `Rental` with business helpers (`close`, `is_overdue`)

### Phase 4 — Forms
- [x] `LoginForm`, `RegisterForm`
- [x] `ClientForm`
- [x] `DumpsterForm`
- [x] `RentalOpenForm`, `RentalCloseForm`

### Phase 5 — Blueprints / routes
- [x] `auth` — login, register, logout
- [x] `main` — dashboard with KPIs
- [x] `clients` — list, create, edit, delete, detail
- [x] `dumpsters` — list, create, edit, delete
- [x] `rentals` — list (active/completed), open, close, detail

### Phase 6 — Templates
- [x] `base.html` with navbar + flash messages
- [x] Auth pages
- [x] Dashboard
- [x] Resource list/form/detail for each entity
- [x] 404 / 500 pages

### Phase 7 — Polish
- [x] CSS tweaks
- [x] `seed.py` with sample data + default admin
- [x] `README.md` with run instructions

### Phase 8 — Verification
- [x] First-run DB creation
- [x] Manual smoke test of full flow (login → create client → create dumpster → open rental → close rental → dashboard)

### Phase 9 — Revenue report
- [x] `RevenueReportForm` (no CSRF — read-only GET)
- [x] `reports` blueprint with `/reports/revenue`
- [x] Template with KPI cards and rentals table, filtered by `return_date`
- [x] Navbar entry

### Phase 11 — Drivers & material tracking
- [x] `Driver` model (name, document, phone, license_number)
- [x] `Rental.driver_id` foreign key + relationship
- [x] `MaterialType` enum + `Rental.material_type` column
- [x] `Rental.close(return_date, material_type)` records material
- [x] `DriverForm` with duplicate-document / duplicate-license validation
- [x] `drivers` blueprint (list, create, edit, delete, detail)
- [x] Driver selector on rental open form; material selector on close form
- [x] Driver shown on rental detail; material shown on detail + revenue report
- [x] Navbar entry for Drivers
- [x] Seed creates two sample drivers and assigns one to the seed rental
- [x] Tests: `test_drivers.py` (7 tests) + updates to `test_rentals.py` + `test_reports.py`

### Phase 10 — Test suite
- [x] `TestingConfig` (in-memory SQLite, CSRF off)
- [x] Pytest fixtures (`app`, `client`, `admin_user`, `auth_client`, `sample_client`, `sample_dumpster`, `open_rental`)
- [x] `test_auth.py` — login required, login flow, register, logout
- [x] `test_clients.py` — CRUD + duplicate document + delete-with-active-rental guard
- [x] `test_dumpsters.py` — CRUD + duplicate identifier + delete-rented guard + status filter
- [x] `test_rentals.py` — model helpers (open/close/overdue) + form lifecycle
- [x] `test_dashboard.py` — KPIs render + overdue badge
- [x] `test_reports.py` — period sum, exclusion, validation
