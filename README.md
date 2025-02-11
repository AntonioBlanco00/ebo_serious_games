# ebo_serious_games

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
