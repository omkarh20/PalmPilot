import serial
import time
import sqlite3
from datetime import datetime

arduino = serial.Serial('com4', 9600)
time.sleep(2) 

conn = sqlite3.connect('gesture_data.db')
cursor = conn.cursor()

def create_table():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gesture_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        gesture TEXT,
        left_distance INTEGER,
        right_distance INTEGER,
        ir_triggered INTEGER
    )
    ''')
    conn.commit()

create_table()

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cursor.execute('''
    INSERT INTO gesture_logs (timestamp, gesture, left_distance, right_distance, ir_triggered)
    VALUES (?, ?, ?, ?, ?)
''', (timestamp, "None", 0, 0, 0))
conn.commit()
print("Inserted initial default entry.\n")

print("Logging started. Press Ctrl+C to stop.\n")

try:
    while True:
        line = arduino.readline().decode('utf-8').strip()
        print("Serial Data:", line)
        
        try:
            data = line.split(',')
            if len(data) == 4:
                gesture = data[0]
                left_distance = int(data[1])
                right_distance = int(data[2])
                ir_triggered = int(data[3])
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    INSERT INTO gesture_logs (timestamp, gesture, left_distance, right_distance, ir_triggered)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, gesture, left_distance, right_distance, ir_triggered))
                conn.commit()
                print("✔ Logged:", gesture)
        except ValueError:
            print("Invalid data received:", line)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    conn.close()
    arduino.close()
