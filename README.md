# ebo_serious_games


## Instalación y configuración de EBO2


Ahora todo el proceso de preparar la aplicación se realiza mediante el script `install.sh`, que automatiza la creación del entorno virtual, la instalación de dependencias y la configuración del lanzador.

---

### Configuración previa (dependencias del sistema)

Antes de ejecutar el script de instalación, asegúrate de tener instaladas las librerías necesarias del sistema.  
Estas librerías permiten que la aplicación funcione correctamente con Tkinter y con PySide/Qt (plugin xcb).

En Ubuntu / Debian puedes instalarlas con:

```sh
sudo apt-get update
sudo apt-get install -y \
    python3-tk \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libxcb-randr0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libglu1-mesa


### Pasos de instalación


1. Abre tu terminal y navega a la carpeta `EBO2`:
```sh
cd EBO2
```


2. Ejecuta el script de instalación:
```sh
./install.sh
```
Este script:
- Crea el entorno virtual `games_venv` si no existe.
- Instala todas las dependencias desde `requirements.txt`.
- Configura el lanzador `.desktop` en el menú de aplicaciones y el escritorio.

3. Ejecuta la aplicación:
- **Desde el escritorio**: haz doble click en el icono de EBO2 (la primera vez tendrás que pulsar click derecho y: allow launching).
- **Desde el menú de aplicaciones**: busca EBO2 y ejecútalo directamente sin pasos adicionales.

## Configuración de `ebo_gpt`

Para que `ebo_gpt` funcione correctamente, es necesario crear un archivo `.env` y agregar tu clave de OpenAI.

### Pasos para crear el archivo `.env`
1. Navega a la carpeta `ebo_gpt` en tu terminal:
   ```sh
   cd EBO1/ebo_gpt
   ```
   o
   ```sh
   cd EBO2/ebo_gpt
   ```
      
2. Ejecuta el siguiente comando para crear el archivo `.env`:
   ```sh
   touch .env
   ```
3. Abre el archivo `.env` con tu editor de texto preferido y agrega la siguiente línea:
   ```env
   OPENAI_API_KEY="tu_clave_aqui"
   ```
4. Guarda los cambios y cierra el archivo.

Ahora `ebo_gpt` estará configurado correctamente para utilizar la API de OpenAI.
