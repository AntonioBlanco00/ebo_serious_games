# ebo_serious_games

## Instalación y configuración de EBO2

Ahora todo el proceso de preparar la aplicación se realiza mediante el script `install.sh`, que automatiza la creación del entorno virtual, la instalación de dependencias y la configuración del lanzador.

---

### 1) Configuración previa (dependencias del sistema)

Antes de ejecutar el script de instalación, asegúrate de tener instaladas las librerías necesarias del sistema.  
Estas librerías permiten que la aplicación funcione correctamente con Tkinter y con PySide/Qt (plugin xcb), y además habilitan la creación de entornos virtuales con `venv`.

En **Ubuntu / Debian** puedes instalarlas con:

```sh
sudo apt-get update
sudo apt-get install -y     python3.10-venv     python3-tk     libxcb-xinerama0     libxcb-cursor0     libxkbcommon-x11-0     libxcb-randr0     libxcb-icccm4     libxcb-image0     libxcb-keysyms1     libxcb-render-util0     libglu1-mesa
```
> **Nota:** En algunas distribuciones el paquete puede llamarse `python3-venv` (sin la versión). Si `python3.10-venv` no está disponible, prueba con:
> ```sh
> sudo apt-get install -y python3-venv
> ```

---

### 2) Clonar el repositorio

Clona el repo y entra en la carpeta `EBO2`:


  ```sh
  git clone https://github.com/<TU_ORGANIZACION_O_USUARIO>/ebo_serious_games.git
  cd ebo_serious_games/EBO2
  ```

---

### 3) Instalación

Ejecuta el script de instalación:
```sh
./install.sh
```
Este script, de forma automática:
- Crea el entorno virtual `games_venv` si no existe.
- Instala todas las dependencias desde `requirements.txt`.
- Configura el lanzador `.desktop` en el menú de aplicaciones y el escritorio.

> Si el script no tiene permisos de ejecución, concédeselos con:
> ```sh
> chmod +x install.sh
> ```

---

### 4) Ejecutar la aplicación

- **Desde el escritorio**: haz doble click en el icono de **EBO2** (la primera vez puede que tengas que hacer clic derecho → *Allow launching*).
- **Desde el menú de aplicaciones**: busca **EBO2** y ejecútalo directamente.

---

## Configuración de `ebo_gpt`

Para que `ebo_gpt` funcione correctamente, es necesario crear un archivo `.env` y agregar tu clave de OpenAI.

### Pasos para crear el archivo `.env`
1. Navega a la carpeta `ebo_gpt` en tu terminal (elige la versión que corresponda):
   ```sh
   cd EBO1/ebo_gpt
   ```
   o
   ```sh
   cd EBO2/ebo_gpt
   ```
2. Crea el archivo `.env`:
   ```sh
   touch .env
   ```
3. Abre el archivo `.env` con tu editor de texto preferido y agrega la siguiente línea:
   ```env
   OPENAI_API_KEY="tu_clave_aqui"
   ```
4. Guarda los cambios y cierra el archivo.

Ahora `ebo_gpt` estará configurado correctamente para utilizar la API de OpenAI.
