import sqlite3
from typing import List, Dict, Optional
import os
import hashlib
import json
from config import DB_PATH, DATA_DIR, logger

SESSION_FILE = os.path.join(DATA_DIR, 'session.json')

def get_connection():
    # Make sure the data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium', -- High, Medium, Low
            status TEXT DEFAULT 'Pending', -- Pending, Done
            pomodoro_count INTEGER DEFAULT 0,
            tag TEXT DEFAULT 'General',     -- Tags
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Try adding tag column if it doesn't exist (for existing DBs)
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN tag TEXT DEFAULT 'General'")
    except sqlite3.OperationalError:
        pass
    
    # Create Pomodoro Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_id INTEGER,
            duration_minutes INTEGER,
            focus_time_percentage REAL,
            start_time TIMESTAMP,
            end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# User Management
def create_user(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> Optional[Dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def update_user_xp(user_id: int, xp_gained: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = xp + ? WHERE id = ?", (xp_gained, user_id))
    
    # Basic level calc: level = 1 + (xp // 100)
    cursor.execute("SELECT xp FROM users WHERE id = ?", (user_id,))
    current_xp = cursor.fetchone()[0]
    new_level = 1 + (current_xp // 100)
    
    cursor.execute("UPDATE users SET level = ? WHERE id = ?", (new_level, user_id))
    conn.commit()
    conn.close()

# Task Management
def add_task(user_id: int, title: str, priority: str = 'Medium', tag: str = 'General'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, title, priority, tag) VALUES (?, ?, ?, ?)", (user_id, title, priority, tag))
    conn.commit()
    conn.close()

def get_tasks(user_id: int) -> List[Dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, created_at DESC", (user_id,))
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks

def update_task_status(task_id: int, status: str, user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()
    
    # Give XP if marked as done
    if status == "Done" and user_id:
        update_user_xp(user_id, 30) # 30 XP for completing a task

def increment_task_pomodoro(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET pomodoro_count = pomodoro_count + 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# Session Management
def add_session(user_id: int, task_id: Optional[int], duration: int, focus_percent: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pomodoro_sessions (user_id, task_id, duration_minutes, focus_time_percentage)
        VALUES (?, ?, ?, ?)
    """, (user_id, task_id, duration, focus_percent))
    conn.commit()
    conn.close()

# Initialize if run directly
if __name__ == "__main__":
    init_db()
    print("Database initialized.")

def get_best_working_hours(user_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%H', start_time) as hr, SUM(duration_minutes) as m
        FROM pomodoro_sessions
        WHERE user_id = ? AND start_time IS NOT NULL
        GROUP BY hr
        ORDER BY m DESC LIMIT 1
    """, (user_id,))
    res = cursor.fetchone()
    conn.close()
    
    if res and res[0]:
        hr = int(res[0])
        return f"{hr}:00 - {hr+1}:00"
    return "Hali noma'lum"

# Analytics
def get_weekly_stats(user_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date as session_date, SUM(duration_minutes) as total_minutes 
        FROM pomodoro_sessions 
        WHERE user_id = ? AND date >= date('now', '-7 days')
        GROUP BY date
        ORDER BY date ASC
    """, (user_id,))
    stats = [{"date": row[0], "minutes": row[1]} for row in cursor.fetchall()]
    conn.close()
    return stats

def get_tag_distribution(user_id: int) -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(t.tag, 'General') as tag_name, SUM(ps.duration_minutes) as total_min
        FROM pomodoro_sessions ps
        LEFT JOIN tasks t ON ps.task_id = t.id
        WHERE ps.user_id = ?
        GROUP BY tag_name
    """, (user_id,))
    dist = {row[0]: row[1] for row in cursor.fetchall() if row[1] and row[1] > 0}
    conn.close()
    return dist

def get_overall_stats(user_id: int) -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total Pomodoros & Minutes
    cursor.execute("SELECT COUNT(*), SUM(duration_minutes) FROM pomodoro_sessions WHERE user_id = ?", (user_id,))
    total_res = cursor.fetchone()
    total_sessions = total_res[0] or 0
    total_minutes = total_res[1] or 0
    
    # Best Day
    cursor.execute("""
        SELECT date, SUM(duration_minutes) as m 
        FROM pomodoro_sessions 
        WHERE user_id = ? 
        GROUP BY date 
        ORDER BY m DESC LIMIT 1
    """, (user_id,))
    best_res = cursor.fetchone()
    best_day = best_res[0] if best_res else "N/A"
    
    conn.close()
    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "best_day": best_day,
        "average_per_day": round(total_minutes / max(1, len(get_weekly_stats(user_id))), 1) if total_sessions > 0 else 0
    }

def get_all_sessions_for_export(user_id: int) -> List[Dict]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            ps.date, 
            ps.start_time, 
            ps.end_time, 
            ps.duration_minutes, 
            COALESCE(t.title, 'Erkin Ish (Task siz)') as task_title,
            COALESCE(t.tag, 'General') as task_tag,
            COALESCE(t.priority, 'N/A') as task_priority
        FROM pomodoro_sessions ps
        LEFT JOIN tasks t ON ps.task_id = t.id
        WHERE ps.user_id = ?
        ORDER BY ps.date DESC, ps.start_time DESC
    """, (user_id,))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

def save_session(user: Dict):
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(user, f)
        logger.info("Session saved successfully.")
    except Exception as e:
        logger.error("Failed to save session", exc_info=True)

def get_saved_session() -> Optional[Dict]:
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                user = json.load(f)
                logger.info("Saved session loaded.")
                return user
        except Exception as e:
            logger.error("Failed to load saved session", exc_info=True)
            pass
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
            logger.info("Session cleared successfully.")
        except Exception as e:
            logger.error("Failed to clear session", exc_info=True)
