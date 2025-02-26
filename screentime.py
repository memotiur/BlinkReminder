import os
import sys
import threading
from datetime import datetime, timedelta
from plyer import notification
import tkinter as tk
from tkinter import messagebox, ttk
import pystray
from pystray import MenuItem as item, Icon
from PIL import Image, ImageDraw

HISTORY_FILE = "screen_time_history.txt"

class ScreenTimeReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Time Manager")
        self.root.geometry("400x750")
        self.root.configure(bg="#ffffff")
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        #  color scheme
        self.colors = {
            "primary": "#2A5C82",
            "secondary": "#5E88B3",
            "background": "#F5F7FA",
            "text": "#2D3748",
            "accent": "#4A5568",
            "card": "#FFFFFF"
        }

        self.setup_styles()
        self.create_widgets()
        self.load_history()
        self.show_instructions()

        self.running = False
        self.total_screen_time = 0
        self.session_start_time = None
        self.twenty_min_timer = 1200  # 20 minutes in seconds
        self.one_hour_timer = 3600    # 60 minutes in seconds
        self.twenty_min_countdown = self.twenty_min_timer
        self.one_hour_countdown = self.one_hour_timer

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TFrame", background=self.colors["background"])
        style.configure("Card.TFrame", 
                      background=self.colors["card"],
                      borderwidth=1,
                      relief="solid",
                      bordercolor="#E2E8F0")
        
        style.configure("TLabel",
                      font=("Segoe UI", 10),
                      background=self.colors["background"],
                      foreground=self.colors["text"])
        
        style.configure("Header.TLabel",
                      font=("Segoe UI", 12, "bold"),
                      foreground=self.colors["primary"])
        
        style.configure("Primary.TButton",
                      font=("Segoe UI", 10, "bold"),
                      foreground="#ffffff",
                      background=self.colors["primary"],
                      borderwidth=0,
                      padding=10)
        
        style.map("Primary.TButton",
                 background=[("active", self.colors["secondary"]), ("disabled", "#CBD5E0")])
        
        style.configure("Secondary.TButton",
                       font=("Segoe UI", 10),
                       foreground=self.colors["primary"],
                       background=self.colors["card"],
                       borderwidth=1,
                       relief="solid",
                       padding=8)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=10, fill=tk.X)
        ttk.Label(header_frame, 
                text="SCREEN TIME MANAGER",
                style="Header.TLabel").pack(side=tk.LEFT)

        # Question Icon for Instructions
        question_button = ttk.Button(header_frame,
                                   text="?",
                                   command=self.show_instructions,
                                   width=2,
                                   style="Secondary.TButton")
        question_button.pack(side=tk.RIGHT)

        # Timer Section
        timer_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        timer_frame.pack(pady=10, fill=tk.X)

        # 20-20-20 Rule Section
        ttk.Label(timer_frame, 
                text="20-20-20 Rule Timer",
                font=("Segoe UI", 10, "bold"),
                foreground=self.colors["accent"]).pack(anchor=tk.W)
        self.twenty_time = ttk.Label(timer_frame, 
                                   text="20:00", 
                                   font=("Segoe UI", 24, "bold"),
                                   foreground=self.colors["primary"])
        self.twenty_time.pack(pady=5)
        ttk.Label(timer_frame, 
                text="Look at something 20 feet away for 20 seconds",
                font=("Segoe UI", 9),
                foreground=self.colors["accent"]).pack()

        ttk.Separator(timer_frame, orient='horizontal').pack(fill=tk.X, pady=15)

        # Hourly Break Section
        ttk.Label(timer_frame, 
                text="Hourly Break Timer",
                font=("Segoe UI", 10, "bold"),
                foreground=self.colors["accent"]).pack(anchor=tk.W)
        self.hourly_time = ttk.Label(timer_frame, 
                                   text="60:00", 
                                   font=("Segoe UI", 24, "bold"),
                                   foreground=self.colors["primary"])
        self.hourly_time.pack(pady=5)
        ttk.Label(timer_frame, 
                text="Take a 5-minute break from your screen",
                font=("Segoe UI", 9),
                foreground=self.colors["accent"]).pack()

        # Control Buttons
        control_frame = ttk.Frame(main_frame, padding=10)
        control_frame.pack(pady=10, fill=tk.X)

        self.start_button = ttk.Button(control_frame, 
                                     text="Start Session", 
                                     command=self.start_reminders,
                                     style="Primary.TButton")
        self.start_button.pack(side=tk.LEFT, expand=True, padx=5)

        self.stop_button = ttk.Button(control_frame, 
                                    text="Pause", 
                                    command=self.stop_reminders,
                                    state=tk.DISABLED,
                                    style="Secondary.TButton")
        self.stop_button.pack(side=tk.LEFT, expand=True, padx=5)

        # Settings Panel
        settings_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        settings_frame.pack(pady=10, fill=tk.X)

        ttk.Label(settings_frame, 
                text="TIMER SETTINGS",
                style="Header.TLabel").pack(anchor=tk.W)

        input_frame = ttk.Frame(settings_frame)
        input_frame.pack(pady=10, fill=tk.X)

        ttk.Label(input_frame, 
                text="20-20-20 Interval (minutes):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.twenty_entry = ttk.Entry(input_frame, width=8, justify='center')
        self.twenty_entry.insert(0, "20")
        self.twenty_entry.configure(state='normal')  # Ensure it's editable
        self.twenty_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)

        ttk.Label(input_frame, 
                text="Break Interval (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.one_hour_entry = ttk.Entry(input_frame, width=8, justify='center')
        self.one_hour_entry.insert(0, "60")
        self.one_hour_entry.configure(state='normal')  # Ensure it's editable
        self.one_hour_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.E)

        ttk.Button(settings_frame, 
                 text="Save Settings",
                 command=self.save_settings,
                 style="Primary.TButton").pack(pady=10)

        # History Button
        ttk.Button(main_frame, 
                 text="View 7-Day Usage History",
                 command=self.show_history,
                 style="Secondary.TButton").pack(pady=10)

    def show_instructions(self):
        messagebox.showinfo(
            "Usage Instructions",
            "How to use:\n\n"
            "1. Set your preferred intervals\n"
            "2. Click 'Start Session'\n\n"
            "When 20-20-20 alert appears:\n"
            "- Look at something 20 feet away\n"
            "- Maintain this for 20 seconds\n"
            "- Optionally dim screen during break\n\n"
            "When Hourly Break alert appears:\n"
            "- Take a 5-minute break\n"
            "- Stretch or walk around\n\n"
            "Click 'Pause' to temporarily stop timers"
        )

    def save_settings(self):
        try:
            twenty_min = int(self.twenty_entry.get())
            one_hour = int(self.one_hour_entry.get())
            self.twenty_min_timer = twenty_min * 60
            self.one_hour_timer = one_hour * 60
            self.twenty_min_countdown = self.twenty_min_timer
            self.one_hour_countdown = self.one_hour_timer
            self.update_progress()
            print(f"Settings saved: 20-20-20 = {twenty_min} min, Hourly = {one_hour} min")  # Debug print
            messagebox.showinfo("Success", "Settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def start_reminders(self):
        if not self.running:
            self.running = True
            self.session_start_time = datetime.now()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.track_screen_time()
            self.reminder_loop()

    def stop_reminders(self):
        if self.running:
            self.running = False
            self.save_session_time()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def reminder_loop(self):
        if not self.running:
            return

        if self.twenty_min_countdown <= 0:
            alert = TwentyTwentyAlert(self.root,
                                    "20-20-20 Rule Reminder",
                                    "Time to follow the 20-20-20 rule:\nLook at something 20 feet away for 20 seconds!")
            alert.grab_set()
            self.twenty_min_countdown = self.twenty_min_timer
            self.stop_reminders()
            return

        if self.one_hour_countdown <= 0:
            self.show_custom_alert(
                "Hourly Break Reminder",
                "Time for a 5-minute break!\nSuggestions:\n- Stretch your body\n- Walk around\n- Hydrate yourself"
            )
            self.one_hour_countdown = self.one_hour_timer
            self.stop_reminders()
            return

        self.twenty_min_countdown -= 1
        self.one_hour_countdown -= 1
        self.update_progress()
        self.root.after(1000, self.reminder_loop)

    def show_custom_alert(self, title, message):
        if self.root.state() == 'iconic':
            self.root.deiconify()
        
        alert = CustomAlert(self.root, title, message)
        alert.grab_set()

    def update_progress(self):
        mins, secs = divmod(self.twenty_min_countdown, 60)
        self.twenty_time.config(text=f"{mins:02d}:{secs:02d}")
        
        hour_mins, hour_secs = divmod(self.one_hour_countdown, 60)
        self.hourly_time.config(text=f"{hour_mins:02d}:{hour_secs:02d}")

    def track_screen_time(self):
        if self.running:
            self.total_screen_time += 1
            self.root.after(1000, self.track_screen_time)

    def save_session_time(self):
        if self.session_start_time:
            end_time = datetime.now()
            duration = (end_time - self.session_start_time).total_seconds()
            minutes = int(duration // 60)
            if minutes > 0:
                with open(HISTORY_FILE, "a") as f:
                    f.write(f"{self.session_start_time.strftime('%Y-%m-%d')}|{minutes}\n")
                self.cleanup_old_entries()

    def cleanup_old_entries(self):
        if os.path.exists(HISTORY_FILE):
            cutoff_date = datetime.now() - timedelta(days=7)
            valid_entries = []
            
            with open(HISTORY_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        date_str, minutes = line.strip().split('|')
                        entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if entry_date >= cutoff_date:
                            valid_entries.append(line)
                    except:
                        continue
            
            with open(HISTORY_FILE, "w") as f:
                f.writelines(valid_entries)

    def load_history(self):
        self.history = {}
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        date_str, minutes = line.strip().split('|')
                        if date_str in self.history:
                            self.history[date_str] += int(minutes)
                        else:
                            self.history[date_str] = int(minutes)
                    except:
                        continue

    def show_history(self):
        self.load_history()
        history_text = "Last 7 Days Screen Time:\n\n"
        
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") 
                for i in range(6, -1, -1)]
        
        for date in dates:
            minutes = self.history.get(date, 0)
            history_text += f"{date}: {minutes//60}h {minutes%60}m\n"
        
        messagebox.showinfo("Screen Time History", history_text)

    def minimize_to_tray(self):
        self.root.withdraw()
        menu = (item('Show', self.show_window), item('Exit', self.exit_app))
        icon = Icon("ScreenTimeReminder", self.create_icon(), menu=menu)
        threading.Thread(target=icon.run, daemon=True).start()

    def show_window(self, icon, item):
        self.root.deiconify()
        icon.stop()

    def create_icon(self):
        image = Image.new("RGB", (64, 64), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill=(42, 92, 130))
        return image

    def exit_app(self):
        self.save_session_time()
        self.root.quit()
        sys.exit(0)


class CustomAlert(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200+500+300")
        self.configure(bg="#ffffff")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        self.alpha = 0.0
        self.attributes("-alpha", self.alpha)
        
        ttk.Label(self, 
                text=message,
                font=("Segoe UI", 12),
                wraplength=380,
                background="#ffffff").pack(pady=20, padx=20)
        
        ttk.Button(self, 
                 text="OK", 
                 command=self.destroy_alert,
                 style="Primary.TButton").pack(pady=10)
        
        self.start_fade_in()

    def start_fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.1
            self.attributes("-alpha", self.alpha)
            self.after(50, self.start_fade_in)
        else:
            self.after(30000, self.destroy_alert)

    def destroy_alert(self):
        self.destroy()

class TwentyTwentyAlert(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("400x250+500+300")
        self.configure(bg="#ffffff")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        self.alpha = 0.0
        self.attributes("-alpha", self.alpha)
        
        ttk.Label(self,
                 text=message,
                 font=("Segoe UI", 12),
                 wraplength=380,
                 background="#ffffff").pack(pady=20, padx=20)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame,
                  text="OK",
                  command=self.destroy_alert,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame,
                  text="Dim Screen",
                  command=self.dim_and_destroy,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        self.start_fade_in()

    def start_fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.1
            self.attributes("-alpha", self.alpha)
            self.after(50, self.start_fade_in)
        else:
            self.after(30000, self.destroy_alert)

    def dim_and_destroy(self):
        # First destroy the alert dialog
        self.destroy()
        
        # Create a semi-transparent overlay
        overlay = tk.Toplevel(self.parent)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.7)
        overlay.configure(bg='gray')
        overlay.attributes('-topmost', True)
        
        # Add countdown label
        countdown = tk.StringVar()
        countdown.set("Time remaining: 20 seconds")
        countdown_label = ttk.Label(overlay,
                                  textvariable=countdown,
                                  font=("Segoe UI", 20, "bold"),
                                  foreground="white",
                                  background="gray")
        countdown_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Start countdown
        self.update_countdown(countdown, overlay, 20)

    def update_countdown(self, countdown_var, overlay, seconds):
        if seconds >= 0:
            countdown_var.set(f"Time remaining: {seconds} seconds")
            overlay.after(1000, lambda: self.update_countdown(countdown_var, overlay, seconds - 1))
        else:
            overlay.destroy()

    def destroy_alert(self):
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeReminderApp(root)
    root.mainloop()
