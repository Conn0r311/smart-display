import tkinter as tk
import time
import requests
import psutil
import socket
from collections import deque
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =============================
# LOCATION SETTINGS
# =============================

LAT = 34.7304
LON = -86.5861

# =============================
# THEME COLORS
# =============================

BG_COLOR = "#121212"
CARD_COLOR = "#1E1E1E"
TEXT_COLOR = "#FFFFFF"

# =============================
# WEATHER
# =============================

def get_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=America%2FChicago"

        data = requests.get(url, timeout=5).json()

        current = data["current_weather"]["temperature"]
        high = data["daily"]["temperature_2m_max"][0]
        low = data["daily"]["temperature_2m_min"][0]

        return f"🌤 Huntsville, AL\n\nNow: {current}°F\nHigh: {high}°F\nLow: {low}°F"

    except:
        return "Weather unavailable"

# =============================
# NETWORK STATUS
# =============================

def get_network_status():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        try:
            requests.get("https://www.google.com", timeout=3)
            internet = "Online"
        except:
            internet = "Offline"

        return f"🌐 Network\n\nIP: {ip}\nInternet: {internet}"

    except:
        return "Network unavailable"

# =============================
# CPU TEMPERATURE
# =============================

def get_cpu_temperature():
    try:
        temps = psutil.sensors_temperatures()

        for sensor in temps.values():
            if sensor:
                return sensor[0].current
    except:
        return None

# =============================
# DASHBOARD UI
# =============================

root = tk.Tk()
root.title("Smart Display")
root.attributes("-fullscreen", True)
root.configure(bg=BG_COLOR)

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

    card.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=600)

    title = tk.Label(
        card,
        text=title_text,
        font=("Segoe UI Variable", 26, "bold"),
        fg="#BBBBBB",
        bg=CARD_COLOR
    )
    title.pack(pady=(0, 20))

    content = tk.Label(
        card,
        font=("Segoe UI Variable", 42, "bold"),
        fg=TEXT_COLOR,
        bg=CARD_COLOR,
        justify="center",
        wraplength=800
    )
    content.pack(expand=True)

    return container, content

# =============================
# CLOCK SCREEN
# =============================

clock_container, clock_label = create_card("Clock")

def update_clock():
    clock_label.config(text=time.strftime("%I:%M:%S %p\n%m/%d/%Y"))
    root.after(1000, update_clock)

update_clock()
screens.append(clock_container)

# =============================
# WEATHER SCREEN
# =============================

weather_container, weather_label = create_card("Weather")

def update_weather():
    weather_label.config(text=get_weather())
    root.after(600000, update_weather)

update_weather()
screens.append(weather_container)

# =============================
# CPU GRAPH SCREEN
# =============================

cpu_container, cpu_card_label = create_card("CPU Usage (Live)")

cpu_data = deque([0]*60, maxlen=60)

fig = Figure(figsize=(8,4), dpi=100)
ax = fig.add_subplot(111)

ax.set_ylim(0, 100)
ax.set_xlim(0, 60)

ax.set_facecolor(CARD_COLOR)
fig.patch.set_facecolor(CARD_COLOR)

ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_color("white")

line, = ax.plot(cpu_data)

canvas = FigureCanvasTkAgg(fig, master=cpu_container)
canvas.get_tk_widget().pack(expand=True)

def update_cpu_graph():
    cpu = psutil.cpu_percent()
    cpu_data.append(cpu)

    line.set_ydata(cpu_data)
    line.set_xdata(range(len(cpu_data)))

    canvas.draw()

    root.after(1000, update_cpu_graph)

update_cpu_graph()
screens.append(cpu_container)

# =============================
# NETWORK SCREEN
# =============================

network_container, network_label = create_card("Network")

def update_network():
    network_label.config(text=get_network_status())
    root.after(10000, update_network)

update_network()
screens.append(network_container)

# =============================
# HEALTH SCREEN (Temperature Warning Feature #9)
# =============================

health_container, health_label = create_card("System Health")

def update_health():

    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    temp = get_cpu_temperature()

    text = f"🖥 System Health\n\nCPU: {cpu}%\nMemory: {memory}%"

    if temp:
        text += f"\nTemp: {temp:.1f}°C"

        if temp > 85:
            health_label.config(fg="#FF4444")
        elif temp > 70:
            health_label.config(fg="#FFD700")
        else:
            health_label.config(fg=TEXT_COLOR)

    health_label.config(text=text)

    root.after(20000, update_health)

update_health()
screens.append(health_container)

# =============================
# SCREEN ROTATION
# =============================

def show_screen(index):
    for frame in screens:
        frame.pack_forget()

    screens[index].pack(fill="both", expand=True)

def next_screen():
    global current_screen

    next_index = (current_screen + 1) % len(screens)

    current_screen = next_index
    show_screen(current_screen)

    root.after(15000, next_screen)

# =============================
# START DISPLAY
# =============================

show_screen(0)
root.after(15000, next_screen)

root.mainloop()