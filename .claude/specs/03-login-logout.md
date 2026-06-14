# Spec: Login and Logout

## Overview
Implement login and logout so registered users can authenticate with Spendly. This step wires the existing `GET /login` route stub to also handle `POST`, validates credentials against the `users` table, starts a Flask session on success, and redirects the user to the dashboard (or a placeholder). The `GET /logout` stub is also implemented to clear the session and redirect back to the landing page. A `secret_key` must be configured on the Flask app for sessions to work.

## Depends on
- Step 1: `database/db.py` — `get_db()` must be working and the `users` table must exist.
- Step 2: Registration — users must exist in the database with hashed passwords.

## Routes
- `GET /login` — renders the login form — public
- `POST /login` — accepts email + password, validates against DB, starts session, redirects to `/dashboard` placeholder on success or re-renders form with `error` on failure — public
- `GET /logout` — clears the session, redirects to `/` — logged-in (but safe to call when not logged in too)

## Database changes
No database changes. The `users` table already has all required columns.

## Templates
- **Modify:** `templates/login.html` — add POST action and method to the form; display inline `{{ error }}` message (if not already present).

## Files to change
- `app.py` — four changes:
  1. Add `app.secret_key` (set from an env var with a fallback for development).
  2. Add `session` to the Flask import.
  3. Add `check_password_hash` to the `werkzeug.security` import.
  4. Convert `GET /login` to accept `GET, POST`; add form handling, DB lookup, password check, session write, and redirect.
  5. Implement `GET /logout` to clear the session and redirect to `landing`.

## Files to create
None.

## New dependencies
No new dependencies. `flask.session` is part of Flask; `check_password_hash` is already installed via Werkzeug.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never use string formatting in SQL
- Passwords verified with `werkzeug.security.check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Store only `user_id` and `user_name` in the session — never store the password or hash
- Wrong email or wrong password must both show the same generic error ("Invalid email or password.") — do not reveal which field was wrong
- `secret_key` must be loaded via `os.environ.get("SECRET_KEY", "dev-secret-change-me")` — never hardcode a real secret
- On successful login, redirect to `url_for('dashboard')` — if that route does not yet exist, add a temporary placeholder route returning a string
- Logout must call `session.clear()` then redirect to `url_for('landing')`

## Definition of done
- [ ] `GET /login` renders the login form with no errors
- [ ] Submitting valid credentials writes `user_id` and `user_name` into the session and redirects away from `/login`
- [ ] Submitting an unknown email shows "Invalid email or password." inline (no 500 error)
- [ ] Submitting a correct email but wrong password shows "Invalid email or password." inline
- [ ] Submitting with empty fields shows an inline validation error before hitting the DB
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] After logout, revisiting a session-protected page (if any exist) does not show protected content
- [ ] App starts without errors after the change
