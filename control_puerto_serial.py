import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading

# Variables globales para la conexión serial y el control de hilos
serial_connection = None
stop_thread = False

# Función para actualizar la lista de puertos disponibles
def actualizar_puertos():
    puertos = [port.device for port in serial.tools.list_ports.comports()]
    port_combobox['values'] = puertos
    if puertos:
        port_combobox.current(0)
    else:
        port_combobox.set('')

# Función para conectar al puerto serial
def conectar_puerto():
    global serial_connection
    try:
        port = port_combobox.get()
        serial_connection = serial.Serial(port, 115200, timeout=1)
        conectar_button.config(state='disabled')
        desconectar_button.config(state='normal')
        habilitar_controles(True)
        messagebox.showinfo("Conexión", f"Conectado a {port}")
        iniciar_hilo_lectura()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar al puerto: {e}")

# Función para desconectar el puerto serial
def desconectar_puerto():
    global serial_connection, stop_thread
    if serial_connection:
        stop_thread = True
        serial_connection.close()
        serial_connection = None
        conectar_button.config(state='normal')
        desconectar_button.config(state='disabled')
        habilitar_controles(False)
        messagebox.showinfo("Desconexión", "Desconectado del puerto")

# Función para habilitar/deshabilitar controles
def habilitar_controles(estado):
    enviar_temp_button.config(state='normal' if estado else 'disabled')
    apagar_foco_button.config(state='normal' if estado else 'disabled')
    apagar_ventilador_button.config(state='normal' if estado else 'disabled')
    abrir_ventana_button.config(state='normal' if estado else 'disabled')
    cerrar_ventana_button.config(state='normal' if estado else 'disabled')
    prender_bomba_button.config(state='normal' if estado else 'disabled')
    apagar_bomba_button.config(state='normal' if estado else 'disabled')

# Función para enviar la temperatura al puerto serial
def enviar_temperatura():
    if serial_connection:
        temperatura = temp_entry.get()
        if temperatura.isdigit():
            serial_connection.write(f'T{temperatura}\n'.encode())
        else:
            messagebox.showwarning("Advertencia", "Ingrese un valor de temperatura válido")
    else:
        messagebox.showwarning("Advertencia", "Conéctese primero a un puerto")

# Funciones para enviar comandos al puerto serial
def apagar_foco():
    if serial_connection:
        serial_connection.write(b'L\n')

def apagar_ventilador():
    if serial_connection:
        serial_connection.write(b'F\n')

def prender_bomba():
    if serial_connection:
        serial_connection.write(b'B\n')

def apagar_bomba():
    if serial_connection:
        serial_connection.write(b'b\n')

def abrir_ventana():
    if serial_connection:
        serial_connection.write(b'O\n')

def cerrar_ventana():
    if serial_connection:
        serial_connection.write(b'C\n')

# Función para leer datos desde el puerto serial
def iniciar_hilo_lectura():
    global stop_thread
    stop_thread = False
    hilo = threading.Thread(target=leer_datos, daemon=True)
    hilo.start()

def leer_datos():
    global stop_thread
    while not stop_thread and serial_connection:
        try:
            if serial_connection.in_waiting:
                linea = serial_connection.readline().decode('utf-8').strip()
                if linea.startswith("TEMP:"):
                    temperature_var.set(linea.split(':')[1])
                elif linea.startswith("HUMIDITY:"):
                    humidity_var.set(linea.split(':')[1])
                elif linea.startswith("LIGHT:"):
                    light_status_var.set("ON" if "ON" in linea else "OFF")
                elif linea.startswith("FAN:"):
                    fan_status_var.set("ON" if "ON" in linea else "OFF")
        except Exception as e:
            print(f"Error al leer datos: {e}")

# Configuración de la ventana principal
root = tk.Tk()
root.title("Control de Dispositivos")
root.geometry("600x600")

