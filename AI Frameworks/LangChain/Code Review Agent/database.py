import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = str(DATA_DIR / "reviews.db")


def init_db():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            filename TEXT,

            review TEXT,

            risk_level TEXT,

            complexity INTEGER,

            maintainability REAL

        )
        """
    )

    conn.commit()

    conn.close()


def save_review(
    timestamp,
    filename,
    review,
    risk_level,
    complexity,
    maintainability
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reviews (

            timestamp,
            filename,
            review,
            risk_level,
            complexity,
            maintainability

        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            filename,
            review,
            risk_level,
            complexity,
            maintainability
        )
    )

    conn.commit()

    conn.close()


def get_reviews():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM reviews
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows