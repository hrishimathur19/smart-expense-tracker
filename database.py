import sqlite3

conn = sqlite3.connect("expense.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    amount REAL,
    date TEXT,
    description TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")