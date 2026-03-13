import customtkinter as ctk
import os
from views.login_view import LoginView
from database import init_db
from config import DEFAULT_THEME, logger, get_text
import traceback

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.error("Failed to initialize database", exc_info=True)

# Setup default appearance
ctk.set_appearance_mode(DEFAULT_THEME)  # Modes: "System", "Dark", "Light" -> uses .env
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PomodoroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.report_callback_exception = self.handle_exception

        
        self.title(get_text("login_title"))
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        # Oynani to'liq ekranga yoyib (maximize) ochish
        self.after(0, lambda: self.state('zoomed'))
        
        self.current_user = None
        
        # Handle window close cleanly
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window
        self.center_window()
        
        # Start looking like login
        from database import get_saved_session
        saved_user = get_saved_session()
        if saved_user:
            logger.info(f"Auto-login found for user: {saved_user['username']}")
            self.on_login_success(saved_user)
        else:
            self.show_login()
        
    def on_closing(self):
        # Stop background tasks and close cleanly
        try:
            # Stop timer if it's running
            if hasattr(self, 'timer_view') and self.timer_view:
                self.timer_view.is_running = False
                if self.timer_view.timer_id:
                    self.timer_view.after_cancel(self.timer_view.timer_id)
                    
            # Cancel ALL pending after callbacks from custom_tkinter
            for after_id in self.tk.call('after', 'info'):
                self.after_cancel(after_id)
        except Exception:
            pass
            
        # Destroy the main application window
        self.destroy()
        
        # Explicitly exit to definitively stop python process
        import sys
        sys.exit(0)
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = self.winfo_height()
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def show_login(self):
        self.clear_window()
        self.login_view = LoginView(self, self.on_login_success)
        self.login_view.pack(fill="both", expand=True)
        
    def on_login_success(self, user):
        from database import save_session
        save_session(user)
        self.current_user = user
        logger.info(f"User logged in: {user['username']}")
        self.show_main_app()
        
    def show_main_app(self):
        self.clear_window()
        
        # Header Area
        header = ctk.CTkFrame(self, height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        user_info = f"👤 {self.current_user['username']}  |  🏆 {get_text('level')}: {self.current_user['level']}  |  ⚡ {get_text('xp')}: {self.current_user['xp']}"
        from config import FONT_SIZE
        ctk.CTkLabel(header, text=user_info, font=ctk.CTkFont(size=FONT_SIZE + 2, weight="bold")).pack(side="left", padx=20, pady=10)
        
        def do_logout():
            from database import clear_session
            clear_session()
            logger.info("User logged out explicitly.")
            self.current_user = None
            self.show_login()
            
        logout_btn = ctk.CTkButton(header, text=get_text("logout_btn"), width=70, fg_color="#CF6679", hover_color="#B00020", command=do_logout)
        logout_btn.pack(side="right", padx=15, pady=10)
        
        # Theme Selector
        themes_map = {
            get_text("theme_system"): "System",
            get_text("theme_dark"): "Dark",
            get_text("theme_light"): "Light",
            get_text("theme_amoled"): "AMOLED"
        }
        
        def change_theme(ui_theme):
            internal_theme = themes_map.get(ui_theme, "Dark")
            if internal_theme == "AMOLED":
                ctk.set_appearance_mode("Dark")
            else:
                ctk.set_appearance_mode(internal_theme)
                
        theme_menu = ctk.CTkOptionMenu(header, values=list(themes_map.keys()), command=change_theme, width=90)
        theme_menu.pack(side="right", padx=10, pady=10)
        theme_menu.set(get_text("theme_dark"))
        
        # Content Split Layout with Tabs
        self.tabview = ctk.CTkTabview(self, fg_color="transparent")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_home = self.tabview.add(get_text("tab_dashboard"))
        self.tab_stats = self.tabview.add(get_text("tab_analytics"))
        self.tab_settings = self.tabview.add(get_text("tab_settings"))
        self.tab_home.grid_columnconfigure(0, weight=1)
        self.tab_home.grid_columnconfigure(1, weight=1)
        self.tab_home.grid_rowconfigure(0, weight=1)
        
        # Views Imports
        from views.timer_view import TimerView
        from views.tasks_view import TasksView
        from views.stats_view import StatsView
        from views.settings_view import SettingsView
        
        # Add Timer Left
        self.timer_view = TimerView(self.tab_home, self.current_user, self.on_session_complete, self.on_timer_pause)
        self.timer_view.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Add Tasks Right
        self.tasks_view = TasksView(self.tab_home, self.current_user, self.on_task_select)
        self.tasks_view.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Analytics View
        self.tab_stats.grid_columnconfigure(0, weight=1)
        self.tab_stats.grid_rowconfigure(0, weight=1)
        self.stats_view = StatsView(self.tab_stats, self.current_user)
        self.stats_view.grid(row=0, column=0, sticky="nsew")
        
        # Settings View
        self.tab_settings.grid_columnconfigure(0, weight=1)
        self.tab_settings.grid_rowconfigure(0, weight=1)
        self.settings_view = SettingsView(self.tab_settings)
        self.settings_view.grid(row=0, column=0, sticky="nsew")

    def on_task_select(self, task):
        self.timer_view.update_task(task)

    def on_timer_pause(self):
        pass # Pause logging logic here later
        
    def on_session_complete(self, duration_minutes, task, is_focus):
        from database import add_session, update_user_xp, increment_task_pomodoro, get_connection
        from tkinter import messagebox
        import json, random, os
        from config import DATA_DIR
        
        task_id = task['id'] if task else None
        
        if is_focus:
            # Save session
            add_session(self.current_user['id'], task_id, duration_minutes, 100.0)
            
            # Gamification XP update (10 XP per minute)
            xp_gained = duration_minutes * 10
            update_user_xp(self.current_user['id'], xp_gained)
            
            # Task update
            if task_id:
                increment_task_pomodoro(task_id)
                self.tasks_view.refresh_tasks()
                
            # Fetch updated user details for UI refresh
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT level, xp FROM users WHERE id = ?", (self.current_user['id'],))
            res = cursor.fetchone()
            conn.close()
            
            if res:
                self.current_user['level'] = res[0]
                self.current_user['xp'] = res[1]
                
            # Refresh header & stats
            self.show_main_app()
            
            # Load motivational quote
            try:
                with open(os.path.join(DATA_DIR, "quotes.json"), "r", encoding="utf-8") as f:
                    quotes = json.load(f)
                    quote = random.choice(quotes)
            except Exception:
                quote = get_text("quote_default")
                
            msg = f"{get_text('pomodoro_finished_msg_1')} {duration_minutes} {get_text('pomodoro_finished_msg_2')} +{xp_gained} {get_text('pomodoro_finished_msg_3')}\n\n💡 \"{quote}\""
            messagebox.showinfo(get_text("pomodoro_finished"), msg, parent=self.winfo_toplevel())
        
    def handle_exception(self, exc_type, exc_value, traceback_obj):
        logger.error("UI Xatolik yuz berdi:", exc_info=(exc_type, exc_value, traceback_obj))
        
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    try:
        logger.info("Pomodoro App is starting...")
        app = PomodoroApp()
        app.mainloop()
    except Exception as e:
        logger.critical("Kutilmagan xatolik bilan yopildi!", exc_info=True)
