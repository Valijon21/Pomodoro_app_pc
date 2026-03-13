import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import create_user, verify_user
from config import get_text

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # App Title and Logo Placeholder
        self.title_label = ctk.CTkLabel(self, text=get_text("login_title"), font=ctk.CTkFont(size=42, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=(40, 30))
        
        # Custom frame for inputs
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="n")
        
        from config import FONT_SIZE
        self.username_entry = ctk.CTkEntry(self.input_frame, placeholder_text=get_text("username_placeholder"), width=300, height=45, font=ctk.CTkFont(size=FONT_SIZE))
        self.username_entry.pack(pady=(0, 15))
        
        self.password_entry = ctk.CTkEntry(self.input_frame, placeholder_text=get_text("password_placeholder"), show="*", width=300, height=45, font=ctk.CTkFont(size=FONT_SIZE))
        self.password_entry.pack(pady=(0, 20))
        
        self.login_btn = ctk.CTkButton(self.input_frame, text=get_text("login_btn"), width=300, height=45, font=ctk.CTkFont(size=FONT_SIZE + 2, weight="bold"), command=self.handle_login)
        self.login_btn.pack(pady=(0, 10))
        
        self.info_label = ctk.CTkLabel(self.input_frame, text=get_text("login_info"), text_color="gray", font=ctk.CTkFont(size=FONT_SIZE - 3))
        self.info_label.pack()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning(get_text("warning"), get_text("login_warn_empty"), parent=self.winfo_toplevel())
            return
            
        # First try to verify
        user = verify_user(username, password)
        if user:
            self.on_login_success(user)
        else:
            # Let's try creating a new user
            success = create_user(username, password)
            if success:
                messagebox.showinfo(get_text("success"), get_text("login_success"), parent=self.winfo_toplevel())
                new_user = verify_user(username, password)
                self.on_login_success(new_user)
            else:
                messagebox.showerror(get_text("error"), get_text("login_error"), parent=self.winfo_toplevel())
