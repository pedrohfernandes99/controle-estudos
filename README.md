# Study Tracker

[![CI](https://github.com/pedrohfernandes99/controle-estudos/actions/workflows/ci.yml/badge.svg)](https://github.com/pedrohfernandes99/controle-estudos/actions/workflows/ci.yml)

A web application to log study sessions per subject and track the time spent on each one.

## Status

🚧 In development — Month 1 completed (foundation, full CRUD, basic report, tests and CI).

## Features

- Create, edit and delete subjects
- Log study sessions (duration, date, notes)
- Report of total time per subject
- Automated tests (24 tests)
- Continuous integration with GitHub Actions

## Tech Stack

- Python 3.8 + Flask 2.0.3
- SQLite (local database, no server required)
- Jinja2 (HTML templates)
- pytest (testing)
- GitHub Actions (CI)

## Running locally

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
python run.py