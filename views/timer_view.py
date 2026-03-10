import customtkinter as ctk
import os
import json
from config import DATA_DIR, logger, get_text
import controllers.blocker as blocker
import controllers.audio_player as audio

class TimerView(ctk.CTkFrame):
    def __init__(self, master, current_user, on_session_complete, on_pause_event):
        super().__init__(master)
        
        self.current_user = current_user
        self.on_session_complete = on_session_complete
        self.on_pause_event = on_pause_event
        
        self.settings = self.load_settings()
        self.pomodoro_cycle_count = 0
        
        self.time_left = self.settings["work_time"] * 60
        self.is_running = False
        self.is_break = False
        self.timer_id = None
        self.current_task = None
        
        # UI Elements
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.header_label = ctk.CTkLabel(self, text=get_text("focus_time"), font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, pady=(20, 10))
        
        self.task_label = ctk.CTkLabel(self, text=get_text("no_task_selected"), font=ctk.CTkFont(size=16), text_color="gray")
        self.task_label.grid(row=1, column=0, pady=(0, 20))
        
        mins, secs = divmod(self.time_left, 60)
        self.time_display = ctk.CTkLabel(self, text=f"{mins:02d}:{secs:02d}", font=ctk.CTkFont(size=80, weight="bold", family="Courier"))
        self.time_display.grid(row=2, column=0, pady=10)
        
        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, pady=20)
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text=get_text("start"), font=ctk.CTkFont(size=16, weight="bold"), width=100, height=40, command=self.toggle_timer)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.reset_btn = ctk.CTkButton(self.btn_frame, text=get_text("reset"), font=ctk.CTkFont(size=16), width=100, height=40, fg_color="gray", hover_color="darkgray", command=self.reset_timer)
        self.reset_btn.grid(row=0, column=1, padx=5)
        
        self.widget_btn = ctk.CTkButton(self.btn_frame, text=get_text("widget"), font=ctk.CTkFont(size=16), width=80, height=40, fg_color="#333333", hover_color="#555555", command=self.open_mini_widget)
        self.widget_btn.grid(row=0, column=2, padx=5)
        
        # Modes
        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.grid(row=4, column=0, pady=10)
        
        self.pomodoro_btn = ctk.CTkButton(self.mode_frame, text=get_text("pomodoro"), width=100, fg_color="#BB86FC" if ctk.get_appearance_mode()=="Dark" else "#6200EE", command=lambda: self.set_mode('work', False))
        self.pomodoro_btn.grid(row=0, column=0, padx=5)
        
        self.short_break_btn = ctk.CTkButton(self.mode_frame, text=get_text("short_break_mode"), width=100, fg_color="transparent", border_width=1, command=lambda: self.set_mode('short', True))
        self.short_break_btn.grid(row=0, column=1, padx=5)
        
        self.long_break_btn = ctk.CTkButton(self.mode_frame, text=get_text("long_break_mode"), width=100, fg_color="transparent", border_width=1, command=lambda: self.set_mode('long', True))
        self.long_break_btn.grid(row=0, column=2, padx=5)
        
        # Cycle info
        self.cycle_label = ctk.CTkLabel(self, text=f"{get_text('current_cycles')} {self.pomodoro_cycle_count} / {self.settings['cycles_before_long_break']}", text_color="gray", font=ctk.CTkFont(size=12))
        self.cycle_label.grid(row=5, column=0, pady=5)
        
    def load_settings(self):
        settings_file = os.path.join(DATA_DIR, 'settings.json')
        defaults = {"work_time": 25, "short_break": 5, "long_break": 15, "cycles_before_long_break": 4, "sound": True, "auto_start_break": False}
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    data = json.load(f)
                    defaults.update(data)
            except Exception: pass
        return defaults

    def update_task(self, task):
        self.current_task = task
        if task:
            self.task_label.configure(text=f"{get_text('current_task')} {task['title']}")
        else:
            self.task_label.configure(text=get_text("no_task_selected"))

    def toggle_timer(self):
        if not self.is_running:
            self.settings = self.load_settings()
            self.is_running = True
            self.start_btn.configure(text=get_text("pause"), fg_color="#CF6679", hover_color="#B00020")
            
            # --- Focus Mode Action ---
            if not self.is_break:
                # We removed the aggressive "minimize all" loop here because it incorrectly 
                # minimized the Pomodoro app itself and disrupted user workflow.
                self.winfo_toplevel().attributes('-fullscreen', True)
                self.winfo_toplevel().attributes('-topmost', True)
                
                # Turn on Strict Focus & Audio
                if self.settings.get("play_lofi", False):
                    audio.play_lofi()
                blocked_sites = self.settings.get("blocked_sites", "")
                if blocked_sites:
                    blocker.block_websites(blocked_sites)
                    
                # Start tracking active window titles for blocker
                self._enforce_focus_mode()
                
            self.run_timer()
        else:
            self.is_running = False
            self.on_pause_event()
            self.start_btn.configure(text=get_text("resume"), fg_color="#1f6aa5", hover_color="#144870")
            
            # Turn off focus mode constraints if paused
            self.winfo_toplevel().attributes('-fullscreen', False)
            self.winfo_toplevel().attributes('-topmost', False)
            
            audio.stop_lofi()
            blocker.unblock_websites(self.settings.get("blocked_sites", ""))
            
            if self.timer_id:
                self.after_cancel(self.timer_id)
            if hasattr(self, 'focus_enforcer_id') and self.focus_enforcer_id:
                self.after_cancel(self.focus_enforcer_id)

    def run_timer(self):
        if self.time_left > 0 and self.is_running:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.time_display.configure(text=time_str)
            
            # Update mini widget if it is open
            if hasattr(self, 'widget_time_label') and self.widget_time_label.winfo_exists():
                self.widget_time_label.configure(text=time_str)
                
            self.time_left -= 1
            self.timer_id = self.after(1000, self.run_timer)
        elif self.time_left == 0 and self.is_running:
            self.is_running = False
            self.time_display.configure(text="00:00")
            self.start_btn.configure(text=get_text("start"), fg_color="#1f6aa5")
            
            self.winfo_toplevel().attributes('-fullscreen', False)
            self.winfo_toplevel().attributes('-topmost', False)
            
            # Sound & Notification
            if self.settings.get("sound", True):
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
            
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast("Pomodoro Pro", get_text("timer_finished"), duration=5, threaded=True)
            except Exception:
                pass
                
            audio.stop_lofi()
            blocker.unblock_websites(self.settings.get("blocked_sites", ""))
            if hasattr(self, 'focus_enforcer_id') and self.focus_enforcer_id:
                self.after_cancel(self.focus_enforcer_id)
            
            # Smart Cycle Logic
            duration_minutes = self.settings["work_time"] if not self.is_break else self.settings["short_break"]
            
            if not self.is_break:
                self.pomodoro_cycle_count += 1
                self.cycle_label.configure(text=f"{get_text('current_cycles')} {self.pomodoro_cycle_count} / {self.settings['cycles_before_long_break']}")
                
                # Check if it's time for a Long Break
                if self.pomodoro_cycle_count >= self.settings["cycles_before_long_break"]:
                    self.pomodoro_cycle_count = 0
                    self.set_mode('long', True)
                else:
                    self.set_mode('short', True)
                    
                # Auto Start Check
                if self.settings.get("auto_start_break", False):
                    self.toggle_timer()
            else:
                self.set_mode('work', False)
            
            # Notify completion to master UI
            self.on_session_complete(duration_minutes, self.current_task, not self.is_break)

    def _enforce_focus_mode(self):
        if not self.is_running or self.is_break:
            return
            
        blocked_sites = self.settings.get("blocked_sites", "")
        if blocked_sites:
            try:
                import ctypes
                import controllers.blocker as blocker
                import uiautomation as auto
                
                keywords = blocker.extract_keywords(blocked_sites)
                
                if keywords:
                    EnumWindows = ctypes.windll.user32.EnumWindows
                    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
                    GetWindowText = ctypes.windll.user32.GetWindowTextW
                    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
                    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

                    def close_tab(hwnd, reason=""):
                        # Bring window to front safely without un-maximizing it
                        if ctypes.windll.user32.IsIconic(hwnd):
                            ctypes.windll.user32.ShowWindow(hwnd, 9) # SW_RESTORE only if minimized
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                        
                        # Press Ctrl+W to close the current tab
                        import pyautogui
                        import time
                        time.sleep(0.1) # Kichik tanaffus oyna oldinga chiqishi uchun
                        pyautogui.hotkey('ctrl', 'w')
                        logger.info(f"Ctrl+W yuborildi: {reason} yopilmoqda...")
                        
                        # Bring Pomodoro window back to front
                        main_win = self.winfo_toplevel()
                        if main_win.state() == 'iconic':
                            main_win.deiconify()
                        main_win.attributes('-topmost', True)
                        main_win.lift()

                    def foreach_window(hwnd, lParam):
                        if IsWindowVisible(hwnd):
                            length = GetWindowTextLength(hwnd)
                            if length > 0:
                                buff = ctypes.create_unicode_buffer(length + 1)
                                GetWindowText(hwnd, buff, length + 1)
                                title_lower = buff.value.lower()
                                
                                # Fast check: Is keyword in Window Title?
                                blocked = False
                                for kw in keywords:
                                    if kw in title_lower:
                                        logger.info(f"Bloklangan sayt aniqlandi (title): {title_lower} (mos keldi: {kw})")
                                        close_tab(hwnd, f"'{title_lower}' sarlavhasi")
                                        blocked = True
                                        break
                                        
                                # Deep check: If it's a browser, check address bar URL via UIAutomation
                                if not blocked and any(b in title_lower for b in ['chrome', 'edge', 'firefox', 'brave', 'yandex']):
                                    try:
                                        win = auto.WindowControl(Name=buff.value, searchDepth=1)
                                        if win.Exists(0, 0):
                                            edit = win.EditControl()
                                            if edit.Exists(0, 0):
                                                url = edit.GetValuePattern().Value.lower()
                                                for kw in keywords:
                                                    if kw in url:
                                                        logger.info(f"Bloklangan sayt aniqlandi (URL): {url} oynada: {title_lower} (mos keldi: {kw})")
                                                        close_tab(hwnd, f"URL '{url}'")
                                                        blocked = True
                                                        break
                                    except Exception as e:
                                        pass
                                
                                if blocked:
                                    return False # Stop enum
                        return True
                        
                    EnumWindows(EnumWindowsProc(foreach_window), 0)
            except Exception as e:
                logger.error(f"Oynani tekshirishda xato: {e}")
                
        # Schedule the next check
        if self.is_running and not self.is_break:
            self.focus_enforcer_id = self.after(2000, self._enforce_focus_mode)

    def reset_timer(self):
        self.is_running = False
        self.settings = self.load_settings() # reload settings dynamically
        
        self.winfo_toplevel().attributes('-fullscreen', False)
        self.winfo_toplevel().attributes('-topmost', False)
        
        if self.timer_id:
            self.after_cancel(self.timer_id)
        if hasattr(self, 'focus_enforcer_id') and self.focus_enforcer_id:
            self.after_cancel(self.focus_enforcer_id)
            
        audio.stop_lofi()
        blocker.unblock_websites(self.settings.get("blocked_sites", ""))
        
        if self.is_break:
            # We don't explicitly know here if it was short or long via simple check, but assume short for a blind reset unless otherwise
            self.time_left = self.settings["short_break"] * 60
        else:
            self.time_left = self.settings["work_time"] * 60
            
        mins, secs = divmod(self.time_left, 60)
        self.time_display.configure(text=f"{mins:02d}:{secs:02d}")
        self.start_btn.configure(text=get_text("start"), fg_color="#1f6aa5")
        
        self.cycle_label.configure(text=f"{get_text('current_cycles')} {self.pomodoro_cycle_count} / {self.settings['cycles_before_long_break']}")

    def set_mode(self, mode_name, is_break):
        self.settings = self.load_settings()
        self.is_break = is_break
        
        if mode_name == 'work':
            minutes = self.settings["work_time"]
        elif mode_name == 'short':
            minutes = self.settings["short_break"]
        else:
            minutes = self.settings["long_break"]
            
        self.time_left = minutes * 60
        self.reset_timer()
        self.time_left = minutes * 60 # Fix reset override
        mins, secs = divmod(self.time_left, 60)
        self.time_display.configure(text=f"{mins:02d}:{secs:02d}")
        
        # UI updates for buttons
        primary_color = "#BB86FC" if ctk.get_appearance_mode()=="Dark" else "#6200EE"
        
        if mode_name == 'work':
            self.header_label.configure(text=get_text("focus_time"))
            self.pomodoro_btn.configure(fg_color=primary_color, border_width=0)
            self.short_break_btn.configure(fg_color="transparent", border_width=1)
            self.long_break_btn.configure(fg_color="transparent", border_width=1)
        elif mode_name == 'short':
            self.header_label.configure(text=get_text("short_break_mode"))
            self.pomodoro_btn.configure(fg_color="transparent", border_width=1)
            self.short_break_btn.configure(fg_color=primary_color, border_width=0)
            self.long_break_btn.configure(fg_color="transparent", border_width=1)
        elif mode_name == 'long':
            self.header_label.configure(text=get_text("long_break_mode"))
            self.pomodoro_btn.configure(fg_color="transparent", border_width=1)
            self.short_break_btn.configure(fg_color="transparent", border_width=1)
            self.long_break_btn.configure(fg_color=primary_color, border_width=0)

    def open_mini_widget(self):
        # Hide Main Window
        main_win = self.winfo_toplevel()
        main_win.withdraw()
        
        # Create Mini Widget Window
        self.mini_widget = ctk.CTkToplevel(self)
        self.mini_widget.title(get_text("pomodoro_widget"))
        self.mini_widget.geometry("220x80+100+100") # Small size, fixed pos
        self.mini_widget.attributes('-topmost', True)
        self.mini_widget.overrideredirect(True) # Remove windows native borders
        self.mini_widget.configure(fg_color="#1E1E1E")
        
        # Allow dragging the widget
        def start_move(event):
            self.mini_widget.x = event.x
            self.mini_widget.y = event.y
            
        def stop_move(event):
            self.mini_widget.x = None
            self.mini_widget.y = None
            
        def do_move(event):
            x = self.mini_widget.winfo_x() - self.mini_widget.x + event.x
            y = self.mini_widget.winfo_y() - self.mini_widget.y + event.y
            self.mini_widget.geometry(f"+{x}+{y}")
            
        self.mini_widget.bind("<ButtonPress-1>", start_move)
        self.mini_widget.bind("<ButtonRelease-1>", stop_move)
        self.mini_widget.bind("<B1-Motion>", do_move)
        
        # Widget Layout
        self.mini_widget.grid_columnconfigure(0, weight=1)
        
        mins, secs = divmod(self.time_left, 60)
        self.widget_time_label = ctk.CTkLabel(self.mini_widget, text=f"{mins:02d}:{secs:02d}", font=ctk.CTkFont(size=24, weight="bold"))
        self.widget_time_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))
        
        def widget_toggle():
            self.toggle_timer()
            w_btn.configure(text=get_text("pause") if self.is_running else get_text("resume"))
            
        def restore_main():
            self.mini_widget.destroy()
            main_win.deiconify()
            main_win.state('zoomed')
        
        w_btn = ctk.CTkButton(self.mini_widget, text=get_text("pause") if self.is_running else get_text("resume"), width=60, height=24, command=widget_toggle)
        w_btn.grid(row=1, column=0, padx=5, pady=5)
        
        r_btn = ctk.CTkButton(self.mini_widget, text=get_text("maximize"), width=100, height=24, fg_color="#333333", command=restore_main)
        r_btn.grid(row=1, column=1, padx=5, pady=5)
