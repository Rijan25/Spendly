import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name or not email or not password:
        return render_template("register.html", error="All fields are required.")

    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")

    password_hash = generate_password_hash(password)

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return render_template("register.html", error="An account with that email already exists.")

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="All fields are required.")

    conn = get_db()
    user = conn.execute(
        "SELECT id, name, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session.clear()
    session["user_id"]   = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


# ------------------------------------------------------------------ #
# Static pages + auth                                                 #
# ------------------------------------------------------------------ #

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


# ------------------------------------------------------------------ #
# Expenses                                                            #
# ------------------------------------------------------------------ #

# Allowed categories — kept in sync with the badge-* CSS classes.
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def _current_user_id():
    """Return the logged-in user's id, or None if not authenticated."""
    return session.get("user_id")


def _validate_expense_form(form):
    """Validate submitted expense fields.

    Returns (data, error). On success `error` is None and `data` is a dict
    ready to bind to a parameterised query; on failure `data` echoes the
    raw input so the form can be re-rendered.
    """
    amount_raw  = form.get("amount", "").strip()
    category    = form.get("category", "").strip()
    date        = form.get("date", "").strip()
    description = form.get("description", "").strip()

    data = {
        "amount": amount_raw,
        "category": category,
        "date": date,
        "description": description,
    }

    if not amount_raw or not category or not date:
        return data, "Amount, category and date are required."

    try:
        amount = float(amount_raw)
    except ValueError:
        return data, "Amount must be a number."

    if amount <= 0:
        return data, "Amount must be greater than zero."

    if category not in CATEGORIES:
        return data, "Please choose a valid category."

    data["amount"] = amount
    return data, None


@app.route("/profile")
def profile():
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    conn = get_db()
    user_row = conn.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if user_row is None:
        conn.close()
        session.clear()
        return redirect(url_for("login"))

    rows = conn.execute(
        """SELECT id, amount, category, date, description
             FROM expenses
            WHERE user_id = ?
         ORDER BY date DESC, id DESC""",
        (user_id,),
    ).fetchall()

    cat_rows = conn.execute(
        """SELECT category, SUM(amount) AS total
             FROM expenses
            WHERE user_id = ?
         GROUP BY category
         ORDER BY total DESC""",
        (user_id,),
    ).fetchall()
    conn.close()

    transactions = [dict(r) for r in rows]
    categories = [{"name": r["category"], "amount": r["total"]} for r in cat_rows]

    total_spent = sum(r["amount"] for r in rows)
    member_since = user_row["created_at"][:7] if user_row["created_at"] else ""
    if member_since:
        year, month = member_since.split("-")
        month_name = ["", "January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November",
                      "December"][int(month)]
        member_since = f"{month_name} {year}"

    user = {
        "name": user_row["name"],
        "email": user_row["email"],
        "member_since": member_since,
    }
    stats = {
        "total_spent": total_spent,
        "transaction_count": len(rows),
        "top_category": categories[0]["name"] if categories else "—",
    }

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        max_amount=categories[0]["amount"] if categories else 1,
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template(
            "expense_form.html",
            categories=CATEGORIES,
            expense=None,
            form_title="Add expense",
            action=url_for("add_expense"),
            submit_label="Add expense",
        )

    data, error = _validate_expense_form(request.form)
    if error:
        return render_template(
            "expense_form.html",
            categories=CATEGORIES,
            expense=data,
            form_title="Add expense",
            action=url_for("add_expense"),
            submit_label="Add expense",
            error=error,
        )

    conn = get_db()
    conn.execute(
        """INSERT INTO expenses (user_id, amount, category, date, description)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, data["amount"], data["category"], data["date"], data["description"]),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    conn = get_db()
    expense = conn.execute(
        "SELECT id, amount, category, date, description FROM expenses WHERE id = ? AND user_id = ?",
        (id, user_id),
    ).fetchone()

    if expense is None:
        conn.close()
        return redirect(url_for("profile"))

    if request.method == "GET":
        conn.close()
        return render_template(
            "expense_form.html",
            categories=CATEGORIES,
            expense=dict(expense),
            form_title="Edit expense",
            action=url_for("edit_expense", id=id),
            submit_label="Save changes",
        )

    data, error = _validate_expense_form(request.form)
    if error:
        conn.close()
        return render_template(
            "expense_form.html",
            categories=CATEGORIES,
            expense=data,
            form_title="Edit expense",
            action=url_for("edit_expense", id=id),
            submit_label="Save changes",
            error=error,
        )

    conn.execute(
        """UPDATE expenses
              SET amount = ?, category = ?, date = ?, description = ?
            WHERE id = ? AND user_id = ?""",
        (data["amount"], data["category"], data["date"], data["description"], id, user_id),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (id, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5002)))
