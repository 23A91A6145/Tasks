import sqlite3


conn = sqlite3.connect(
    "database/etl.db"
)

cursor = conn.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM iris_data"
)

count = cursor.fetchone()[0]

print(
    f"Rows In Database: {count}"
)

conn.close()