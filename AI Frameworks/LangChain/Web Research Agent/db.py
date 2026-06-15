import sqlite3


DB_NAME = "database/research.db"


def create_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS research_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            report TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def save_research(topic, report):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO research_history
        (topic, report)
        VALUES (?, ?)
        """,
        (topic, report)
    )

    conn.commit()
    conn.close()


def get_all_research():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
        id,
        topic,
        created_at
        FROM research_history
        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    conn.close()

    return data


def get_research_by_id(research_id):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT report
        FROM research_history
        WHERE id = ?
        """,
        (research_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result