import sqlite3
from pathlib import Path


DB_PATH = Path("database/reports.db")

DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


def initialize_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        topic TEXT,

        created_at TEXT,

        markdown_path TEXT,

        pdf_path TEXT,

        report TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_report(
    topic,
    markdown_path,
    pdf_path,
    report
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reports
        (
            topic,
            created_at,
            markdown_path,
            pdf_path,
            report
        )
        VALUES
        (
            ?,
            datetime('now'),
            ?,
            ?,
            ?
        )
        """,
        (
            topic,
            markdown_path,
            pdf_path,
            report
        )
    )

    conn.commit()
    conn.close()