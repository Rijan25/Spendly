# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands should be run from the `expense-tracker/` directory with the virtual environment activated.

```powershell
# Activate venv (Windows)
.\venv\Scripts\Activate.ps1

# Run the development server (port 5001)
python app.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_auth.py

# Run a specific test
pytest tests/test_auth.py::test_login_success
```

## Architecture

**Spendly** is a step-by-step guided Flask/SQLite expense tracker. Much of the codebase is intentionally left as stubs for students to implement.

### Entry point and routing

`app.py` is the sole Flask application file — it creates the `app` instance and defines all routes. Routes are plain functions returning either `render_template(...)` calls or placeholder strings for unimplemented steps.

### Database layer

`database/db.py` is the database module (currently a stub). It is expected to expose three functions:
- `get_db()` — returns a `sqlite3.Connection` with `row_factory = sqlite3.Row` and `PRAGMA foreign_keys = ON`
- `init_db()` — creates tables using `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — inserts sample rows for development

The SQLite database file (`expense_tracker.db`) is gitignored and lives at the project root.

### Templates

All templates extend `templates/base.html` using Jinja2 block inheritance (`{% extends "base.html" %}`). The blocks used are `title`, `head`, `content`, and `scripts`. Flash/error messages are rendered inline via `{% if error %}` rather than Flask's `flash()` mechanism.

### Static assets

`static/css/style.css` — app-wide styles (uses DM Serif Display and DM Sans from Google Fonts)  
`static/js/main.js` — client-side JS (stub; features added per step)

### Planned build-out steps

The route stubs in `app.py` correspond to a numbered implementation sequence:
- Step 1: `database/db.py` — SQLite setup
- Step 3: `/logout`
- Step 4: `/profile`
- Steps 7–9: `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`

Password hashing is expected to use `werkzeug.security` (`generate_password_hash` / `check_password_hash`), which is already installed as a Flask dependency.
