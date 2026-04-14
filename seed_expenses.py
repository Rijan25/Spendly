#!/usr/bin/env python3
"""Seed script to create random expenses for a user."""

import sqlite3
import random
import sys
from datetime import datetime, timedelta
from database.db import DATABASE

# Expense categories with realistic Indian descriptions and amount ranges (₹)
CATEGORIES = {
    "Food": (50, 800, [
        "Lunch at office canteen", "Grocery shopping", "Street food",
        "Restaurant dinner", "Morning chai and snacks", "Weekend buffet",
        "Pizza delivery", "Fresh fruits", "Bakery items"
    ]),
    "Transport": (20, 500, [
        "Bus fare", "Metro card recharge", "Auto rickshaw", "Taxi ride",
        "Fuel for scooter", "Bike maintenance", "Train ticket"
    ]),
    "Bills": (200, 3000, [
        "Electricity bill", "Water bill", "Internet bill", "Mobile recharge",
        "Gas cylinder", "Maintenance charges", "DTH subscription"
    ]),
    "Health": (100, 2000, [
        "Doctor consultation", "Medicines", "Gym membership", "Health checkup",
        "Physiotherapy", "Dental care", "Vitamins supplement"
    ]),
    "Entertainment": (100, 1500, [
        "Movie tickets", "Concert entry", "Streaming subscription",
        "Game purchase", "Amusement park", "Cricket match ticket"
    ]),
    "Shopping": (200, 5000, [
        "New clothes", "Shoes", "Electronics", "Home decor",
        "Birthday gift", "Furniture item", "Kitchen appliance"
    ]),
    "Other": (50, 1000, [
        "Miscellaneous", "Donation", "Stationery", "Pet supplies",
        "Car wash", "Laundry", "Haircut"
    ])
}

# Category distribution weights (Food most common, Health/Entertainment least)
CATEGORY_WEIGHTS = {
    "Food": 25,
    "Transport": 18,
    "Bills": 15,
    "Health": 8,
    "Entertainment": 10,
    "Shopping": 14,
    "Other": 10
}


def get_db_connection():
    """Opens connection to spendly.db with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def verify_user_exists(conn, user_id):
    """Check if user exists in the database."""
    cursor = conn.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


def generate_expense(user_id, months_ago):
    """Generate a single random expense."""
    # Select category based on weights
    category = random.choices(
        list(CATEGORY_WEIGHTS.keys()),
        weights=list(CATEGORY_WEIGHTS.values())
    )[0]

    min_amt, max_amt, descriptions = CATEGORIES[category]
    amount = round(random.uniform(min_amt, max_amt), 2)
    description = random.choice(descriptions)

    # Generate random date within the past 'months' months
    days_ago = random.randint(0, months_ago * 30)
    expense_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    return (user_id, amount, category, expense_date, description)


def seed_expenses(user_id, count, months):
    """Generate and insert expenses for a user."""
    conn = get_db_connection()

    # Verify user exists
    user = verify_user_exists(conn, user_id)
    if not user:
        print(f"No user found with id {user_id}.")
        conn.close()
        return None

    print(f"Seeding {count} expenses for {user['name']} (user_id={user_id})...")

    expenses = [generate_expense(user_id, months) for _ in range(count)]

    try:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, expenses)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error inserting expenses: {e}")
        conn.close()
        return None

    # Get date range of inserted expenses
    result = conn.execute("""
        SELECT MIN(date) as min_date, MAX(date) as max_date
        FROM expenses
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    # Get sample of 5 expenses
    sample = conn.execute("""
        SELECT id, amount, category, date, description
        FROM expenses
        WHERE user_id = ?
        ORDER BY RANDOM()
        LIMIT 5
    """, (user_id,)).fetchall()

    print(f"\nSuccessfully inserted {count} expenses")
    print(f"  Date range: {result['min_date']} to {result['max_date']}")
    print(f"\n  Sample expenses:")
    for exp in sample:
        print(f"    - Rs. {exp['amount']:.2f} ({exp['category']}) on {exp['date']}: {exp['description']}")

    conn.close()


def main():
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    seed_expenses(user_id, count, months)


if __name__ == "__main__":
    main()
