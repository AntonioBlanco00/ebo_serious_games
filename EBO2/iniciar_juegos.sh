#!/bin/bash

# Ejecutar primero python3 reiniciar.py y esperar 1 segundo
python3 reiniciar.py
sleep 1

# Definir las rutas y nombres de las pestañas usando rutas relativas
ruta1="./ebo_gpt"
nombre1="GPT"
ruta2="./pasapalabra"
nombre2="Pasapalabra"
ruta3="./simonSay"
nombre3="SimonSay"
ruta4="./storytelling"
nombre4="Storytelling"
ruta5="./app_juegos"
nombre5="APP_JUEGOS"
ruta6="./ebo_app"
nombre6="EBO_APP"


# Comando para abrir una nueva pestaña con un comando específico en gnome-terminal
function abrir_pestana {
    gnome-terminal --tab -- bash -c "$1; exec bash"
}

# Abrir la primera ruta en la pestaña inicial y ejecutar el comando
abrir_pestana "cd $ruta1 && echo 'Ejecutando en $nombre1' && src/ebo_gpt.py etc/config"

# Abrir las siguientes rutas en nuevas pestañas y ejecutar los comandos correspondientes
abrir_pestana "cd $ruta2 && echo 'Ejecutando en $nombre2' && src/pasapalabra.py etc/config"
abrir_pestana "cd $ruta3 && echo 'Ejecutando en $nombre3' && src/simonSay.py etc/config"
abrir_pestana "cd $ruta4 && echo 'Ejecutando en $nombre4' && src/storytelling.py etc/config"
abrir_pestana "cd $ruta5 && echo 'Ejecutando en $nombre5' && src/app_juegos.py etc/config"
abrir_pestana "cd $ruta6 && echo 'Ejecutando en $nombre6' && src/ebo_app.py etc/config"

