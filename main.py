import tkinter as tk
import time
import requests
import os
import psutil

# =============================
# LOCATION SETTINGS
# Huntsville, Alabama
# =============================

LAT = 34.7304
LON = -86.5861

# =============================
# WEATHER SERVICE
# Open-Meteo Free API
# =============================

def get_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=America%2FChicago"

        response = requests.get(url)
        data = response.json()

        current_temp = data["current_weather"]["temperature"]
        max_temp = data["daily"]["temperature_2m_max"][0]
        min_temp = data["daily"]["temperature_2m_min"][0]

        return f"Huntsville, AL\nNow: {current_temp}°F\nHigh: {max_temp}°F  Low: {min_temp}°F"

    except:
        return "Weather unavailable"

# =============================
# HARDWARE HEALTH WIDGET
# =============================

def get_system_health():
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent

        # Raspberry Pi temperature (if available)
        try:
            temp = psutil.sensors_temperatures()
            if temp and len(temp) > 0:
                for sensor in temp.values():
                    if sensor:
                        temperature = sensor[0].current
                        return f"System Health\nCPU: {cpu}%\nMemory: {memory}%\nTemp: {temperature:.1f}°C"
        except:
            pass

        return f"System Health\nCPU: {cpu}%\nMemory: {memory}%"

    except:
        return "System health unavailable"
# =============================
# TODO LIST SYSTEM
# =============================

def get_todos():
    try:
        if not os.path.exists("todos.txt"):
            return "Todo file missing"

        with open("todos.txt", "r") as f:
            tasks = [line.strip() for line in f.readlines() if line.strip()]

        if not tasks:
            return "To-Do List Empty"

        return "To-Do List\n\n" + "\n".join("• " + task for task in tasks)

    except:
        return "To-Do unavailable"

# =============================
# UI THEME
# Beach Minimal Style
# =============================

root = tk.Tk()
root.attributes("-fullscreen", False)
root.attributes("-alpha", 1.0)

BG_COLOR = "#6EC6FF"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#1E88E5"

root.configure(bg=BG_COLOR)

screens = []
current_screen = 0

# Label creator helper
def create_label(master, size=50, color=TEXT_COLOR, wrap=800):
    return tk.Label(
        master,
        font=("Segoe UI Variable", size, "bold"),
        fg=color,
        bg=BG_COLOR,
        justify="center",
        wraplength=wrap
    )

# =============================
# CLOCK SCREEN
# =============================

clock_frame = tk.Frame(root, bg=BG_COLOR)

clock_label = create_label(clock_frame, 90)
clock_label.pack(expand=True, pady=60)

def update_clock():
    clock_label.config(text=time.strftime("%I:%M:%S %p"))
    root.after(1000, update_clock)

update_clock()
screens.append(clock_frame)

def update_clock():
    clock_label.config(text=time.strftime("%I:%M:%S %p\n%m/%d/%Y"))
    root.after(1000, update_clock)
# =============================
# WEATHER SCREEN
# =============================

weather_frame = tk.Frame(root, bg=BG_COLOR)

weather_label = create_label(weather_frame, 48, ACCENT_COLOR)
weather_label.pack(expand=True, padx=60)

def update_weather():
    weather_label.config(text=get_weather())
    root.after(600000, update_weather)

update_weather()
screens.append(weather_frame)

# =============================
# TODO SCREEN
# =============================

todo_frame = tk.Frame(root, bg=BG_COLOR)

todo_label = create_label(todo_frame, 40, TEXT_COLOR)
todo_label.pack(expand=True, padx=60, pady=40)

def update_todos():
    todo_label.config(text=get_todos())
    root.after(30000, update_todos)

update_todos()
screens.append(todo_frame)

# =============================
# HEALTH SCREEN
# =============================

health_frame = tk.Frame(root, bg=BG_COLOR)

health_label = create_label(health_frame, 40, TEXT_COLOR)
health_label.pack(expand=True, padx=60, pady=40)

def update_health():
    health_label.config(text=get_system_health())
    root.after(20000, update_health)

update_health()
screens.append(health_frame)

# =============================
# FADE TRANSITION ENGINE
# =============================

def show_screen(index):
    for frame in screens:
        frame.pack_forget()

    screens[index].pack(fill="both", expand=True)

def fade_transition(next_index):
    global current_screen

    for alpha in range(100, 0, -10):
        root.attributes("-alpha", alpha / 100)
        root.update()
        time.sleep(0.02)

    current_screen = next_index
    show_screen(current_screen)

    for alpha in range(0, 100, 10):
        root.attributes("-alpha", alpha / 100)
        root.update()
        time.sleep(0.02)

def next_screen():
    global current_screen

    next_index = (current_screen + 1) % len(screens)

    fade_transition(next_index)

    root.after(15000, next_screen)

# =============================
# START DISPLAY LOOP
# =============================

show_screen(0)
root.after(15000, next_screen)
root.mainloop()