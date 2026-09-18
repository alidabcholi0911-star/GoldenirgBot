import sqlite3
import os
import random
import string
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.sqlite")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    return connection


def setup_database():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS codes ("
        "code TEXT PRIMARY KEY, "
        "type TEXT NOT NULL, "
        "content TEXT, "
        "file_id TEXT, "
        "caption TEXT, "
        "created_at INTEGER NOT NULL"
        ")"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS settings ("
        "key TEXT PRIMARY KEY, "
        "value TEXT"
        ")"
    )
    connection.commit()
    connection.close()


def get_code(code):
    normalized_code = code.strip().upper()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT code, type, content, file_id, caption FROM codes WHERE code = ?", (normalized_code,))
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    result = {
        "code": row[0],
        "type": row[1],
        "content": row[2],
        "file_id": row[3],
        "caption": row[4],
    }
    return result


def generate_code():
    characters = string.ascii_uppercase + string.digits
    while True:
        random_part = "".join(random.choices(characters, k=8))
        candidate = "GOLDENORG_" + random_part
        existing = get_code(candidate)
        if existing is None:
            return candidate


def save_code(content_type, content=None, file_id=None, caption=None):
    code = generate_code()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO codes (code, type, content, file_id, caption, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (code, content_type, content, file_id, caption, int(time.time())),
    )
    connection.commit()
    connection.close()
    return code


def get_setting(key):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    return row[0]


def set_setting(key, value):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    connection.commit()
    connection.close()


setup_database()
