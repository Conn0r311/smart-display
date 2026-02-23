import tkinter as tk
import time
import requests
import os
import psutil

# =============================
# LOCATION
# =============================

LAT = 34.7304
LON = -86.5861

# =============================
# WEATHER
# =============================

def get_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=America%2FChicago"
        response = requests.get(url, timeout=5)
        data = response.json()

        current_temp = data["current_weather"]["temperature"]
        max_temp = data["daily"]["temperature_2m_max"][0]
        min_temp = data["daily"]["temperature_2m_min"][0]

        return f"🌤 Huntsville, AL\n\nNow: {current_temp}°F\nHigh: {max_temp}°F\nLow: {min_temp}°F"

    except:
        return "Weather unavailable"

# =============================
# SYSTEM HEALTH
# =============================

def get_system_health():
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent

        return f"🖥 System Health\n\nCPU: {cpu}%\nMemory: {memory}%"

    except:
        return "System health unavailable"

# =============================
# TODO LIST
# =============================

def get_todos():
    try:
        if not os.path.exists("todos.txt"):
            return "To-Do file missing"

        with open("todos.txt", "r") as f:
            tasks = [line.strip() for line in f.readlines() if line.strip()]

        if not tasks:
            return "To-Do List Empty"

        return "📝 To-Do List\n\n" + "\n".join("• " + task for task in tasks)

    except:
        return "To-Do unavailable"

# =============================
# UI SETUP
# =============================

root = tk.Tk()
root.title("Connor Smart Display")
root.attributes("-fullscreen", True)
root.configure(bg="#121212")

BG_COLOR = "#121212"
CARD_COLOR = "#1E1E1E"
TEXT_COLOR = "#FFFFFF"

screens = []
current_screen = 0

# =============================
# CARD BUILDER
# =============================

def create_card(title_text):
    container = tk.Frame(root, bg=BG_COLOR)

    card = tk.Frame(
        container,
        bg=CARD_COLOR,
        padx=60,
        pady=50
    )

    card.place(relx=0.5, rely=0.5, anchor="center", width=900, height=500)

    title = tk.Label(
        card,
        text=title_text,
        font=("Segoe UI Variable", 28, "bold"),
        fg="#BBBBBB",
        bg=CARD_COLOR
    )
    title.pack(pady=(0, 25))

    content = tk.Label(
        card,
        text="",
        font=("Segoe UI Variable", 42, "bold"),
        fg=TEXT_COLOR,
        bg=CARD_COLOR,
        justify="center",
        wraplength=800
    )
    content.pack(expand=True)

    return container, content

# =============================
# CLOCK
# =============================

clock_container, clock_label = create_card("Clock")

def update_clock():
    clock_label.config(text=time.strftime("%I:%M:%S %p\n%m/%d/%Y"))
    root.after(1000, update_clock)

update_clock()
screens.append(clock_container)

# =============================
# WEATHER
# =============================

weather_container, weather_label = create_card("Weather")

def update_weather():
    weather_label.config(text=get_weather())
    root.after(600000, update_weather)

update_weather()
screens.append(weather_container)

# =============================
# TODO
# =============================

todo_container, todo_label = create_card("Tasks")

def update_todos():
    todo_label.config(text=get_todos())
    root.after(30000, update_todos)

update_todos()
screens.append(todo_container)

# =============================
# HEALTH
# =============================

health_container, health_label = create_card("System")

def update_health():
    health_label.config(text=get_system_health())
    root.after(20000, update_health)

update_health()
screens.append(health_container)

# =============================
# FADE TRANSITION
# =============================

def show_screen(index):
    for frame in screens:
        frame.pack_forget()
    screens[index].pack(fill="both", expand=True)

def fade_transition(next_index):
    global current_screen

    for alpha in range(100, 0, -5):
        root.attributes("-alpha", alpha / 100)
        root.update()
        time.sleep(0.01)

    current_screen = next_index
    show_screen(current_screen)

    for alpha in range(0, 100, 5):
        root.attributes("-alpha", alpha / 100)
        root.update()
        time.sleep(0.01)

def next_screen():
    global current_screen
    next_index = (current_screen + 1) % len(screens)
    fade_transition(next_index)
    root.after(15000, next_screen)

# =============================
# START
# =============================

show_screen(0)
root.after(15000, next_screen)
root.mainloop()