import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import psutil

CACHE_FILE = os.path.expanduser("~/.mac_fan_control_cache.json")

class FanControl:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.setup_cache()
        self.setup_style()
        self.setup_bindings()

        self.after_handlers = []
        self.schedule_updates()
        self.apply_cached_speeds()

    def setup_ui(self):
        self.root.title("🚀 Mac Fan Control")
        self.root.geometry("850x600")
        self.root.minsize(750, 500)

        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(1, weight=1)

        # Header Frame
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Title
        ttk.Label(self.header_frame, text="Mac Fan Control", font=('Helvetica', 16, 'bold'),
                 foreground="#2ecc71").pack(side="left", padx=15)

        # Control Buttons
        self.control_buttons = ttk.Frame(self.header_frame)
        self.control_buttons.pack(side="right", padx=10)

        ttk.Button(self.control_buttons, text="🌓", width=3,
                  command=self.toggle_dark_mode).pack(side="left", padx=5)
        ttk.Button(self.control_buttons, text="⚙", width=3,
                  command=self.show_info).pack(side="left", padx=5)

        # Fan Control Frame
        self.fan_frame = ttk.LabelFrame(self.root, text="Fan Configuration", padding=(20, 15))
        self.fan_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        # Fan Controls
        self.create_fan_controls("Fan 1", 0)
        self.create_fan_controls("Fan 2", 1)

        # Visual Separator
        ttk.Separator(self.fan_frame, orient='horizontal').grid(row=2, column=0, columnspan=4, pady=15, sticky="ew")

        # Action Buttons
        self.action_frame = ttk.Frame(self.fan_frame)
        self.action_frame.grid(row=3, column=0, columnspan=4, pady=10, sticky="e")

        ttk.Button(self.action_frame, text="FULL BLAST!!!", style="Accent.TButton",
                  command=self.set_full_blast).pack(side="right", padx=5)
        ttk.Button(self.action_frame, text="Apply", command=self.apply_fan_speeds).pack(side="right", padx=5)
        ttk.Button(self.action_frame, text="Default", command=self.set_default_speeds).pack(side="right", padx=5)

        # Temperature Monitor Frame
        self.temp_frame = ttk.LabelFrame(self.root, text="System Temperatures", padding=(20, 15))
        self.temp_frame.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        # Temperature Display
        self.temp_canvas = tk.Canvas(self.temp_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.temp_frame, orient="vertical", command=self.temp_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.temp_canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.temp_canvas.configure(scrollregion=self.temp_canvas.bbox("all")))
        self.temp_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.temp_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.temp_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.temp_info = tk.StringVar()
        ttk.Label(self.scrollable_frame, textvariable=self.temp_info,
                 font=('Consolas', 10), justify="left").pack(fill="both", expand=True)

    def create_fan_controls(self, fan_name, row):
        ttk.Label(self.fan_frame, text=f"{fan_name} Speed:",
                 font=('Helvetica', 10)).grid(row=row, column=0, padx=10, pady=10, sticky="w")

        slider = ttk.Scale(self.fan_frame, from_=2000, to=6200, orient="horizontal")
        slider.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        value_label = ttk.Label(self.fan_frame, text="2000", width=5,
                               font=('Helvetica', 10, 'bold'))
        value_label.grid(row=row, column=2, padx=10, pady=10)

        rpm_label = ttk.Label(self.fan_frame, text=f"{fan_name} RPM: ...",
                             font=('Helvetica', 10))
        rpm_label.grid(row=row, column=3, padx=10, pady=10)

        slider.config(command=lambda v, s=slider, l=value_label: self.update_slider_label(s, l))

        # Store references
        if "1" in fan_name:
            self.fan1_slider = slider
            self.fan1_value_label = value_label
            self.fan1_rpm_label = rpm_label
        else:
            self.fan2_slider = slider
            self.fan2_value_label = value_label
            self.fan2_rpm_label = rpm_label

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure colors and styles
        self.style.configure(".", font=('Helvetica', 10))
        self.style.configure("Accent.TButton", foreground="white", background="#e74c3c")
        self.style.map("Accent.TButton",
                      background=[('active', '#c0392b'), ('disabled', '#95a5a6')])

        self.colors = {
            'light': {
                'bg': '#f8f9fa', 'fg': '#212529', 'secondary': '#e9ecef',
                'accent': '#2ecc71', 'text': '#343a40'
            },
            'dark': {
                'bg': '#212529', 'fg': '#f8f9fa', 'secondary': '#343a40',
                'accent': '#2ecc71', 'text': '#dee2e6'
            }
        }

        self.current_theme = 'light'
        self.apply_theme()

    def apply_theme(self):
        colors = self.colors[self.current_theme]
        self.root.config(bg=colors['bg'])
        self.temp_canvas.config(bg=colors['bg'])

        self.style.configure('.',
                            background=colors['secondary'],
                            foreground=colors['fg'],
                            fieldbackground=colors['secondary'])

        self.style.configure("TLabel", foreground=colors['text'])
        self.style.configure("TLabelframe", foreground=colors['accent'])
        self.style.configure("TScrollbar", troughcolor=colors['secondary'])

    def setup_cache(self):
        self.cache = {'fan1_min': 2000, 'fan1_max': 6200,
                     'fan2_min': 2000, 'fan2_max': 6200,
                     'default': True}
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    self.cache = json.load(f)
        except Exception as e:
            messagebox.showerror("Cache Error", f"Failed to load cache: {e}")

    def setup_bindings(self):
        self.root.bind("<Visibility>", self.handle_wake_event)

    def schedule_updates(self):
        self.refresh_fan_speeds()
        self.refresh_temperature_data()

    def handle_wake_event(self, event):
        if not self.cache.get('default', True):
            self.apply_cached_speeds()

    def save_cache(self):
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            messagebox.showerror("Cache Error", f"Failed to save cache: {e}")

    def read_fan_speed(self, fan):
        try:
            with open(f"/sys/devices/platform/applesmc.768/{fan}_input", "r") as f:
                return int(f.read().strip())
        except Exception as e:
            return f"Error: {e}"

    def apply_fan_speeds(self):
        fan1_speed = int(self.fan1_slider.get())
        fan2_speed = int(self.fan2_slider.get())

        try:
            for fan, speed in [('fan1', fan1_speed), ('fan2', fan2_speed)]:
                os.system(f'echo {speed} | sudo tee /sys/devices/platform/applesmc.768/{fan}_min')
                os.system(f'echo {speed} | sudo tee /sys/devices/platform/applesmc.768/{fan}_max')

            self.cache.update({
                'fan1_min': fan1_speed,
                'fan1_max': fan1_speed,
                'fan2_min': fan2_speed,
                'fan2_max': fan2_speed,
                'default': False
            })
            self.save_cache()
            messagebox.showinfo("Success", "Fan speeds updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set fan speeds: {e}")

    def apply_cached_speeds(self):
        try:
            for fan in ['fan1', 'fan2']:
                os.system(f'echo {self.cache[f"{fan}_min"]} | sudo tee /sys/devices/platform/applesmc.768/{fan}_min')
                os.system(f'echo {self.cache[f"{fan}_max"]} | sudo tee /sys/devices/platform/applesmc.768/{fan}_max')

            self.fan1_slider.set(self.cache['fan1_min'])
            self.fan2_slider.set(self.cache['fan2_min'])
        except Exception as e:
            messagebox.showerror("Cache Error", f"Failed to apply cached speeds: {e}")

    def set_default_speeds(self):
        try:
            for fan in ['fan1', 'fan2']:
                os.system(f'echo 2000 | sudo tee /sys/devices/platform/applesmc.768/{fan}_min')
                os.system(f'echo 6200 | sudo tee /sys/devices/platform/applesmc.768/{fan}_max')

            self.fan1_slider.set(2000)
            self.fan2_slider.set(2000)
            self.cache.update({'default': True})
            self.save_cache()
            messagebox.showinfo("Reset", "Fan speeds restored to defaults!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset speeds: {e}")

    def set_full_blast(self):
        self.fan1_slider.set(6200)
        self.fan2_slider.set(6200)
        self.apply_fan_speeds()
        messagebox.showinfo("Full Power!", "All fans set to maximum speed! 🔥")

    def update_slider_label(self, slider, label):
        label.config(text=f"{int(slider.get())}")

    def refresh_fan_speeds(self):
        try:
            fan1_rpm = self.read_fan_speed("fan1")
            fan2_rpm = self.read_fan_speed("fan2")

            self.fan1_rpm_label.config(text=f"Fan 1 RPM: {fan1_rpm}" if isinstance(fan1_rpm, int) else fan1_rpm)
            self.fan2_rpm_label.config(text=f"Fan 2 RPM: {fan2_rpm}" if isinstance(fan2_rpm, int) else fan2_rpm)
        except Exception as e:
            self.fan1_rpm_label.config(text=f"Fan 1 RPM: Error ({e})")
            self.fan2_rpm_label.config(text=f"Fan 2 RPM: Error ({e})")

        self.root.after(2000, self.refresh_fan_speeds)

    def refresh_temperature_data(self):
        try:
            temps = []
            for sensor, info in psutil.sensors_temperatures().items():
                for temp in info:
                    label = temp.label or sensor
                    temps.append(f"• {label}: {temp.current:.1f}°C")
            self.temp_info.set("\n".join(temps))
        except Exception as e:
            self.temp_info.set(f"Error reading sensors: {e}")

        self.root.after(5000, self.refresh_temperature_data)

    def toggle_dark_mode(self):
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()

    def show_info(self):
        messagebox.showinfo(
            "About",
            "Mac Fan Control v0.1\n\n"
            "Features:\n"
            "• Custom fan speed control\n"
            "• Temperature monitoring\n"
            "• Dark/light mode toggle\n"
            "• Sleep/wake persistence\n"
            "• Safety-preset controls\n\n"
            "⚠️ Use with caution on supported devices!"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = FanControl(root)
    root.mainloop()
