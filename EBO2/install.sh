#!/bin/bash

# Script de instalación automática de EBO2

# Detectar la ruta actual del proyecto
PROJECT_PATH=$(pwd)

echo "Instalando entorno virtual y dependencias..."

# Crear el entorno virtual si no existe
if [ ! -d "$PROJECT_PATH/games_venv" ]; then
    python3 -m venv "$PROJECT_PATH/games_venv"
    echo "Entorno virtual games_venv creado."
else
    echo "Entorno virtual ya existe, se reutilizará."
fi

# Activar el entorno virtual
source "$PROJECT_PATH/games_venv/bin/activate"

# Instalar dependencias desde requirements.txt
if [ -f "$PROJECT_PATH/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$PROJECT_PATH/requirements.txt"
    echo "Dependencias instaladas."
else
    echo "No se encontró requirements.txt, omitiendo instalación de dependencias."
fi

deactivate

echo "Configurando el archivo .desktop..."

# Archivo .desktop
DESKTOP_FILE="EBO2.desktop"
ICON_FILE="happy_sinfondo.png"

# Comprobar que el archivo .desktop existe
if [ ! -f "$DESKTOP_FILE" ]; then
    echo "Error: $DESKTOP_FILE no encontrado en $PROJECT_PATH"
    exit 1
fi

# Comprobar que el icono existe
if [ ! -f "$PROJECT_PATH/$ICON_FILE" ]; then
    echo "Error: Icono $ICON_FILE no encontrado en $PROJECT_PATH"
    exit 1
fi

# Modificar los campos Exec e Icon en el .desktop con la ruta actual
sed -i "s|^Exec=.*|Exec=$PROJECT_PATH/iniciar_juegos.sh|" "$DESKTOP_FILE"
sed -i "s|^Icon=.*|Icon=$PROJECT_PATH/$ICON_FILE|" "$DESKTOP_FILE"

# Copiar al escritorio (Desktop y Escritorio para compatibilidad)
for DIR in "$HOME/Desktop" "$HOME/Escritorio"; do
    mkdir -p "$DIR"
    cp "$DESKTOP_FILE" "$DIR/"
    chmod +x "$DIR/$DESKTOP_FILE"
    gio set "$DIR/$DESKTOP_FILE" "metadata::trusted" yes
done

# Copiar al menú de aplicaciones
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_DIR"
cp "$DESKTOP_FILE" "$APP_DIR/"
chmod +x "$APP_DIR/$DESKTOP_FILE"

# Asegurarse de que el icono es legible
chmod 644 "$PROJECT_PATH/$ICON_FILE"

# Actualizar caché del menú de aplicaciones
update-desktop-database "$APP_DIR"

# Permitir ejecutar iniciar_juegos.sh
chmod +x "$PROJECT_PATH/iniciar_juegos.sh"

# Refrescar Nautilus para que el escritorio muestre el nuevo .desktop
nautilus -q

echo "Instalación completada. Ahora puedes ejecutar EBO2 desde el escritorio o el menú de aplicaciones."

