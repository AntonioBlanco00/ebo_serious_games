import json
import csv
import os
import shutil
import re
from datetime import datetime

# Obtener la fecha actual en formato día_mes
current_date = datetime.now().strftime("%d_%B_%Y").lower()

# Posibles rutas donde buscar los archivos JSON y su asignación a EBO1 o EBO2
possible_paths = {
    "EBO1": [
        "EBO1/pasapalabra/resultados_pasapalabra.json",
        "EBO1/simonSay/resultados_juego.json"
    ],
    "EBO2": [
        "EBO2/pasapalabra/resultados_pasapalabra.json",
        "EBO2/simonSay/resultados_juego.json"
    ]
}

# Carpeta de resultados y copias de seguridad
base_result_folder = "resultados"
base_backup_folder = "copia_seguridad_datos"

# Lista para almacenar los datos procesados
found_files = []

# Verificar si los archivos JSON existen en las rutas y procesarlos
for subfolder, paths in possible_paths.items():
    for json_file in paths:
        if os.path.exists(json_file):
            found_files.append((json_file, subfolder))
            # Abrir el archivo JSON y procesar línea por línea
            with open(json_file, "r", encoding="utf-8") as file:
                data = []
                for line in file:
                    try:
                        entry = json.loads(line.strip())  # Convertir línea JSON a diccionario
                        # Convertir los tiempos en segundos
                        entry["Tiempo total (seg)"] = entry["Tiempo transcurrido (min)"] * 60 + entry["Tiempo transcurrido (seg)"]
                        # Eliminar los campos originales de minutos y segundos
                        del entry["Tiempo transcurrido (min)"]
                        del entry["Tiempo transcurrido (seg)"]
                        # Añadir a la lista de datos
                        data.append(entry)
                    except json.JSONDecodeError:
                        print(f"Error al procesar la línea: {line}")
                
                # Establecer los nombres de las columnas de acuerdo con el primer conjunto de datos
                if data:
                    fieldnames = list(data[0].keys())
                    
                    # Crear la carpeta de resultados
                    result_folder = os.path.join(base_result_folder, subfolder)
                    os.makedirs(result_folder, exist_ok=True)

                    # Determinar el nombre del archivo CSV
                    if "pasapalabra" in json_file:
                        csv_filename = "resultados_pasapalabra.csv"
                    elif "resultados_juego" in json_file:
                        csv_filename = "resultados_juego_simon.csv"
                    else:
                        continue  # Si no es ninguno de esos, no procesamos el archivo
                    
                    # Generar la ruta final del archivo CSV
                    output_file = os.path.join(result_folder, f"{csv_filename.split('.')[0]}_dia_{current_date}.csv")

                    # Escribir los datos procesados en el archivo CSV
                    with open(output_file, mode="w", newline="", encoding="utf-8") as file_csv:
                        writer = csv.DictWriter(file_csv, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(data)
                    
                    print(f"Archivo CSV generado en: {output_file}")

# Mover los archivos JSON encontrados a la carpeta de copia de seguridad con el nombre correspondiente
for full_path, subfolder in found_files:
    backup_folder = os.path.join(base_backup_folder, subfolder)
    os.makedirs(backup_folder, exist_ok=True)  # Crear la carpeta si no existe
    filename = os.path.basename(full_path)
    backup_filename = f"{filename.split('.')[0]}_dia_{current_date}.json"
    shutil.move(full_path, os.path.join(backup_folder, backup_filename))
    print(f"Archivo JSON movido a: {backup_folder}/{backup_filename}")

# --------------------------- Procesamiento de archivos .txt ---------------------------

def rename_and_modify_txt_file(file_path, output_directory, backup_directory):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Buscar el goal y nombre del jugador
    match = re.search(r'"goal"\s*:\s*"(.*?)".*?"nombre del jugador"\s*:\s*"(.*?)"', content, re.DOTALL)
    
    if match:
        goal = match.group(1).strip()
        player_name = match.group(2).strip()
        base_name = f"storytelling_{player_name}_{goal}_{current_date}"
    else:
        # Si no se encuentra goal y nombre del jugador, buscar el nombre del usuario
        name_match = re.search(r'Nombre:\s*([^\.]+)', content)
        if name_match:
            base_name = f"conversacion_{name_match.group(1).strip()}_{current_date}"
        else:
            return f"No se encontró un nombre válido en el archivo {file_path}."
    
    # Modificar contenido eliminando primer mensaje del usuario
    content = re.sub(r'User: .*?Assistant:', 'Assistant:', content, 1, flags=re.DOTALL)
    
    # Evitar sobrescribir archivos añadiendo un sufijo numérico si el archivo ya existe en la carpeta de salida
    os.makedirs(output_directory, exist_ok=True)
    new_name = f"{base_name}.txt"
    counter = 1
    while os.path.exists(os.path.join(output_directory, new_name)):
        new_name = f"{base_name}_{counter}.txt"
        counter += 1
    
    new_path = os.path.join(output_directory, new_name)
    with open(new_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    # Mover el archivo original a la carpeta de respaldo
    if backup_directory:
        os.makedirs(backup_directory, exist_ok=True)
        backup_path = os.path.join(backup_directory, os.path.basename(file_path))
        shutil.move(file_path, backup_path)
    
    return f"Archivo renombrado y almacenado en {new_path}. El archivo original ha sido movido a {backup_path}."

def process_txt_files(input_dirs, output_directory, backup_directory):
    for input_dir in input_dirs:
        if os.path.exists(input_dir):
            for file_name in os.listdir(input_dir):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(input_dir, file_name)
                    print(rename_and_modify_txt_file(file_path, output_directory, backup_directory))

# Rutas de entrada, salida y respaldo para archivos .txt
txt_input_dirs = ["EBO2/ebo_gpt/conversaciones", 
                  "EBO1/ebo_gpt/conversaciones"] 

txt_output_directory = "resultados/conversaciones"  # Ruta de salida para archivos .txt
txt_backup_directory = "copia_seguridad_datos/conversaciones"  # Carpeta de respaldo para archivos .txt

# Procesar los archivos .txt
process_txt_files(txt_input_dirs, txt_output_directory, txt_backup_directory)
