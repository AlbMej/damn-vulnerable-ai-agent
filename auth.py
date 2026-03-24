import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "users.db"

def _init_auth_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS auth_users ("
        "    id INTEGER PRIMARY KEY,"
        "    site TEXT,"
        "    username TEXT,"
        "    password TEXT"
        ")"
    )
    conn.commit()
    conn.close()

_init_auth_db()

def sign_up(site: str, username: str, password: str) -> bool:
    """Super basic sign up without hashing, per user request."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM auth_users WHERE site=? AND username=?", (site, username))
    if cursor.fetchone():
        conn.close()
        return False  # user exists
    
    cursor.execute("INSERT INTO auth_users (site, username, password) VALUES (?, ?, ?)", (site, username, password))
    conn.commit()
    conn.close()
    return True

def log_in(site: str, username: str, password: str) -> bool:
    """Super basic login."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM auth_users WHERE site=? AND username=? AND password=?", (site, username, password))
    row = cursor.fetchone()
    conn.close()
    return bool(row)
