

import sqlite3

conn = sqlite3.connect("expense.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM expenses")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()