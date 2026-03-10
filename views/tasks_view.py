import customtkinter as ctk
from tkinter import messagebox
from database import add_task, get_tasks, update_task_status, increment_task_pomodoro
from config import get_text

class TasksView(ctk.CTkFrame):
    def __init__(self, master, current_user, on_task_select):
        super().__init__(master)
        self.current_user = current_user
        self.on_task_select = on_task_select
        self.tasks = []
        
        # UI Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(15, 5), padx=15)
        
        ctk.CTkLabel(self.header_frame, text=get_text("tasks_title"), font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        self.add_btn = ctk.CTkButton(self.header_frame, text=get_text("add_btn"), width=100, command=self.show_add_task_dialog)
        self.add_btn.pack(side="right")
        
        # Scrollable Tasks List
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.tasks = get_tasks(self.current_user['id'])
        
        if not self.tasks:
            ctk.CTkLabel(self.scrollable_frame, text=get_text("no_tasks"), text_color="gray").pack(pady=40)
            return
            
        for task in self.tasks:
            self.create_task_widget(task)

    def create_task_widget(self, task):
        # Determine colors by priority
        if task['priority'] == "High":
            border_color = "#CF6679" # Red
        elif task['priority'] == "Medium":
            border_color = "#FFB300" # Yellow
        else:
            border_color = "#03DAC6" # Green
            
        task_frame = ctk.CTkFrame(self.scrollable_frame, border_width=1, border_color=border_color)
        task_frame.pack(fill="x", pady=6, padx=5)
        
        # Title
        title_font = ctk.CTkFont(size=14, overstrike=(task['status'] == "Done"))
        title_label = ctk.CTkLabel(task_frame, text=task['title'], font=title_font)
        title_label.pack(side="left", padx=(15, 10), pady=12)
        
        # Tag Badge
        tag = task.get('tag', 'General')
        ctk.CTkLabel(task_frame, text=f" {tag} ", font=ctk.CTkFont(size=11), fg_color="#333333", text_color="#A0A0A0", corner_radius=4).pack(side="left", padx=5)
        
        # Info Badges
        pomo_label = ctk.CTkLabel(task_frame, text=f"🍅 {task['pomodoro_count']}", font=ctk.CTkFont(size=12, weight="bold"))
        pomo_label.pack(side="left", padx=10)
        
        # Buttons
        if task['status'] != "Done":
            select_btn = ctk.CTkButton(task_frame, text=get_text("select"), width=60, height=28, command=lambda t=task: self.on_task_select(t))
            select_btn.pack(side="right", padx=10, pady=10)
            
            done_btn = ctk.CTkButton(task_frame, text=get_text("done_btn"), width=60, height=28, fg_color="#03DAC6", text_color="black", hover_color="#018786", command=lambda t=task: self.mark_done(t['id']))
            done_btn.pack(side="right", padx=0, pady=10)
        else:
            done_label = ctk.CTkLabel(task_frame, text=get_text("done"), text_color="#03DAC6")
            done_label.pack(side="right", padx=15, pady=10)

    def show_add_task_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title(get_text("new_task"))
        dialog.geometry("400x300")
        dialog.attributes('-topmost', True)
        
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 200
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 150
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=get_text("task_name"), font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        title_entry = ctk.CTkEntry(dialog, width=300)
        title_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text=get_text("priority"), font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        priority_var = ctk.StringVar(value="Medium")
        pri_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        pri_frame.pack()
        
        ctk.CTkRadioButton(pri_frame, text="High", variable=priority_var, value="High").pack(side="left", padx=10)
        ctk.CTkRadioButton(pri_frame, text="Medium", variable=priority_var, value="Medium").pack(side="left", padx=10)
        ctk.CTkRadioButton(pri_frame, text="Low", variable=priority_var, value="Low").pack(side="left", padx=10)
        
        ctk.CTkLabel(dialog, text=get_text("tag"), font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        tag_var = ctk.StringVar(value="General")
        tags = ["General", "💼 Ish", "📚 O'qish", "💪 Sport", "💡 Personal"]
        ctk.CTkOptionMenu(dialog, variable=tag_var, values=tags, width=300).pack(pady=5)
        
        def save_task():
            title = title_entry.get().strip()
            prior = priority_var.get()
            tag = tag_var.get()
            if not title:
                messagebox.showwarning(get_text("error"), get_text("error_name"), parent=dialog)
                return
            add_task(self.current_user['id'], title, prior, tag)
            self.refresh_tasks()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text=get_text("save_task"), command=save_task).pack(pady=30)

    def mark_done(self, task_id):
        update_task_status(task_id, "Done", self.current_user['id'])
        self.refresh_tasks()
