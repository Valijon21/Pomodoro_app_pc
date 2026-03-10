import customtkinter as ctk
import json
import os
from tkinter import messagebox
from config import DATA_DIR, logger, get_text

class SettingsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.settings_file = os.path.join(DATA_DIR, 'settings.json')
        self.settings = self.load_settings()
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_label = ctk.CTkLabel(self, text=get_text("settings_title"), font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, pady=(20, 20))
        
        # Form Container
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, pady=10)
        
        # Time Settings
        self.work_time_var = ctk.StringVar(value=str(self.settings.get("work_time", 25)))
        self.short_break_var = ctk.StringVar(value=str(self.settings.get("short_break", 5)))
        self.long_break_var = ctk.StringVar(value=str(self.settings.get("long_break", 15)))
        self.cycles_var = ctk.StringVar(value=str(self.settings.get("cycles_before_long_break", 4)))
        self.create_input(self.form_frame, 0, get_text("work_time"), self.work_time_var)
        self.create_input(self.form_frame, 1, get_text("short_break"), self.short_break_var)
        self.create_input(self.form_frame, 2, get_text("long_break"), self.long_break_var)
        self.create_input(self.form_frame, 3, get_text("cycles"), self.cycles_var)
        
        # Toggles
        self.sound_var = ctk.BooleanVar(value=self.settings.get("sound", True))
        self.auto_break_var = ctk.BooleanVar(value=self.settings.get("auto_start_break", False))
        self.lofi_var = ctk.BooleanVar(value=self.settings.get("play_lofi", False))
        
        self.sound_switch = ctk.CTkSwitch(self.form_frame, text=get_text("sound"), variable=self.sound_var)
        self.sound_switch.grid(row=4, column=0, pady=15, sticky="w")
        
        self.auto_break_switch = ctk.CTkSwitch(self.form_frame, text=get_text("auto_break"), variable=self.auto_break_var)
        self.auto_break_switch.grid(row=5, column=0, pady=5, sticky="w")
        
        self.lofi_switch = ctk.CTkSwitch(self.form_frame, text=get_text("lofi"), variable=self.lofi_var)
        self.lofi_switch.grid(row=4, column=1, pady=15, padx=20, sticky="w")
        
        # Blocked Sites Input
        ctk.CTkLabel(self.form_frame, text=get_text("blocked_sites_label"), font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, columnspan=2, pady=(20, 5), sticky="w")
        self.blocked_sites_var = ctk.StringVar(value=self.settings.get("blocked_sites", "youtube.com, instagram.com, tiktok.com"))
        self.blocked_sites_entry = ctk.CTkEntry(self.form_frame, textvariable=self.blocked_sites_var, width=400)
        self.blocked_sites_entry.grid(row=7, column=0, columnspan=2, pady=5, sticky="w", ipadx=5)
        
        # Language Selector
        ctk.CTkLabel(self.form_frame, text=get_text("language_label"), font=ctk.CTkFont(weight="bold")).grid(row=8, column=0, pady=(20, 5), sticky="w")
        self.lang_var = ctk.StringVar(value=self.settings.get("language", "uz"))
        self.lang_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.lang_var, values=["uz", "ru", "en"], width=100)
        self.lang_menu.grid(row=8, column=1, pady=(20, 5), sticky="w")
        
        # Save Button
        self.save_btn = ctk.CTkButton(self.form_frame, text=get_text("save_btn"), font=ctk.CTkFont(weight="bold"), fg_color="#03DAC6", text_color="black", hover_color="#018786", command=self.save_settings)
        self.save_btn.grid(row=9, column=0, columnspan=2, pady=30, ipadx=20, ipady=5)

    def create_input(self, parent, row, label_text, var):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", pady=10, padx=10)
        entry = ctk.CTkEntry(parent, textvariable=var, width=80)
        entry.grid(row=row, column=1, sticky="e", pady=10, padx=10)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error("Sozlamalar o'qishda xatolik", exc_info=True)
            
        return {
            "work_time": 25,
            "short_break": 5,
            "long_break": 15,
            "cycles_before_long_break": 4,
            "sound": True,
            "auto_start_break": False,
            "play_lofi": False,
            "blocked_sites": "youtube.com, instagram.com, tiktok.com, facebook.com",
            "language": "uz"
        }

    def save_settings(self):
        try:
            new_settings = {
                "work_time": int(self.work_time_var.get()),
                "short_break": int(self.short_break_var.get()),
                "long_break": int(self.long_break_var.get()),
                "cycles_before_long_break": int(self.cycles_var.get()),
                "sound": self.sound_var.get(),
                "auto_start_break": self.auto_break_var.get(),
                "play_lofi": self.lofi_var.get(),
                "blocked_sites": self.blocked_sites_var.get(),
                "language": self.lang_var.get()
            }
            with open(self.settings_file, "w") as f:
                json.dump(new_settings, f, indent=4)
                
            # Update current language in config
            import config
            config.CURRENT_LANGUAGE = self.lang_var.get()
                
            messagebox.showinfo(get_text("saved_title"), get_text("saved_msg"), parent=self.winfo_toplevel())
            logger.info("Foydalanuvchi sozlamalari yangilandi.")
            
            # Refresh the UI dynamically so they don't have to restart
            app = self.winfo_toplevel()
            if hasattr(app, 'show_main_app'):
                app.show_main_app()
                try:
                    app.tabview.set(get_text("tab_settings"))
                except Exception:
                    pass
            
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("error_number"), parent=self.winfo_toplevel())
        except Exception as e:
            logger.error("Sozlamalarni saqlashda xato", exc_info=True)
            messagebox.showerror(get_text("error"), get_text("error_save"), parent=self.winfo_toplevel())
