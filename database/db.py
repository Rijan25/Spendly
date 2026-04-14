import sqlite3
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = "spendly.db"


def get_db():
    """Opens connection to spendly.db with row_factory and foreign keys enabled."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Creates tables using CREATE TABLE IF NOT EXISTS."""
    db = get_db()

    # Users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT (datetime('now'))
        )
    """)

    # Expenses table
    db.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.commit()


def create_user(name, email, password):
    """Creates a new user with hashed password.

    Args:
        name: User's full name
        email: User's email address
        password: User's plain text password

    Returns:
        int: The new user's ID

    Raises:
        ValueError: If email already exists
    """
    db = get_db()

    # Check if email already exists
    existing = db.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()

    if existing:
        raise ValueError("Email already registered")

    # Hash password and insert
    password_hash = generate_password_hash(password)
    cursor = db.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    """, (name, email, password_hash))

    db.commit()
    return cursor.lastrowid


def seed_db():
    """Inserts demo data only once."""
    db = get_db()

    # Check if already seeded
    existing_user = db.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()

    if existing_user:
        return  # Already seeded

    # Insert demo user
    password_hash = generate_password_hash("demo123")
    db.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    """, ("Demo User", "demo@spendly.com", password_hash))

    # Get the user id
    user = db.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()
    user_id = user["id"]

    # Insert 8 sample expenses across all 7 categories
    sample_expenses = [
        (50.00, "Food", "2026-04-01", "Grocery shopping"),
        (25.00, "Transport", "2026-04-02", "Bus pass"),
        (80.00, "Bills", "2026-04-03", "Electric bill"),
        (35.00, "Health", "2026-04-04", "Pharmacy"),
        (15.00, "Entertainment", "2026-04-05", "Movie ticket"),
        (120.00, "Shopping", "2026-04-06", "New shoes"),
        (40.00, "Other", "2026-04-07", "Miscellaneous"),
        (60.00, "Food", "2026-04-08", "Restaurant dinner"),
    ]

    for amount, category, date, description in sample_expenses:
        db.execute("""
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, category, date, description))

    db.commit()
