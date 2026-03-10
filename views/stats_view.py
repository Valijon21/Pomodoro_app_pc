import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import get_weekly_stats, get_overall_stats, get_all_sessions_for_export
from config import get_text
from tkcalendar import Calendar
import datetime
import csv
from tkinter import filedialog, messagebox

class StatsView(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master)
        
        self.current_user = current_user
        
        # Grid config
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_label = ctk.CTkLabel(self, text=get_text("analytics_title"), font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, pady=(20, 10))
        
        # Summary Cards Frame
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, pady=10, sticky="ew", padx=20)
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Split Bottom into Chart (left), Pie Chart (mid), and Calendar (right)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        
        # Chart Area
        self.chart_frame = ctk.CTkFrame(self.bottom_frame)
        self.chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Pie Chart Area
        self.pie_frame = ctk.CTkFrame(self.bottom_frame)
        self.pie_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Calendar Heatmap Area 
        self.cal_frame = ctk.CTkFrame(self.bottom_frame)
        self.cal_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.refresh_stats()

    def refresh_stats(self):
        # Clear old stats logic
        for child in self.cards_frame.winfo_children():
            child.destroy()
        for child in self.chart_frame.winfo_children():
            child.destroy()
        for child in getattr(self, 'pie_frame', ctk.CTkFrame(self)).winfo_children():
            child.destroy()
        for child in self.cal_frame.winfo_children():
            child.destroy()
            
        from database import get_best_working_hours, get_tag_distribution
        stats = get_overall_stats(self.current_user['id'])
        weekly_data = get_weekly_stats(self.current_user['id'])
        best_time = get_best_working_hours(self.current_user['id'])
        tag_data = get_tag_distribution(self.current_user['id'])
        
        # Draw Summary Cards
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.create_card(self.cards_frame, 0, get_text("total_focus"), f"{stats['total_minutes']} min")
        self.create_card(self.cards_frame, 1, get_text("best_day"), stats['best_day'])
        self.create_card(self.cards_frame, 2, get_text("average"), f"{stats['average_per_day']} min/kun")
        self.create_card(self.cards_frame, 3, get_text("ai_recommendation"), best_time)
        
        # Gamification Frame & Actions
        self.badges_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.badges_frame.grid(row=2, column=0, pady=(0, 10), sticky="ew", padx=20)
        
        # Export button (Right Aligned)
        export_btn = ctk.CTkButton(self.badges_frame, text=get_text("export"), fg_color="#1f6aa5", width=120, command=self.export_csv)
        export_btn.pack(side="right", anchor="n")
        
        self.draw_badges(stats['total_sessions'])
        
        # Draw matplotlib & Calendar
        self.draw_chart(weekly_data)
        self.draw_pie_chart(tag_data)
        self.draw_calendar(weekly_data)
        
    def draw_badges(self, total_pomodoros):
        ctk.CTkLabel(self.badges_frame, text=get_text("badges"), font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        badges_container = ctk.CTkFrame(self.badges_frame, fg_color="#1E1E1E", corner_radius=10)
        badges_container.pack(fill="x", ipady=10)
        
        # Bronze: 100, Silver: 500, Gold: 1000
        bronze_color = "#CD7F32" if total_pomodoros >= 100 else "#404040"
        silver_color = "#C0C0C0" if total_pomodoros >= 500 else "#404040"
        gold_color = "#FFD700" if total_pomodoros >= 1000 else "#404040"
        
        b1 = ctk.CTkLabel(badges_container, text=get_text("bronze"), text_color=bronze_color, font=ctk.CTkFont(size=14, weight="bold"))
        b1.pack(side="left", expand=True)
        
        b2 = ctk.CTkLabel(badges_container, text=get_text("silver"), text_color=silver_color, font=ctk.CTkFont(size=14, weight="bold"))
        b2.pack(side="left", expand=True)
        
        b3 = ctk.CTkLabel(badges_container, text=get_text("gold"), text_color=gold_color, font=ctk.CTkFont(size=14, weight="bold"))
        b3.pack(side="left", expand=True)
        
    def create_card(self, parent, col, title, value):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#2D2D2D")
        card.grid(row=0, column=col, padx=10, sticky="ew")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14), text_color="gray").pack(pady=(15, 5))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color="#BB86FC").pack(pady=(0, 15))

    def draw_chart(self, weekly_data):
        if not weekly_data:
            ctk.CTkLabel(self.chart_frame, text=get_text("chart_no_data"), text_color="gray").pack(expand=True)
            return
            
        dates = [d['date'][-5:] for d in weekly_data] # Get 'MM-DD'
        minutes = [d['minutes'] for d in weekly_data]
        
        # Create matplotlib figure using dark theme friendly colors
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#2D2D2D')
        ax.set_facecolor('#2D2D2D')
        
        ax.plot(dates, minutes, marker='o', color='#03DAC6', linewidth=2, markersize=8)
        
        # Configure axes colors
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        
        ax.tick_params(colors='white')
        ax.set_ylabel(get_text("minutes"), color='white')
        ax.set_title(get_text("7_days_trend"), color='white', pad=15)
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def draw_pie_chart(self, tag_data):
        if not tag_data:
            ctk.CTkLabel(self.pie_frame, text=get_text("pie_no_data"), text_color="gray").pack(expand=True)
            return
            
        labels = list(tag_data.keys())
        sizes = list(tag_data.values())
        colors = ['#03DAC6', '#BB86FC', '#CF6679', '#FFB300', '#4CAF50', '#2196F3']
        
        fig, ax = plt.subplots(figsize=(4, 4))
        fig.patch.set_facecolor('#2D2D2D')
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.0f%%', 
                                          startangle=140, colors=colors, textprops={'color':"w"})
        
        ax.set_title(get_text("tag_distribution"), color='white', pad=15)
        
        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def draw_calendar(self, weekly_data):
        self.cal = Calendar(self.cal_frame, selectmode='none', font="Arial 12", background="#2D2D2D", foreground="white", headersbackground="#1E1E1E", normalbackground="#2D2D2D", bordercolor="#1E1E1E")
        self.cal.pack(fill="both", expand=True, padx=10, pady=10)

        # Tags mapping to custom highlighting colors
        self.cal.tag_config('low', background='#03DAC6', foreground='black')
        self.cal.tag_config('med', background='#FFB300', foreground='black')
        self.cal.tag_config('high', background='#CF6679', foreground='black')

        for day in weekly_data:
            try:
                # the date is formatted as 'YYYY-MM-DD'
                y, m, d = map(int, day['date'].split('-'))
                d_obj = datetime.date(y, m, d)
                minutes = day['minutes']
                
                if minutes >= 120:
                    self.cal.calevent_create(d_obj, f'{minutes}m', 'high')
                elif minutes >= 50:
                    self.cal.calevent_create(d_obj, f'{minutes}m', 'med')
                elif minutes > 0:
                    self.cal.calevent_create(d_obj, f'{minutes}m', 'low')
            except Exception as e:
                pass

    def export_csv(self):
        data = get_all_sessions_for_export(self.current_user['id'])
        if not data:
            messagebox.showinfo("Export", get_text("export_empty"))
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", title="Hisobotni Saqlash", filetypes=[("CSV Fayllari", "*.csv")])
        if not filepath:
            return
            
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Headers
                writer.writerow(data[0].keys())
                # Data
                for row in data:
                    writer.writerow(row.values())
            messagebox.showinfo(get_text("success"), get_text("export_success"))
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('export_error')} {e}")
