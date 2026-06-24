import sqlite3

DB_NAME = "startup_history.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startup_idea TEXT NOT NULL,
        business_type TEXT,
        audience TEXT,
        report TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_validation(
    startup_idea,
    business_type,
    audience,
    report
):
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO validations
        (
            startup_idea,
            business_type,
            audience,
            report
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            startup_idea,
            business_type,
            audience,
            str(report)
        )
    )

    conn.commit()
    conn.close()


def get_all_validations():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM validations
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_top_startups():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT startup_idea,
               created_at
        FROM validations
        ORDER BY id DESC
        LIMIT 10
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows