import sqlite3

conn = sqlite3.connect("expense.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")

users = cursor.fetchall()

print(users)      # <-- ye add karo

conn.close()