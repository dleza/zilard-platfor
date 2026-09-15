# Disability-Disaggregated Labour Data Management System Prototype

First-version Django prototype for the ZILARD/ZCTU/ZAFOD/SASK Disability Inclusion in the World of Work project. It is designed for early stakeholder demos, data-collection workflow testing, and requirements refinement before full production development.

## Folder Structure

```text
.
├── config/                 # Django settings, URLs, ASGI/WSGI
├── core/                   # Shared audit log, middleware, template helpers
├── users/                  # Custom user model, RBAC, login, optional TOTP
├── workers/                # Workers, disability profiles, workplaces, APIs
├── monitoring/             # Project activities and training attendance
├── dashboards/             # Role-aware dashboard and GIS map
├── reports/                # CSV, Excel, and PDF report views
├── feedback/               # Stakeholder feedback capture and review
├── mobile_api/             # Token-authenticated endpoints for the Expo mobile app
├── mobile/                 # Expo/React Native mobile app scaffold
├── templates/              # Tailwind/HTMX server-rendered UI
├── static/                 # CSS and JavaScript
├── media/                  # Local uploaded files during development
├── manage.py
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_sample_data --workers 75
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Demo Accounts

The sample-data command creates these users. Password for all: `ChangeMe!2026`

| Username | Role |
| --- | --- |
| `admin` | System Admin / superuser |
| `manager` | National Project Manager |
| `focal_muz` | Trade Union Focal Person assigned to MUZ |
| `collector_muz` | Data Collector assigned to MUZ |
| `readonly` | Read-Only user |

You can also create your own admin:

```bash
python manage.py createsuperuser
```

## Implemented MVP Features

- Role-based access model: System Admin, National Project Manager, Trade Union Focal Person, Data Collector, Read-Only.
- Custom login/logout with optional TOTP fields and verification flow.
- Worker registry with unique IDs, demographics, contact, location, workplace, sector, occupation, employment, and union data.
- Province and district fields use pre-entered Zambia district dropdowns, centrally managed in `workers/choices.py`.
- Occupations are managed in Django Admin under Workers > Occupation settings and appear as a selectable dropdown during worker entry.
- Trade unions are managed in Django Admin under Workers > Trade union settings and appear as selectable union-name dropdowns during worker entry and filtering.
- System Admin users also get an in-app Settings menu for managing occupation and trade union lookup forms without leaving the prototype UI.
- The in-app Settings menu also includes user management and role/user-category settings for System Admin users.
- Disability profile linked to workers with type, severity, assistive devices, accommodations, accessibility challenges, functional limitations, and Washington Group-inspired questions.
- Workplace records with accessibility status and accessibility audit records.
- Workplace accommodations available is captured as a Yes/No field, with supporting notes kept separately.
- Labour-rights tracking for grievances, legal support, collective bargaining, and social protection.
- Project monitoring records for trainings, workshops, audits, engagement, advocacy, and attendance.
- Mobile-friendly data collection form with localStorage draft saving, simulated GPS capture, and upload preview.
- Searchable/filterable worker list with HTMX partial refresh.
- Dashboard with summary cards, disability/gender/province/union/accessibility charts.
- Leaflet map for worker GPS points.
- Visible report workspace with standard reports, custom filters, and matching CSV, Excel, and PDF exports.
- Django Admin for power users.
- DRF endpoints under `/api/`.
- Mobile-ready DRF endpoints under `/api/mobile/`, including token login, lookups, dashboard summary, workers, workplaces, labour rights, and feedback.
- Expo/React Native starter app in `mobile/` with login, dashboard, worker submission, GPS capture, feedback, and offline queue helper.
- Stakeholder feedback button on every authenticated page.
- Basic audit trail via model signals.
- Accessibility basics: semantic headings, labels, skip link, keyboard-friendly controls, high contrast mode, strong focus states.

## PostgreSQL Switch

SQLite is the default for prototype demos. To use PostgreSQL, set these environment variables before running migrations:

```bash
set DB_ENGINE=postgresql
set POSTGRES_DB=dldms
set POSTGRES_USER=dldms
set POSTGRES_PASSWORD=change-me
set POSTGRES_HOST=127.0.0.1
set POSTGRES_PORT=5432
```

Then run:

```bash
python manage.py migrate
python manage.py load_sample_data
```

## Verification

The project was smoke-tested locally with:

```bash
python manage.py check
python manage.py migrate
python manage.py load_sample_data --workers 75
```

Main pages, the worker API, and CSV export returned successful responses in a Django test client. Excel and PDF exports require `openpyxl` and `reportlab` from `requirements.txt`.

## Mobile App Prototype

The mobile app scaffold lives in `mobile/`.

```bash
cd mobile
npm install
npm run start
```

If testing on a physical Android phone, change `mobile/src/api/client.ts` so `API_BASE_URL` uses the computer's LAN IP address, for example:

```ts
export const API_BASE_URL = "http://192.168.1.25:8000/api/mobile";
```

Then run Django on all interfaces:

```bash
python manage.py runserver 0.0.0.0:8000
```

The mobile app authenticates through:

```text
POST /api/mobile/auth/login/
```

and then sends:

```text
Authorization: Token <token>
```

on later requests.
