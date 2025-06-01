import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect('gesture_data.db')
df = pd.read_sql_query("SELECT * FROM gesture_logs", conn)
conn.close()

#1.Gesture Frequency Count
plt.figure(figsize=(8,5))
sns.countplot(data=df, x='gesture', order=df['gesture'].value_counts().index)
plt.title('Gesture Frequency')
plt.xlabel('Gesture Type')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('gesture_frequency.png')
plt.show()

#2.IR Triggered Events
plt.figure(figsize=(5,4))
sns.countplot(data=df, x='ir_triggered')
plt.title('IR Trigger Events')
plt.xlabel('IR Triggered')
plt.ylabel('Count')
plt.xticks([0, 1], ['Triggered', 'Not Triggered'])
plt.tight_layout()
plt.savefig('ir_triggered_counts.png')
plt.show()

#3.Left Distance vs Instance (for Lpush and Lpull)
left_df = df[df['gesture'].isin(['Lpush', 'Lpull'])].copy()
left_df['instance'] = range(1, len(left_df) + 1)

plt.figure(figsize=(8,5))
sns.lineplot(data=left_df, x='instance', y='left_distance', hue='gesture', marker='o')
plt.title('Left Distance for Lpush and Lpull')
plt.xlabel('Instance Number')
plt.ylabel('Left Distance (cm)')
plt.tight_layout()
plt.savefig('left_distance_lpush_lpull.png')
plt.show()

#4.Right Distance vs Instance (for Rpush and Rpull)
right_df = df[df['gesture'].isin(['Rpush', 'Rpull'])].copy()
right_df['instance'] = range(1, len(right_df) + 1)

plt.figure(figsize=(8,5))
sns.lineplot(data=right_df, x='instance', y='right_distance', hue='gesture', marker='o')
plt.title('Right Distance for Rpush and Rpull')
plt.xlabel('Instance Number')
plt.ylabel('Right Distance (cm)')
plt.tight_layout()
plt.savefig('right_distance_rpush_rpull.png')
plt.show()

#5.Combined Line - Lpush and Lpull
plt.figure(figsize=(8,5))
plt.plot(left_df['instance'], left_df['left_distance'], color='gray', linewidth=2, label='Combined Line')
sns.scatterplot(data=left_df, x='instance', y='left_distance', hue='gesture', palette={'Lpush': 'blue', 'Lpull': 'red'})
plt.title('Left Distance - Combined Line with Lpush/Lpull Points')
plt.xlabel('Instance Number')
plt.ylabel('Left Distance (cm)')
plt.legend()
plt.tight_layout()
plt.savefig('left_combined_line_lpush_lpull.png')
plt.show()

#6.Combined Line - Rpush and Rpull
plt.figure(figsize=(8,5))
plt.plot(right_df['instance'], right_df['right_distance'], color='gray', linewidth=2, label='Combined Line')
sns.scatterplot(data=right_df, x='instance', y='right_distance', hue='gesture', palette={'Rpush': 'green', 'Rpull': 'orange'})
plt.title('Right Distance - Combined Line with Rpush/Rpull Points')
plt.xlabel('Instance Number')
plt.ylabel('Right Distance (cm)')
plt.legend()
plt.tight_layout()
plt.savefig('right_combined_line_rpush_rpull.png')
plt.show()
