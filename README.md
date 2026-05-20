# LogSystem - Sistemas Logísticos

Flask web application for managing clients, drivers, dumpsters, and rentals for Alfa Caçambas (Votorantim/SP).

## Features

- Session-based authentication (Flask-Login) with login, register, and logout.
- **Client** CRUD with active-rental safety check and direct contact links (`tel:` / `mailto:`).
- **Driver** CRUD with CPF and license number (CNH) uniqueness validation, blocked deletion when assigned to active rentals.
- **Dumpster** CRUD with status filter (`available`, `rented`, `maintenance`).
- **Rental** lifecycle:
  - **Open** — selects client, dumpster, driver; snapshots the daily rate; locks the dumpster.
  - **Close** — records the material discarded (construction debris, soil, wood, vegetation, mixed, other); auto-computes `total_amount = daily_rate × max(1, days)`; frees the dumpster.
- **Dashboard** with KPIs (clients, available dumpsters, active and overdue rentals) and a recent-rentals table.
- **Revenue report** by period — filters completed rentals by return date and shows total revenue, count, billed days, and a per-rental breakdown including driver and material.

## Stack

- Python 3.13 — Flask 3.x
- Flask-SQLAlchemy, Flask-Login, Flask-WTF
- pytest for the test suite
- SQLite (file at `instance/app.db`)
- Bootstrap 5 (CDN)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit SECRET_KEY
python seed.py         # creates DB, admin user, drivers, dumpsters, and a sample rental
```

## Run

```bash
source .venv/bin/activate
python run.py
# open http://127.0.0.1:5000
```

Default admin (from `seed.py`): **username** `admin` / **password** `admin123`.

## Tests

The project ships with a pytest suite (38 tests) that uses an in-memory SQLite database and disables CSRF inside the testing config.

```bash
source .venv/bin/activate
pytest -v                 # run everything
pytest tests/test_rentals.py -v   # run a single module
pytest -k "report"        # run by keyword
```

The suite covers: authentication, client/driver/dumpster CRUD with their guards, rental open/close flow, automatic total calculation, material recording, overdue detection, dashboard KPIs, and the revenue report.

## Resetting the database

The project uses `db.create_all()` (no Alembic migrations). When the schema changes — e.g. a new column or table — drop the SQLite file and re-seed:

```bash
rm -f instance/app.db
python seed.py
```

## Main routes

| Route | Purpose |
| --- | --- |
| `/auth/login`, `/auth/register`, `/auth/logout` | Authentication |
| `/` | Dashboard |
| `/clients/` | Client list, create, edit, detail |
| `/drivers/` | Driver list, create, edit, detail |
| `/dumpsters/` | Dumpster list with status filter |
| `/rentals/` | Rental list (active/completed), open, detail, close |
| `/reports/revenue` | Revenue by period |

## Project structure

See `ROADMAP.md` for the phase-by-phase build log and the directory layout.
