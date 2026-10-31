# Study Tracker

[![CI](https://github.com/pedrohfernandes99/controle-estudos/actions/workflows/ci.yml/badge.svg)](https://github.com/pedrohfernandes99/controle-estudos/actions/workflows/ci.yml)

A web application to log study sessions per subject, track time spent on each one, and visualize progress over time.

## Status

🚧 **Active development** — core features working, authentication in progress.

- ✅ Subject and session management (full CRUD)
- ✅ Per-subject report with date-range filter
- ✅ Weekly breakdown report
- ✅ CSV export (respects the active filter)
- ✅ Automated test suite (33 tests)
- ✅ Continuous integration with GitHub Actions
- 🚧 Authentication: registration, login and logout working; route protection pending

## Features

### Subjects and sessions
- Create, edit and delete subjects
- Log study sessions (subject, duration in minutes, date, notes)
- Edit and delete individual sessions
- Cascade delete: removing a subject also removes its sessions

### Reports
- Total time per subject
- Filter by date range (`start` / `end`)
- Weekly breakdown (year-week grouping)
- CSV export of detailed sessions (semicolon-separated for Excel pt-BR compatibility)

### Authentication (in progress)
- User registration with password confirmation
- Secure password storage using Werkzeug's `generate_password_hash`
- Login / logout with Flask session cookies
- ⚠️ Route protection (`@login_required`) still pending

## Tech Stack

- **Python 3.8** + **Flask 2.0.3**
- **SQLite** (local database, no server required)
- **Jinja2** (HTML templates)
- **Werkzeug** (password hashing)
- **pytest 8.3.5** (33 automated tests)
- **GitHub Actions** (CI on every push)

## Running locally

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
python run.py