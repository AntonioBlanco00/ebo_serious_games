import os
import re
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


def modificar_ips_en_configs(ruta_base, nueva_ip):
    # Recorrer la estructura de directorios
    for root, dirs, files in os.walk(ruta_base):
        # Buscar la carpeta "etc"
        if "etc" in dirs:
            etc_path = os.path.join(root, "etc")
            for archivo in os.listdir(etc_path):
                if archivo == "config":
                    config_path = os.path.join(etc_path, archivo)
                    modificar_ip_en_config(config_path, nueva_ip)


def modificar_ip_en_config(ruta_config, nueva_ip):
    # Leer el contenido del archivo
    with open(ruta_config, 'r') as archivo:
        contenido = archivo.read()

    # Buscar y reemplazar las IPs
    contenido_modificado = re.sub(
        r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
        nueva_ip,
        contenido
    )

    # Buscar y reemplazar 'localhost'
    if 'localhost' in contenido_modificado:
        contenido_modificado = contenido_modificado.replace('localhost', nueva_ip)
        print(f"Se reemplazó 'localhost' por {nueva_ip} en: {ruta_config}")

    # Guardar los cambios en el archivo
    with open(ruta_config, 'w') as archivo:
        archivo.write(contenido_modificado)
    print(f"Modificada la IP en: {ruta_config}")


def verificar_conexion_ip(ip):
    try:
        resultado = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return resultado.returncode == 0
    except Exception:
        return False


def ejecutar_programa():
    nueva_ip = entry_ip.get()

    # Validar la IP proporcionada
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', nueva_ip):
        messagebox.showerror("Error", "La IP proporcionada no es válida. Por favor, verifica e inténtalo de nuevo.")
        return

    if verificar_conexion_ip(nueva_ip):
        modificar_ips_en_configs(ruta_base, nueva_ip)
        messagebox.showinfo("Éxito", "El proceso se completó correctamente.")
        root.destroy()  # Cerrar la interfaz gráfica
    else:
        messagebox.showerror(
            "Error",
            "No se puede establecer conexión. Revisa que EBO esté encendido y que la IP sea la correcta. "
            "Recuerda que tanto este ordenador como EBO tienen que estar conectados al mismo wifi"
        )


if __name__ == "__main__":
    # Obtener la ruta base actual
    ruta_base = os.getcwd()

    # Crear la interfaz gráfica
    root = tk.Tk()
    root.title("Configurador de IPs")
    root.geometry("600x400")
    root.configure(bg="#f5f5f5")

    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 12), background="#f5f5f5")
    style.configure("TButton", font=("Arial", 10), padding=5)

    frame = ttk.Frame(root, padding="10")
    frame.pack(expand=True)

    texto = (
        "Introduce la nueva IP que deseas configurar:\n\n"
        "Para obtener la IP:\n"
        "1- Abre un terminal en EBO\n"
        "2- Ejecuta ifconfig\n"
        "3- Ahi aparecerá la IP a introducir, en wlan0\n"
        "\n"
        "IP:"
    )

    label_instruccion = ttk.Label(frame, text=texto, justify="left")
    label_instruccion.pack(pady=10)
    entry_ip = ttk.Entry(frame, width=30, font=("Arial", 12))
    entry_ip.pack(pady=5)

    boton_procesar = ttk.Button(frame, text="Procesar", command=ejecutar_programa)
    boton_procesar.pack(pady=20)

    root.mainloop()
