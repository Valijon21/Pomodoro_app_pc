import sqlite3
import datetime

conn = sqlite3.connect('C:/Users/nout.plus/Desktop/Proyekt/pomodoro/data/pomodoro.db')
cursor = conn.cursor()

user_id = 3 # 'vali'

# Check if data already exists to avoid duplicates
cursor.execute("SELECT COUNT(*) FROM pomodoro_sessions WHERE user_id = ?", (user_id,))
if cursor.fetchone()[0] == 0:
    data = [
        ('2026-02-27', 25),   # 1 pomodoro
        ('2026-02-28', 50),   # 2 pomodoros
        ('2026-03-01', 120),  # etc
        ('2026-03-02', 75),
        ('2026-03-03', 150),
        ('2026-03-04', 200),
        ('2026-03-05', 50)
    ]
    
    for d, m in data:
        # Split into individual 25min chunks for realism
        chunks = m // 25
        for i in range(chunks):
            start_hour = 9 + i
            time_str = f"{d} {start_hour:02d}:00:00"
            cursor.execute("""
                INSERT INTO pomodoro_sessions (user_id, task_id, duration_minutes, focus_time_percentage, start_time, end_time, date)
                VALUES (?, NULL, 25, 100.0, ?, ?, ?)
            """, (user_id, time_str, f"{d} {start_hour:02d}:25:00", d))

    # set level and xp
    # 670 minutes total = 6700 XP
    cursor.execute("UPDATE users SET xp = 6700, level = 68 WHERE id = ?", (user_id,))
    conn.commit()
    print("Mock data inserted successfully!")
else:
    print("Data already exists.")
conn.close()
