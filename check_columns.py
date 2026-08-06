import sqlite3

conn = sqlite3.connect("expense.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(expenses)")

for column in cursor.fetchall():
    print(column)

conn.close()