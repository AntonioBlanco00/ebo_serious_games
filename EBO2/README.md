# EBO2

## Como acceder a la aplicación `EBO2.desktop` mediante doble click

Para que la app de EBO2 funcione mediante doble click, es necesario copiar el archivo `EBO2.desktop` al escritorio y/o al Menú de aplicaciones.

### Pasos para copiar el archivo `.desktop`
1. Modifica el archivo EBO2.desktop para introducir tu ruta completa en los campos Exced y Icon, puedes abrirlo mediante el editor de textos o desde tu terminal:
   ```sh
   nano /tu-ruta/ebo_serious_games/EBO2/EBO2.desktop

   ```

2. Copia el archivo EBO2.desktop al escritorio desde tu terminal:
   ```sh
   cp ~/tu-ruta/ebo_serious_games/EBO2/EBO2.desktop ~/Escritorio/
   ```
      
3. Copia el archivo EBO2.desktop al menú de aplicaciones desde tu terminal:
   ```sh
   cp ~/tu-ruta/ebo_serious_games/EBO2/EBO2.desktop ~/.local/share/applications/
   ```

Ahora podrás acceder al menú de juegos de EBO2 desde el escritorio o el menú de aplicaciones haciendo doble click.
