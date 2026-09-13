import sqlite3
import os
import random
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
    connection.commit()
    connection.close()


def get_code(code):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT code, type, content, file_id, caption FROM codes WHERE code = ?", (code,))
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
    while True:
        candidate = str(random.randint(100000, 999999))
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


setup_database()
