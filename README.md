# ebo_serious_games


## Creación de entorno virtual e instalación de dependencias

Antes de ejecutar cualquier juego o script, es recomendable crear un entorno virtual y asegurarse de que todas las dependencias estén instaladas.  

### Pasos

1. Abre tu terminal y navega a la carpeta `EBO2`:
   ```sh
   cd EBO2
   ```

2. Crea un entorno virtual llamado `games_venv`:
   ```sh
   python3 -m venv games_venv
   ```
   
3. Activa el entorno virtual:
   ```sh
   source games_venv/bin/activate
   ```

4. Instala todas las dependencias del proyecto usando `requirements.txt`:
   ```sh
   pip install -r requirements.txt
   ```
   
5. En este punto para ejecutar la aplicación bastará con configurar la IP que tiene EBO2 con:
   ```sh
   python3 actualizar_configs.py
   ```
   Y ejecutar la aplicación con:
   ```sh
   bash iniciar_juegos.sh
   ```

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