# Variables para monitoreo de datos
temperature_var = tk.StringVar(value="0.0")
humidity_var = tk.StringVar(value="0.0")
fan_status_var = tk.StringVar(value="OFF")
light_status_var = tk.StringVar(value="OFF")
window_status_var = tk.StringVar(value="CERRADA")
bomba_status_var = tk.StringVar(value="APAGADA")

# Widgets de la GUI
port_combobox = ttk.Combobox(root, width=15)
port_combobox.grid(row=0, column=1, padx=5, pady=5)
actualizar_puertos_button = tk.Button(root, text="Actualizar Puertos", command=actualizar_puertos)
actualizar_puertos_button.grid(row=0, column=2, padx=5, pady=5)
conectar_button = tk.Button(root, text="Conectar", command=conectar_puerto)
conectar_button.grid(row=0, column=3, padx=5, pady=5)
desconectar_button = tk.Button(root, text="Desconectar", state='disabled', command=desconectar_puerto)
desconectar_button.grid(row=0, column=4, padx=5, pady=5)

# Etiquetas para el monitoreo
tk.Label(root, text="Temperatura:").grid(row=1, column=0, sticky='w')
tk.Label(root, textvariable=temperature_var).grid(row=1, column=1, sticky='w')
tk.Label(root, text="Humedad:").grid(row=2, column=0, sticky='w')
tk.Label(root, textvariable=humidity_var).grid(row=2, column=1, sticky='w')
tk.Label(root, text="Ventilador:").grid(row=3, column=0, sticky='w')
tk.Label(root, textvariable=fan_status_var).grid(row=3, column=1, sticky='w')
tk.Label(root, text="Foco:").grid(row=4, column=0, sticky='w')
tk.Label(root, textvariable=light_status_var).grid(row=4, column=1, sticky='w')
tk.Label(root, text="Ventana:").grid(row=5, column=0, sticky='w')
tk.Label(root, textvariable=window_status_var).grid(row=5, column=1, sticky='w')
tk.Label(root, text="Bomba:").grid(row=6, column=0, sticky='w')
tk.Label(root, textvariable=bomba_status_var).grid(row=6, column=1, sticky='w')

# Controles de temperatura
tk.Label(root, text="Temperatura objetivo:").grid(row=7, column=0, sticky='w')
temp_entry = tk.Entry(root)
temp_entry.grid(row=7, column=1, sticky='w')
enviar_temp_button = tk.Button(root, text="Enviar Temp", command=enviar_temperatura, state='disabled')
enviar_temp_button.grid(row=7, column=2, padx=5, pady=5)

# Botones de control de dispositivos
apagar_ventilador_button = tk.Button(root, text="Apagar Ventilador", command=apagar_ventilador, state='disabled')
apagar_ventilador_button.grid(row=8, column=0, padx=5, pady=5)
apagar_foco_button = tk.Button(root, text="Apagar Foco", command=apagar_foco, state='disabled')
apagar_foco_button.grid(row=8, column=1, padx=5, pady=5)
abrir_ventana_button = tk.Button(root, text="Abrir Ventana", command=abrir_ventana, state='disabled')
abrir_ventana_button.grid(row=9, column=0, padx=5, pady=5)
cerrar_ventana_button = tk.Button(root, text="Cerrar Ventana", command=cerrar_ventana, state='disabled')
cerrar_ventana_button.grid(row=9, column=1, padx=5, pady=5)
prender_bomba_button = tk.Button(root, text="Prender Bomba", command=prender_bomba, state='disabled')
prender_bomba_button.grid(row=10, column=0, padx=5, pady=5)
apagar_bomba_button = tk.Button(root, text="Apagar Bomba", command=apagar_bomba, state='disabled')
apagar_bomba_button.grid(row=10, column=1, padx=5, pady=5)

# Botón para salir de la aplicación
salir_button = tk.Button(root, text="Salir", command=root.destroy)
salir_button.grid(row=11, column=2, padx=5, pady=5)

# Ejecutar la función de actualización de puertos al inicio
actualizar_puertos()

# Iniciar el loop de la GUI
root.mainloop()