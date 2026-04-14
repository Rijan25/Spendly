#!/usr/bin/env python3
"""Seed script to create a random Nepali user in the database."""

import sqlite3
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

DATABASE = "spendly.db"

# Common Nepali first names
FIRST_NAMES = [
    "Aarav", "Aayush", "Bibek", "Bikash", "Dipesh", "Ganesh", "Hari",
    "Ishan", "Janak", "Kamal", "Krishna", "Madhav", "Nabin", "Omesh",
    "Prabin", "Prakash", "Rajesh", "Ramesh", "Sagar", "Sandeep", "Sanjay",
    "Saroj", "Sushil", "Umesh", "Vijay", "Yogesh",
    "Anita", "Bandana", "Deepa", "Gita", "Hema", "Jamuna", "Kamala",
    "Laxmi", "Maya", "Nirmala", "Pooja", "Rashmi", "Sita", "Sharma",
    "Tara", "Uma", "Vandana"
]

# Common Nepali last names
LAST_NAMES = [
    "Adhikari", "Aryal", "Baral", "Bhattarai", "Chalise", "Chaudhary",
    "Dahal", "Dhungana", "Gautam", "Ghimire", "Gurung", "Hamal",
    "Joshi", "Kafle", "Karki", "Khadka", "Koirala", "Lamichhane",
    "Magar", "Marahatta", "Neupane", "Oli", "Pandey", "Parajuli",
    "Paudel", "Pokhrel", "Pradhan", "Rai", "Rijal", "Rana",
    "Regmi", "Shrestha", "Subedi", "Tamang", "Thapa", "Upadhyay"
]


def get_db_connection():
    """Opens connection to spendly.db with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def generate_nepali_name():
    """Generate a random Nepali name."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return f"{first_name} {last_name}"


def generate_email(name):
    """Generate email from name with random 2-3 digit suffix."""
    # Convert name to lowercase and replace spaces with dots
    name_part = name.lower().replace(" ", ".")
    # Add random 2-3 digit number
    digits = random.randint(10, 999)
    return f"{name_part}{digits}@gmail.com"


def email_exists(conn, email):
    """Check if email already exists in users table."""
    cursor = conn.execute("SELECT id FROM users WHERE email = ?", (email,))
    return cursor.fetchone() is not None


def seed_user():
    """Generate and insert a unique Nepali user."""
    conn = get_db_connection()

    max_attempts = 10
    for _ in range(max_attempts):
        name = generate_nepali_name()
        email = generate_email(name)

        if not email_exists(conn, email):
            break
    else:
        print("Failed to generate unique email after multiple attempts")
        conn.close()
        return

    password_hash = generate_password_hash("password123")
    created_at = datetime.now().isoformat()

    # Insert the user
    cursor = conn.execute("""
        INSERT INTO users (name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, email, password_hash, created_at))

    conn.commit()

    user_id = cursor.lastrowid

    print(f"User created successfully!")
    print(f"  id: {user_id}")
    print(f"  name: {name}")
    print(f"  email: {email}")

    conn.close()


if __name__ == "__main__":
    seed_user()
