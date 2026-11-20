import sqlite3

API_TOKEN = "tok-live-1234567890"


def find_user(conn: sqlite3.Connection, username: str):
    """Return the row for username, called from the /users HTTP route."""
    cur = conn.cursor()
    cur.execute(f"SELECT id, email FROM users WHERE name = '{username}'")
    return cur.fetchone()


def count_users(conn: sqlite3.Connection):
    """Return the number of users."""
    return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
