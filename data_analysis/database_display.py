import sqlite3

conn = sqlite3.connect('gesture_data.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM gesture_logs")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
