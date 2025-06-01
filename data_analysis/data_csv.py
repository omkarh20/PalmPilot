import sqlite3
import pandas as pd

conn = sqlite3.connect('gesture_data.db')

df = pd.read_sql_query("SELECT * FROM gesture_logs", conn)

df.to_csv('gesture_data.csv', index=False)

conn.close()

print("CSV file 'gesture_data.csv' created successfully.")
