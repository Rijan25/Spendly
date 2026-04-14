# Spec: Login and Logout

## Overview
This feature implements the authentication flow for Spendly. Users can log in with their email and password, and log out to end their session. Login validates credentials against the database and establishes a session, while logout clears the session data. This is a prerequisite for all logged-in features like expense management and profile access.

## Depends on
- Step 1: Database setup (already complete — `users` table exists)
- Step 2: Registration (already complete — users can be created with hashed passwords)

## Routes
- `GET /login` — Already implemented as stub, renders login form
- `POST /login` — New route to handle form submission, credential validation, and session creation — public
- `GET /logout` — Stub route to clear session and redirect to login — logged-in users only

## Database changes
No database changes — the `users` table already exists with:
- `id`, `name`, `email`, `password_hash`, `created_at`

## Templates
- **Create:** `templates/login.html` — Login form with email and password fields, extend `base.html`
- **Modify:** None required for initial implementation

## Files to change
- `app.py` — Add POST handler for `/login`, implement `/logout` route
- `database/db.py` — Add `get_user_by_email()` function to fetch user by email for credential validation

## Files to create
- `templates/login.html` — Login form template

## New dependencies
No new dependencies — `werkzeug.security` is already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — use sqlite3 only
- All DB queries must use parameterized queries with `?` placeholders
- Passwords must be verified with `werkzeug.security.check_password_hash()`
- All templates must extend `base.html`
- Use `flash()` for success/error messages — display them in templates
- Use Flask sessions for authentication state (`session['user_id']`)
- Redirect to `/profile` or `/` on successful login
- Validate: email exists, password matches hash
- Use `abort(400)` or re-render with error for invalid credentials
- Logout should only work for authenticated users (check `session.get('user_id')`)

## Definition of done
- [ ] GET `/login` renders the login form template
- [ ] POST `/login` with valid credentials creates a session and redirects
- [ ] POST `/login` with invalid email shows error message
- [ ] POST `/login` with wrong password shows error message
- [ ] POST `/login` with missing fields shows error message
- [ ] GET `/logout` clears the session and redirects to `/` or `/login`
- [ ] Flash message displayed on successful logout
- [ ] All links in templates use `url_for()` — no hardcoded URLs
- [ ] Session stores `user_id` after successful login
