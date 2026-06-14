# Spec: Registration

## Overview
Implement user registration so new visitors can create a Spendly account. This step wires the existing `GET /register` route to also handle `POST`, validates the submitted form, hashes the password, inserts a new row into the `users` table, and redirects the user to the login page on success. The template (`templates/register.html`) already exists with the correct form markup — only the route logic needs to be added.

## Depends on
- Step 1: `database/db.py` — `get_db()` and `init_db()` must be working; the `users` table must exist.

## Routes
- `POST /register` — accepts form submission (name, email, password), validates input, inserts user, redirects to `/login` on success or re-renders the form with an `error` on failure — public

## Database changes
No database changes. The `users` table is already created by `init_db()` in Step 1.

## Templates
- **Modify:** `templates/register.html` — no markup changes needed; the template already renders `{{ error }}` inline. No changes required unless the form fields need to be repopulated on error (nice-to-have, not required for definition of done).

## Files to change
- `app.py` — convert `GET /register` route to accept `GET, POST`; add form handling, validation, DB insert, and redirect logic. Add imports: `request`, `redirect`, `url_for` from flask; `generate_password_hash` from `werkzeug.security`.

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never use string formatting in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Duplicate email must show a user-friendly inline error (not a 500); catch the `sqlite3.IntegrityError`
- Validate that name, email, and password are all non-empty before hitting the DB
- Minimum password length: 8 characters
- On success, redirect to `/login` using `redirect(url_for('login'))`
- Do **not** auto-login the user after registration (session management comes in a later step)

## Definition of done
- [ ] Submitting the register form with valid data inserts a new user in the database
- [ ] The stored password is a hashed string (not plaintext)
- [ ] Submitting with a duplicate email shows an inline error message and does not crash
- [ ] Submitting with an empty name, email, or password shows an inline error message
- [ ] Submitting with a password shorter than 8 characters shows an inline error message
- [ ] Successful registration redirects to `/login`
- [ ] `GET /register` still renders the blank form with no errors
- [ ] App starts without errors after the change
