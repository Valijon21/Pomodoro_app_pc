# Pomodoro Pro: Ultimate Productivity & Focus Timer 🍅

![Pomodoro App Banner](https://img.shields.io/badge/App-Pomodoro%20Pro-red?style=for-the-badge&logo=clock)
![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-brightgreen?style=for-the-badge)

**Pomodoro Pro** is a feature-rich, desktop-based productivity application built with Python and CustomTkinter. It is designed to help users manage their time efficiently using the Pomodoro Technique, keep track of their tasks, and aggressively remove digital distractions during focus sessions.

## 🚀 Key Features

*   **Customizable Pomodoro Timer**: Tailor your deep work (25 min default), short breaks (5 min), and long breaks (15 min) to your exact workflow.
*   **Aggressive Focus Blocker**: Enter distraction sites (e.g., `youtube.com`, `instagram`). The app intelligently detects if you open them in *any* browser during a focus session and instantly closes the distraction tab (`Ctrl + W`) to keep you on track.
*   **Task Management (To-Do)**: Add, edit, prioritize (High/Medium/Low), and tag tasks. Earn Experience Points (XP) and level up as you complete them!
*   **Multi-Language Support**: Fully localized in **Uzbek (UZ)**, **Russian (RU)**, and **English (EN)**. Change languages on the fly without breaking the layout.
*   **Auto-Login & Local Database**: Secure local SQLite database (`pomodoro.db`) with password hashing. Enjoy seamless Auto-Login via encrypted session tokens.
*   **Detailed Analytics**: Visual charts (via Matplotlib) track your daily/weekly focus minutes, best working hours, and tag distribution.
*   **Lo-Fi Audio Player**: Built-in ambient Lo-Fi player to keep you in the flow zone.

## 🛠️ Technology Stack

*   **Language**: Python 3.x
*   **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
*   **Database**: SQLite3 (Local storage)
*   **Distraction Blocking**: `pygetwindow`, `ctypes` (Win32 API), `pyautogui`
*   **Data Visualization**: `matplotlib`

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Valijon21/Pomodoro_app_pc.git
   cd Pomodoro_app_pc
   ```

2. **Create a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

## 🛡️ Distraction Blocker Logic
The built-in blocker uses an advanced regex-based domain parser to smartly identity websites regardless of how you input them (e.g., `youtube`, `https://www.youtube.com/watch?v=1`, or `instagram.com`). 
If the blocker is active and it detects the text in an active window title, it leverages the Win32 API to bring the window to the foreground and securely sends a `Ctrl+W` shortcut to terminate the tab immediately. 

## 🧪 Running Tests
The project includes professional unit testing to ensure robust functionality, specially for the regex domain extractor.
```bash
python -m unittest tests/test_blocker.py
```

## 📂 Project Structure

```text
Pomodoro_app_pc/
├── main.py                     # Application entry point & routing 
├── database.py                   # SQLite DB schemas and queries
├── config.py                     # App configurations and constants
├── controllers/                  
│   ├── blocker.py                # Focus mode website blocking logic
│   └── audio_player.py           # Lo-Fi music controller
├── views/                        # CustomTkinter UI Components
│   ├── login_view.py             # Auth screen
│   ├── main_view.py              # Main dashboard wrapper
│   ├── timer_view.py             # Core Pomodoro timer
│   ├── tasks_view.py             # Todo list manager
│   ├── stats_view.py             # Analytics and charts
│   └── settings_view.py          # Preferences and Language settings
├── data/                         # Local storage (ignored by git)
│   ├── translations.json         # UZ, RU, EN UI strings
│   ├── session.json              # Auto-login token
│   └── pomodoro.db               # SQLite database
├── tests/
│   └── test_blocker.py           # Unit tests
├── README.md
└── requirements.txt
```

---
*Built with ❤️ for ultimate productivity.*
