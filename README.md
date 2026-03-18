# Pomodoro Pro: Ultimate Productivity & Focus Timer 🍅

![Pomodoro App Banner](https://img.shields.io/badge/App-Pomodoro%20Pro-red?style=for-the-badge&logo=clock)
![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-brightgreen?style=for-the-badge)

**Pomodoro Pro** is a feature-rich, desktop-based productivity application built with Python and CustomTkinter. It is designed to help users manage their time efficiently using the Pomodoro Technique, keep track of their tasks, and aggressively remove digital distractions during focus sessions.

## 🚀 Key Features

*   **Customizable Pomodoro Timer**: Tailor your deep work (25 min default), short breaks (5 min), and long breaks (15 min) to your exact workflow.
*   **Unbreakable Focus Blocker (V3)**: Enter distraction sites (e.g., `youtube.com`, `kun.uz`). The app intelligently scans the active browser's **Address Bar (URL)** using `uiautomation` to instantly close distraction tabs (`Ctrl + W`) regardless of their article or window titles. Seamlessly brings your Pomodoro timer back to Fullscreen.
*   **Task Management (To-Do)**: Add, edit, prioritize (High/Medium/Low), and tag tasks. Earn Experience Points (XP) and level up as you complete them!
*   **Multi-Language Support**: Fully localized in **Uzbek (UZ)**, **Russian (RU)**, and **English (EN)** with professional corrections.
*   **Adjustable Font Size**: Globally scale the UI text size (10px to 24px) for perfect readability on any monitor.
*   **Analytics & AI**: Visual charts track focus minutes and best working hours, plus AI-powered productivity recommendations.
*   **Lo-Fi & Custom Music**: Built-in ambient Lo-Fi player or **select your own MP3 files** for a personalized flow state.

## 🛠️ Technology Stack

*   **Language**: Python 3.x
*   **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
*   **Database**: SQLite3 (Local storage)
*   **Distraction Blocking**: `uiautomation` (Address Bar Scanning), `pygetwindow`, `ctypes` (Win32 API), `pyautogui`
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
The built-in blocker uses an advanced regex-based domain parser and `uiautomation` to smoothly fetch the active URL from your browser's address bar (Chrome, Edge, Firefox).
If the blocker is active and the URL matches your blocked sites, it cleanly brings the tab to the foreground and securely sends a `Ctrl+W` shortcut to terminate the tab immediately without disrupting the browser's maximized geometry or the main app.

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
**Developer**: Valijon Ergashev

*Built with ❤️ for ultimate productivity.*
