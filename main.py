import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports
import os
import sys


def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and PyInstaller. """
    if getattr(sys, 'frozen', False):  # Check if the app is bundled
        base_path = sys._MEIPASS  # PyInstaller extracts resources here
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def list_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def connect_to_arduino():
    global ser
    com_port = com_port_var.get()
    try:
        ser = serial.Serial(com_port, 9600, timeout=1)
        connection_status_label.config(text="Pripojené úspešne", fg="green")
    except Exception as e:
        connection_status_label.config(text=f"Chyba pripojenia: {e}", fg="red")


def send_data():
    if not ser or not ser.is_open:
        messagebox.showerror("Chyba", "Najprv sa pripojte k Arduino.")
        return

    try:
        data = []
        for entry in input_entries:
            value = int(entry.get())
            if 0 <= value <= 35:
                data.append(value)
            else:
                raise ValueError(f"Hodnota {value} nie je v rozsahu 0-35.")

        ser.write(bytearray(data))
        echo = ser.read(len(data))

        if echo == bytearray(data):
            messagebox.showinfo("Úspech", "Údaje úspešne odoslané a potvrdené.")
        else:
            messagebox.showerror("Chyba", "Echo nezodpovedá odoslaným údajom.")
    except Exception as e:
        messagebox.showerror("Chyba", f"Došlo k chybe: {e}")


def draw_graph():
    try:
        data = []
        for entry in input_entries:
            value = int(entry.get())
            if 0 <= value <= 35:
                data.append(value)
            else:
                raise ValueError(f"Hodnota {value} nie je v rozsahu 0-35.")

        update_graph(data)
    except Exception as e:
        messagebox.showerror("Chyba", f"Došlo k chybe: {e}")


def update_graph(data):
    ax.clear()
    ax.plot([1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000], data, marker='o',
            color='blue')
    ax.set_title("Graf predstihu")
    ax.set_xlabel("Otáčky motora (ot/min)")
    ax.set_ylabel("Predstih pred HÚ")
    ax.set_xlim(00, 8000)
    ax.set_ylim(5, 40)
    ax.grid(True)
    canvas.draw()

def refresh_ports():
    """Refresh the COM ports dropdown menu."""
    available_ports = list_available_ports()
    menu = com_port_dropdown["menu"]
    menu.delete(0, "end")  # Clear existing menu options

    if available_ports:
        for port in available_ports:
            menu.add_command(label=port, command=lambda p=port: com_port_var.set(p))
        com_port_var.set(available_ports[0])  # Set the first available port as default
    else:
        menu.add_command(label="žiadny port", command=lambda: com_port_var.set("žiadny port"))
        com_port_var.set("žiadny port")

# Initialize GUI
root = tk.Tk()
root.title("Nastavenie predstihu zapaľovania")
root.geometry("900x680")

# Set custom icon
icon_path = resource_path("icon.ico")
try:
    root.iconbitmap(icon_path)
except Exception as e:
    print(f"Error setting icon: {e}")

# Description
description_label = tk.Label(root, text="Nastavenie predstihu zapaľovania pre Babetta 210",
                             font=("Courier New", 18, "bold"))
description_label.pack(pady=10)

# Logo
logo_path = resource_path("rs_logo.png")
tk_logo_image = None
try:
    tk_logo_image = tk.PhotoImage(file=logo_path)
    logo_label = tk.Label(root, image=tk_logo_image)
    logo_label.pack(pady=10)
except Exception as e:
    logo_label = tk.Label(root, text="RS Logo Placeholder", font=("Arial", 12, "bold"), bg="lightgray", width=20,
                          height=3)
    logo_label.pack(pady=10)
    print(f"Error loading logo: {e}")

# COM Port Dropdown
com_port_frame = tk.Frame(root)
com_port_frame.pack(pady=10)
com_port_label = tk.Label(com_port_frame, text="COM Port:")
com_port_label.pack(side=tk.LEFT, padx=5)

com_port_var = tk.StringVar()
available_ports = list_available_ports()

if available_ports:
    com_port_var.set(available_ports[0])  # Set the first available port as default
else:
    available_ports = ["žiadny port"]
    com_port_var.set("žiadny port")

com_port_dropdown = tk.OptionMenu(com_port_frame, com_port_var, *available_ports)
com_port_dropdown.pack(side=tk.LEFT, padx=5)

connect_button = tk.Button(com_port_frame, text="Pripojiť", command=connect_to_arduino)
connect_button.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(com_port_frame, text="Obnoviť", command=refresh_ports)
refresh_button.pack(side=tk.LEFT, padx=5)

connection_status_label = tk.Label(root, text="", font=("Arial", 10))
connection_status_label.pack()



# Input Fields
input_frame = tk.Frame(root)
input_frame.pack(side=tk.LEFT, padx=10, pady=10)

input_labels = ["1500 ot/min", "2000 ot/min", "2500 ot/min", "3000 ot/min", "3500 ot/min", "4000 ot/min", "4500 ot/min",
                "5000 ot/min", "5500 ot/min", "6000 ot/min", "6500 ot/min", "7000 ot/min", "7500 ot/min", "8000 ot/min"]
input_entries = []

for label_text in input_labels:
    row = tk.Frame(input_frame)
    row.pack(fill=tk.X, pady=2)

    label = tk.Label(row, text=label_text, width=10, anchor="w")
    label.pack(side=tk.LEFT)

    entry = tk.Entry(row, width=5)
    entry.pack(side=tk.RIGHT, padx=5)
    input_entries.append(entry)

# Graph Area
fig, ax = plt.subplots(figsize=(5, 4))
ax.set_title("Graf predstihu")
ax.set_xlabel("Otáčky motora (ot/min)")
ax.set_ylabel("Predstih pred HÚ")
ax.set_xlim(0, 8000)
ax.set_ylim(5, 40)
ax.grid(True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

send_button = tk.Button(button_frame, text="Pošli údaje", command=send_data)
send_button.pack(side=tk.LEFT, padx=5)

draw_button = tk.Button(button_frame, text="Prekresli graf", command=draw_graph)
draw_button.pack(side=tk.LEFT, padx=5)


# Start GUI loop
root.mainloop()
