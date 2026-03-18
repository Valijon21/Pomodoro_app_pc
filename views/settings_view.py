import customtkinter as ctk
import json
import os
from tkinter import filedialog, messagebox
from config import DATA_DIR, logger, get_text, FONT_SIZE

class SettingsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.settings_file = os.path.join(DATA_DIR, 'settings.json')
        self.settings = self.load_settings()
        
        # Header (Fixed at top)
        self.header_label = ctk.CTkLabel(self, text=get_text("settings_title"), font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=(20, 10))
        
        # Use a Scrollable Frame for the form to prevent clipping
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Form Container inside scrollable frame
        self.form_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=20)
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # Time Settings
        self.work_time_var = ctk.StringVar(value=str(self.settings.get("work_time", 25)))
        self.short_break_var = ctk.StringVar(value=str(self.settings.get("short_break", 5)))
        self.long_break_var = ctk.StringVar(value=str(self.settings.get("long_break", 15)))
        self.cycles_var = ctk.StringVar(value=str(self.settings.get("cycles_before_long_break", 4)))
        self.font_size_var = ctk.IntVar(value=self.settings.get("font_size", 14))
        self.music_path_var = ctk.StringVar(value=self.settings.get("custom_music_path", ""))
        
        self.create_input(self.form_frame, 0, get_text("work_time"), self.work_time_var)
        self.create_input(self.form_frame, 1, get_text("short_break"), self.short_break_var)
        self.create_input(self.form_frame, 2, get_text("long_break"), self.long_break_var)
        self.create_input(self.form_frame, 3, get_text("cycles"), self.cycles_var)
        
        # Font Size Slider
        ctk.CTkLabel(self.form_frame, text=get_text("font_size_label"), font=ctk.CTkFont(size=FONT_SIZE, weight="bold")).grid(row=4, column=0, sticky="w", pady=10, padx=10)
        self.font_slider = ctk.CTkSlider(self.form_frame, from_=10, to=24, number_of_steps=14, variable=self.font_size_var)
        self.font_slider.grid(row=4, column=1, sticky="w", pady=10, padx=10)
        self.font_size_label_val = ctk.CTkLabel(self.form_frame, textvariable=self.font_size_var, font=ctk.CTkFont(size=FONT_SIZE))
        self.font_size_label_val.grid(row=4, column=1, sticky="e", padx=(0, 0))
        
        # Toggles
        self.sound_var = ctk.BooleanVar(value=self.settings.get("sound", True))
        self.auto_break_var = ctk.BooleanVar(value=self.settings.get("auto_start_break", False))
        self.lofi_var = ctk.BooleanVar(value=self.settings.get("play_lofi", False))
        
        self.sound_switch = ctk.CTkSwitch(self.form_frame, text=get_text("sound"), variable=self.sound_var, font=ctk.CTkFont(size=FONT_SIZE))
        self.sound_switch.grid(row=5, column=0, pady=15, sticky="w")
        
        self.auto_break_switch = ctk.CTkSwitch(self.form_frame, text=get_text("auto_break"), variable=self.auto_break_var, font=ctk.CTkFont(size=FONT_SIZE))
        self.auto_break_switch.grid(row=6, column=0, pady=10, sticky="w")
        
        self.lofi_switch = ctk.CTkSwitch(self.form_frame, text=get_text("lofi"), variable=self.lofi_var, font=ctk.CTkFont(size=FONT_SIZE))
        self.lofi_switch.grid(row=6, column=1, pady=10, padx=20, sticky="w")
        
        # Custom Music Picker (grouped with Lo-Fi)
        music_frame = ctk.CTkFrame(self.form_frame, fg_color="gray20" if ctk.get_appearance_mode()=="Dark" else "gray90")
        music_frame.grid(row=7, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.music_btn = ctk.CTkButton(music_frame, text=get_text("select_music_btn"), font=ctk.CTkFont(size=FONT_SIZE, weight="bold"), command=self.select_custom_music, width=200)
        self.music_btn.pack(side="left", padx=10, pady=10)
        
        self.music_label = ctk.CTkLabel(music_frame, text=self.get_music_display_text(), font=ctk.CTkFont(size=FONT_SIZE-2), text_color="#BB86FC" if ctk.get_appearance_mode()=="Dark" else "#6200EE")
        self.music_label.pack(side="left", padx=10, pady=10)
        
        # Blocked Sites Input
        ctk.CTkLabel(self.form_frame, text=get_text("blocked_sites_label"), font=ctk.CTkFont(size=FONT_SIZE, weight="bold")).grid(row=8, column=0, columnspan=2, pady=(20, 5), sticky="w")
        self.blocked_sites_var = ctk.StringVar(value=self.settings.get("blocked_sites", "youtube.com, instagram.com, tiktok.com"))
        self.blocked_sites_entry = ctk.CTkEntry(self.form_frame, textvariable=self.blocked_sites_var, width=400, font=ctk.CTkFont(size=FONT_SIZE))
        self.blocked_sites_entry.grid(row=9, column=0, columnspan=2, pady=5, sticky="w", ipadx=5)
        
        # Language Selector
        ctk.CTkLabel(self.form_frame, text=get_text("language_label"), font=ctk.CTkFont(size=FONT_SIZE, weight="bold")).grid(row=10, column=0, pady=(20, 5), sticky="w")
        self.lang_var = ctk.StringVar(value=self.settings.get("language", "uz"))
        self.lang_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.lang_var, values=["uz", "ru", "en"], width=100, font=ctk.CTkFont(size=FONT_SIZE))
        self.lang_menu.grid(row=10, column=1, pady=(20, 5), sticky="w")
        
        # Save Button
        self.save_btn = ctk.CTkButton(self.form_frame, text=get_text("save_btn"), font=ctk.CTkFont(size=FONT_SIZE, weight="bold"), fg_color="#03DAC6", text_color="black", hover_color="#018786", command=self.save_settings)
        self.save_btn.grid(row=11, column=0, columnspan=2, pady=40, ipadx=30, ipady=8)

    def select_custom_music(self):
        file_path = filedialog.askopenfilename(
            title=get_text("select_music_btn"),
            filetypes=[(get_text("music_files"), "*.mp3 *.wav")]
        )
        if file_path:
            self.music_path_var.set(file_path)
            self.music_label.configure(text=self.get_music_display_text())
            logger.info(f"Yangi musiqa tanlandi: {file_path}")

    def get_music_display_text(self):
        path = self.music_path_var.get()
        if not path:
            return "Standard Lo-Fi"
        return f"{get_text('current_music_label')} {os.path.basename(path)}"

    def create_input(self, parent, row, label_text, var):
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=FONT_SIZE, weight="bold")).grid(row=row, column=0, sticky="w", pady=15, padx=10)
        entry = ctk.CTkEntry(parent, textvariable=var, width=100, font=ctk.CTkFont(size=FONT_SIZE))
        entry.grid(row=row, column=1, sticky="e", pady=15, padx=10)

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
            "language": "uz",
            "font_size": 14
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
                "language": self.lang_var.get(),
                "font_size": int(self.font_size_var.get()),
                "custom_music_path": self.music_path_var.get()
            }
            with open(self.settings_file, "w") as f:
                json.dump(new_settings, f, indent=4)
                
            # Update current language and font size in config
            import config
            config.CURRENT_LANGUAGE = self.lang_var.get()
            config.FONT_SIZE = int(self.font_size_var.get())
                
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
