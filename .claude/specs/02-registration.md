# Spec: Registration

## Overview
This feature implements the user registration flow for Spendly. Users can create an account by providing their name, email, and password. The registration page already exists as a stub route — this step makes it functional by adding POST handling, input validation, password hashing, and user creation in the database.

## Depends on
- Step 1: Database setup (already complete — `users` table exists in `database/db.py`)

## Routes
- `GET /register` — Already implemented, renders registration form
- `POST /register` — New route to handle form submission, validation, and user creation — public

## Database changes
No database changes — the `users` table already exists with:
- `id`, `name`, `email`, `password_hash`, `created_at`

## Templates
- **Modify:** `templates/register.html` — Add flash message display for success/error feedback, add `url_for()` for form action instead of hardcoded path

## Files to change
- `app.py` — Add POST handler for `/register` route
- `database/db.py` — Add `create_user()` function for inserting new users
- `templates/register.html` — Minor updates for flash messages and proper URL handling

## Files to create
No new files.

## New dependencies
No new dependencies — `werkzeug.security` is already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — use sqlite3 only
- All DB queries must use parameterized queries with `?` placeholders
- Passwords must be hashed with `werkzeug.security.generate_password_hash()`
- All templates must extend `base.html`
- Use `flash()` for success/error messages — display them in templates
- Redirect to login page on successful registration
- Validate: email uniqueness, password minimum length (8 characters)
- Use `abort(400)` for validation errors with form re-render

## Definition of done
- [ ] POST `/register` creates a new user in the database
- [ ] Password is hashed before storage (verify in DB that plain text is not stored)
- [ ] Duplicate email returns error message and re-renders form
- [ ] Password under 8 characters returns error message
- [ ] Missing required fields returns error message
- [ ] Successful registration redirects to `/login` with success flash message
- [ ] All links in templates use `url_for()` — no hardcoded URLs
