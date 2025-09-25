#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2024 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

from rich.console import Console
from genericworker import *
import interfaces as ifaces
import json
from time import sleep
import pandas as pd
import time
from datetime import datetime
import random
import os, warnings
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.filterwarnings(
    "ignore",
    message=r"pkg_resources is deprecated as an API.*",
    category=UserWarning,
    module=r"pygame\.pkgdata"
)
import pygame
import sys
from PySide6 import QtUiTools
from PySide6.QtCore import Qt, QTimer, QFile, Signal, Slot, QEvent
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QPixmap

UI_RESP   = "../../igs/pasapalabra_respuesta.ui"
UI_MENU   = "../../igs/pasapalabra_menu.ui"
UI_CHECK  = "../../igs/botonUI.ui"
UI_START  = "../../igs/comenzarUI.ui"
LOGO_1    = "../../igs/logos/logo_euro.png"
LOGO_2    = "../../igs/logos/robolab.png"

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        self.NUM_LEDS = 52
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        pygame.init()

        ########## INTRODUCCIÓN DE SONIDOS ##########
        self.sounds = {
            "click": pygame.mixer.Sound('src/click.wav'),
        }

        self.reiniciar_variables()

        QApplication.processEvents()

        self.ui = self.load_ui()
        self.ui2 = self.therapist_ui()
        self.ui3 = self.load_check()
        self.ui4 = self.comenzar_checked()

        ########## BATERÍA DE RESPUESTAS Y FUNCIÓN PARA ALEATORIZAR ##########
        self.bateria_aciertos = [
            "¡Increíble, acertaste!",
            "¡Qué bien, has acertado!",
            "¡Excelente trabajo, lo lograste!",
            "¡Estupendo, muy bien hecho!",
            "¡Fantástico, respuesta correcta!",
            "¡Bien hecho, estás en racha!",
            "¡Lo hiciste perfecto, sigue así!",
            "¡Genial, has acertado, sigue adelante!"
        ]

        self.bateria_fallos = [
            "Incorrecto. No te preocupes, todos fallamos alguna vez.",
            "Fallo. ¡Ánimo, la próxima vez seguro que aciertas!",
            "Error. ¡No pasa nada, lo seguirás haciendo mejor!",
            "Incorrecto. Un pequeño tropiezo, sigue adelante, ¡lo lograrás!",
            "Mal, pero ¡No te rindas, sigue intentándolo!",
            "Fallo. ¡Sigue adelante, cada intento te acerca más!",
            "Fallaste pero ¡El error no te define, lo harás mejor la próxima!",
            "Incorrecto. ¡Ánimo, que pronto lo conseguirás!"
        ]

        self.bateria_pasapalabra = [
            "¡Pasapalabra, sigue adelante, que te va a ir genial!",
            "¡Pasapalabra! Vamos a la siguiente, ¡tú puedes!",
            "¡No te preocupes, pasamos a la siguiente palabra!",
            "¡Pasapalabra! La siguiente será tuya.",
            "¡Siguiente palabra, que va a ser más fácil!",
            "¡Pasapalabra, a por la siguiente con todo!",
            "¡Vamos, pasemos a la siguiente, lo lograrás!",
            "¡Pasapalabra, ahora es el turno de la siguiente!"
        ]

    def elegir_respuesta(self, bateria):
        return random.choice(bateria)

    def __del__(self):
        """Destructor"""

    def setParams(self, params):

        return True

    ########## FUNCIÓN PARA ENCENDER LAS LUCES LEDS ##########
    def set_all_LEDS_colors(self, red=0, green=0, blue=0, white=0):
        pixel_array = {i: ifaces.RoboCompLEDArray.Pixel(red=red, green=green, blue=blue, white=white) for i in
                       range(self.NUM_LEDS)}
        self.ledarray_proxy.setLEDArray(pixel_array)

    ########## OBTIENE LOS ROSCOS ##########
    def archivo(self, archivo_json):
        """Cargar los datos desde el archivo JSON"""
        self.bd = archivo_json
        with open(self.bd, 'r', encoding='utf-8') as json_file:
            self.datos = json.load(json_file)["preguntas"] # Acceder a la clave 'preguntas'

        # Iterar sobre las preguntas y almacenar las letras, preguntas y respuestas
        for pregunta in self.datos:
            self.letras.append(pregunta['letra'])  # Guardar las letras
            self.preguntas.append(pregunta['definicion'])  # Guardar las definiciones
            self.respuestas.append(pregunta['respuesta'])  # Guardar las respuestas

    ########## PROCESO DEL JUEGO ##########
    def juego(self):
        # Carga banco de preguntas
        json_elegido = f"roscos/{self.rosco}.json"
        self.archivo(json_elegido)
        print("Comienzo de juego")

        # Mapa letra->índice para evitar búsquedas repetidas
        idx = {l: i for i, l in enumerate(self.letras)}

        self.start_time = time.time()

        cola = self.letras[:]  # letras pendientes en esta vuelta (lista)
        pasadas = []  # letras pasadas para la siguiente vuelta (lista)
        in_pasadas_phase = False  # False = primera(s) vuelta(s); True = vuelta de letras pasadas

        i = 0
        while (i < len(cola) or pasadas) and self.running:
            # Si terminamos la cola y hay pasadas, arrancamos la vuelta de pasadas
            if i >= len(cola) and pasadas:
                self.speech_proxy.say("Vamos a dar otra vuelta con las letras que pasaste.", False)
                print("Ahora vamos a repasar las letras que pasaste.")
                cola = pasadas
                pasadas = []
                in_pasadas_phase = True
                i = 0
                continue

            # Si ya no queda nada y no hay pasadas, salimos
            if i >= len(cola):
                break

            letra = cola[i]
            j = idx[letra]

            # Presenta pista + pregunta
            self._presentar_pista(j, letra)
            correcta = self.respuestas[j]

            # UI + espera
            self._mostrar_ui_con_respuesta(correcta)
            self._esperar_respuesta()
            if not self.running:
                break

            # Cierra cronómetro y registra
            self._cerrar_cronometro()

            # Procesa respuesta
            if self.resp == "pasapalabra":
                self._feedback("pass")
                if not in_pasadas_phase:
                    # Primera(s) vuelta(s): se reprograma para la vuelta de pasadas
                    pasadas.append(letra)
                    self.letras_pasadas.append(letra)
                    self.pasadas += 1
                else:
                    # En la vuelta de pasadas: se elimina definitivamente (no se vuelve a pasar)
                    if letra in self.letras_pasadas:
                        self.letras_pasadas.remove(letra)
                # En ambos casos, quitamos la letra de la cola actual y NO incrementamos i
                del cola[i]
                continue

            elif self.resp == "si":
                self._feedback("ok")
                self.aciertos += 1
                if in_pasadas_phase:
                    # En segunda vuelta, resolver resta una pasada pendiente
                    self.pasadas -= 1
                    if letra in self.letras_pasadas:
                        self.letras_pasadas.remove(letra)
                del cola[i]
                continue

            else:
                self._feedback("ko", correcta=correcta)
                self.fallos += 1
                if in_pasadas_phase:
                    self.pasadas -= 1
                    if letra in self.letras_pasadas:
                        self.letras_pasadas.remove(letra)
                del cola[i]
                continue

        # Fin de juego
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        self.media = (sum(self.responses_times) / len(self.responses_times)) if self.responses_times else 0.0
        self.running = False

        self.speech_proxy.say("Fin del juego. ¡Lo has hecho genial!:", False)
        self.agregar_resultados(
            self.nombre, self.rosco, self.aciertos, self.fallos, self.pasadas, self.fecha, self.hora,
            (self.elapsed_time // 60), (self.elapsed_time % 60), self.media
        )
        self.guardar_resultados()
        self.reiniciar_variables()
        self.gestorsg_proxy.LanzarApp()

    def _presentar_pista(self, i: int, letra: str):
        if self.respuestas[i].startswith(letra):
            self.letra_actual = f"Comienza con la letra:{letra}"
            self.speech_proxy.say(self.letra_actual, False)
            print(f"Con la letra: {letra}")
        else:
            self.letra_actual = f"Contiene la letra:{letra}"
            self.speech_proxy.say(self.letra_actual, False)
            print(f"Contiene la letra: {letra}")
        self.pregunta_actual = self.preguntas[i]
        self.speech_proxy.say(self.pregunta_actual, False)
        print(self.pregunta_actual)
        self.terminaHablar()

    def _mostrar_ui_con_respuesta(self, respuesta_correcta: str):
        self.start_question_time = time.time()
        self.ui.respuesta.clear()
        self.ui.respuesta.insertPlainText(respuesta_correcta)
        self.ui.show()

    def _esperar_respuesta(self):
        self.resp = ""
        while self.resp == "" and self.running:
            QApplication.processEvents()

    def _cerrar_cronometro(self):
        self.end_question_time = time.time()
        self.cerrar_ui(1)
        self.response_time = self.end_question_time - self.start_question_time
        self.responses_times.append(self.response_time)

    def _feedback(self, tipo: str, correcta: str | None = None):
        if tipo == "pass":
            self.speech_proxy.say(self.elegir_respuesta(self.bateria_pasapalabra), False)
            print("Has pasado esta letra.")
            self.set_all_LEDS_colors(255, 255, 0);
            self.emotionalmotor_proxy.expressSurprise()
            sleep(2);
            self.set_all_LEDS_colors(0, 0, 0);
            sleep(1);
            self.emotionalmotor_proxy.expressJoy()
        elif tipo == "ok":
            self.speech_proxy.say(self.elegir_respuesta(self.bateria_aciertos), False)
            print("¡Respuesta correcta!")
            self.set_all_LEDS_colors(0, 255, 0);
            self.emotionalmotor_proxy.expressJoy()
            sleep(1);
            self.set_all_LEDS_colors(0, 0, 0);
            sleep(1);
            self.emotionalmotor_proxy.expressJoy()
        elif tipo == "ko":
            self.speech_proxy.say(f"{self.elegir_respuesta(self.bateria_fallos)} La respuesta correcta era {correcta}",
                                  False)
            print(f"Respuesta incorrecta! La respuesta es {correcta}")
            self.set_all_LEDS_colors(255, 0, 0);
            self.emotionalmotor_proxy.expressSadness()
            sleep(2);
            self.set_all_LEDS_colors(0, 0, 0);
            sleep(1);
            self.emotionalmotor_proxy.expressJoy()

    def reiniciar_variables(self):
        self.datos = []
        self.letras = []
        self.preguntas = []
        self.respuestas = []
        self.aciertos = 0
        self.fallos = 0
        self.pasadas = 0
        self.letras_pasadas = []
        self.nombre = ""
        self.fecha = 0
        self.hora = 0
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.rosco = ""
        self.bd = ""
        self.resp =""
        self.running = False
        self.boton = False
        self.check = ""
        self.letra_actual = ""
        self.pregunta_actual = ""
        self.start_question_time = 0
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0

        self.df = pd.DataFrame(columns=["Nombre", "Rosco", "Aciertos", "Fallos", "Pasadas", "Fecha", "Hora", "Tiempo transcurrido (min)",
                                        "Tiempo transcurrido (seg)", "Tiempo de respuesta medio (seg)"])
        print("Variable self.df reiniciada para la próxima partida.")

    ########## INTRODUCCIÓN AL JUEGO ##########
    def introduccion (self):
        while self.running:
            if not self.running:
                break

            QApplication.processEvents()

            self.fecha = datetime.now().strftime("%d-%m-%Y")
            self.hora = datetime.now().strftime("%H:%M:%S")
            self.emotionalmotor_proxy.expressJoy()
            self.speech_proxy.say(f"Hola {self.nombre}, vamos a jugar a Pasapalabra.", False)
            print(f"Hola {self.nombre}, vamos a jugar a Pasapalabra.")
            self.speech_proxy.say( "Pasapalabra es un juego donde tienes que responder correctamente a preguntas cuyas respuestas empiezan o "
                                   "contienen cada letra del abecedario ", False)
            print("Pasapalabra es un juego donde tienes que responder correctamente a preguntas cuyas respuestas empiezan o "
                                   "contienen cada letra del abecedario ")
            self.speech_proxy.say("¿Quieres que te explique el juego?", False)
            print("¿Quieres que te explique el juego?")
            self.terminaHablar()
            # Introducir interfaz
            self.check = ""
            self.ui3.show()
            self.ui3.exec_()

            if self.check == "si":
                self.speech_proxy.say(
                    "Cada letra tiene una pregunta asociada. Por ejemplo: Con la A: Accesorio de joyería que se pone en los dedos. "
                    "La respuesta sería Anillos", False)
                print( "Cada letra tiene una pregunta asociada. Por ejemplo: Con la A: Accesorio de joyería que se pone en los dedos. "
                    "La respuesta sería Anillos")
                self.speech_proxy.say("Si no sabes la respuesta, puedes decir pasapalabra para saltar esa pregunta y volver a ella más tarde", False)
                print("Si no sabes la respuesta, puedes decir pasapalabra para saltar esa pregunta y volver a ella más tarde")
                self.speech_proxy.say("El juego termina cuando hayas contestado las preguntas asociadas a todas las letras", False)
                print("El juego termina cuando hayas contestado las preguntas asociadas a todas las letras")
            elif self.check == "no":
                self.speech_proxy.say("Mantén la calma, escucha bien las preguntas, y si dudas, ¡pasapalabra!", False)
                print("Mantén la calma, escucha bien las preguntas, y si dudas, ¡pasapalabra!")
                self.speech_proxy.say("¡Comencemos con el juego!", False)
                print("Comencemos con el juego")

            self.terminaHablar()
            self.ui4.show()
            self.ui4.exec_()
            self.juego()

    def terminaHablar(self):
        sleep(2.5)
        while self.speech_proxy.isBusy():
            pass

    ########## FUNCIÓN QUE AGREGA LOS RESULTADOS AL DATAFRAME ##########
    def agregar_resultados(self, nombre,dificultad, aciertos, fallos, pasadas, fecha, hora,
                           tiempo_transcurrido_min, tiempo_transcurrido_seg, tiempo_respuesta_medio):
        # Crea un diccionario con los datos nuevos
        nuevo_resultado = {
            "Nombre": nombre,
            "Rosco" : dificultad,
            "Aciertos": aciertos,
            "Fallos": fallos,
            "Pasadas": pasadas,
            "Fecha": fecha,
            "Hora": hora,
            "Tiempo transcurrido (min)": tiempo_transcurrido_min,
            "Tiempo transcurrido (seg)": tiempo_transcurrido_seg,
            "Tiempo de respuesta medio (seg)": tiempo_respuesta_medio
        }

        # Convierte el diccionario en un DataFrame de una fila
        nuevo_df = pd.DataFrame([nuevo_resultado])

        # Agrega la nueva fila al DataFrame existente
        self.df = pd.concat([self.df, nuevo_df], ignore_index=True)

    ########## FUNCIÓN QUE GUARDA LOS RESULTADOS DEL JUEGO ##########
    def guardar_resultados(self):
        archivo = "resultados_pasapalabra.json"

        # Inicializar un DataFrame vacío para los resultados existentes
        datos_existentes = pd.DataFrame()

        # Intentar leer el archivo existente si existe
        if os.path.exists(archivo):
            try:
                datos_existentes = pd.read_json(archivo, orient='records', lines=True)
            except ValueError:
                print(
                    "El archivo JSON existente tiene un formato inválido o está vacío. Sobrescribiendo el archivo.")

        # Asegurarse de que los DataFrames no estén vacíos antes de concatenar
        if not self.df.empty:
            if not datos_existentes.empty:
                # Concatenar si ambos DataFrames tienen contenido válido
                self.df = pd.concat([datos_existentes, self.df], ignore_index=True)
            else:
                # Si no hay datos existentes válidos, usar solo los nuevos
                print("No se encontraron datos previos válidos, creando un nuevo archivo.")
        else:
            print("El DataFrame de nuevos resultados está vacío. No se guardará nada.")
            return

        # Guardar el DataFrame combinado en formato JSON
        self.df.to_json(archivo, orient='records', lines=True)
        print(f"Resultados guardados correctamente en {archivo}")
        df_resultados = pd.read_json(archivo, orient='records', lines=True)
        print(df_resultados)

    ##########################################################################################

    def load_ui_generic(self, ui_path, ui_number, *, logo_paths=None, botones=None,
                        ayuda_button=None, back_button=None, after_load=None):
        loader = QtUiTools.QUiLoader()
        file = QFile(ui_path)
        file.open(QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Logos
        if logo_paths:
            for label_name, path in logo_paths.items():
                label = getattr(ui, label_name, None)
                if label:
                    label.setPixmap(QPixmap(path))
                    label.setScaledContents(True)

        # Botones
        if botones:
            for btn_name, func in botones.items():
                btn = getattr(ui, btn_name, None)
                if btn:
                    btn.clicked.connect(func)

        # Ayuda
        if ayuda_button and hasattr(ui, ayuda_button):
            getattr(ui, ayuda_button).clicked.connect(lambda: self.toggle_ayuda(ui))
            if hasattr(ui, "ayuda"):
                ui.ayuda.hide()

        # Back
        if back_button and hasattr(ui, back_button):
            getattr(ui, back_button).clicked.connect(lambda: self.back_clicked_ui(ui_number))

        # Hook post-carga
        if callable(after_load):
            after_load(ui)

        # Registrar para eventFilter
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
        self.ui_numbers[ui] = ui_number
        ui.installEventFilter(self)
        return ui

    @Slot()
    def toggle_ayuda(self, ui):
        if hasattr(ui, "ayuda"):
            ui.ayuda.setVisible(not ui.ayuda.isVisible())

    @Slot()
    def back_clicked_ui(self, ui_number):
        self.cerrar_ui(ui_number)
        self.gestorsg_proxy.LanzarApp()

    ##########################################################################################

    def load_ui(self):
        # UI 1: respuesta/corrección
        ui = self.load_ui_generic(
            UI_RESP, ui_number=1,
            logo_paths={"label_2": LOGO_1, "label_3": LOGO_2},
            botones={
                "correcta": self.correcta_clicked,
                "incorrecta": self.incorrecta_clicked,
                "pasapalabra": self.pasapalabra_clicked,
                "repetir": self.repetir_clicked,
            },
            ayuda_button="ayuda_button",
            back_button="back_button",
            after_load=lambda u: (hasattr(u, "ayuda") and u.ayuda.hide())
        )
        return ui

    def correcta_clicked(self):
        self.resp = "si"
        print("Respuesta: Sí")
        # self.ui.exec_()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()
        self.cerrar_ui(1)

    def incorrecta_clicked(self):
        self.resp = "no"
        print("Respuesta: No")
        # self.ui.exec_()   # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()
        self.cerrar_ui(1)

    def pasapalabra_clicked(self):
        self.resp = "pasapalabra"
        print("Respuesta: No")
        # self.ui.exec_()   # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()
        self.cerrar_ui(1)

    def repetir_clicked (self):
        print("Respuesta: Repetir")
        if self.speech_proxy.isBusy():
            pass
        else:
            self.speech_proxy.say(f"{self.letra_actual}, {self.pregunta_actual}", False)


    ##########################################################################################

    def therapist_ui(self):
        self.running = True
        ui = self.load_ui_generic(
            UI_MENU, ui_number=2,
            logo_paths={"label": LOGO_1, "label_2": LOGO_2},
            botones={"confirmar_button": self.therapist},
            ayuda_button="ayuda_button",
            back_button="back_button",
            after_load=lambda u: (self.configure_combobox(u, "roscos"))
        )
        return ui

    def therapist(self):
        # Obtiene los valores ingresados en los campos
        self.nombre = self.ui2.usuario.toPlainText()
        self.rosco = self.ui2.comboBox.currentText()

        # Validaciones simples
        if not self.nombre:
            print("Por favor ingresa un nombre de usuario.")
            return
        if not self.rosco or self.rosco == "Seleccionar rosco...":
            print("Por favor selecciona un rosco.")
            return

        # Muestra los valores en consola
        print(f"Usuario: {self.nombre}")
        print(f"Rosco: {self.rosco}")

        print("Valores confirmados. Juego listo para comenzar.")
        self.boton = True
        self.running = True
        self.sounds["click"].play()
        self.cerrar_ui(2)
        self.ui2.usuario.clear()
        self.introduccion()

    def configure_combobox(self, ui, folder_path):
        # Acceder al QComboBox por su nombre de objeto
        combobox = ui.findChild(QtWidgets.QComboBox, "comboBox")
        if combobox:
            combobox.addItem("Seleccionar rosco...")
            # Obtener la lista de archivos en la carpeta
            try:
                archivos = [
                    archivo for archivo in os.listdir(folder_path)
                    if os.path.isfile(os.path.join(folder_path, archivo))
                ]
                # Agregar los nombres de los archivos al QComboBox sin la extensión .json
                for archivo in archivos:
                    nombre_sin_extension, ext = os.path.splitext(archivo)
                    # Agregar solo el nombre sin la extensión
                    combobox.addItem(nombre_sin_extension)
            except FileNotFoundError:
                print(f"La carpeta {folder_path} no existe.")
            except Exception as e:
                print(f"Error al listar archivos: {e}")
        else:
            print("No se encontró el QComboBox")

    ##########################################################################################

    def load_check(self):
        ui = self.load_ui_generic(
            UI_CHECK, ui_number=3,
            botones={"si": self.si_clicked, "no": self.no_clicked}
        )
        return ui

    def si_clicked(self):
        self.check = "si"
        print("Respuesta: Sí")
        self.ui3.accept()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()

    def no_clicked(self):
        self.check = "no"
        print("Respuesta: No")
        self.ui3.accept()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()

    ##########################################################################################

    def comenzar_checked(self):
        ui = self.load_ui_generic(
            UI_START, ui_number=4,
            botones={"comenzar": self.comenzar}
        )
        return ui

    def comenzar (self):
        self.running = True
        print("¡El juego ha comenzado!")
        self.ui4.accept()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()

    ##########################################################################################
    
    def eventFilter(self, obj, event):
        """ Captura eventos de la UI """
        # Obtener el número de UI asociado al objeto
        ui_number = self.ui_numbers.get(obj, None)

        if ui_number is not None and event.type() == QtCore.QEvent.Close:
            target_ui = self.ui if ui_number == 1 else getattr(self, f'ui{ui_number}', None)
            
            if obj == target_ui:
                respuesta = QMessageBox.question(
                    target_ui, "Cerrar", f"¿Estás seguro de que quieres salir del juego?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if respuesta == QMessageBox.Yes:
                    print(f"Ventana {ui_number} cerrada por el usuario.")
                    self.reiniciar_variables()
                    self.gestorsg_proxy.LanzarApp()
                    return False  # Permitir el cierre
                else:
                    print(f"Cierre de la ventana {ui_number} cancelado.")
                    event.ignore()  # Bloquear el cierre
                    return True  # **DETENER la propagación del evento para que no se cierre**
        return False  # Propaga otros eventos normalmente
    
    def cerrar_ui(self, numero):
        ui_nombre = "ui" if numero == 1 else f"ui{numero}"
        ui_obj = getattr(self, ui_nombre, None)
        
        if ui_obj:
            ui_obj.removeEventFilter(self)  # Desactiva el event filter
            ui_obj.close()  # Cierra la ventana
            ui_obj.installEventFilter(self)  # Reactiva el event filter
        else:
            print(f"Error: {ui_nombre} no existe en la instancia.")

    ####################################################################################################################################

    @QtCore.Slot()
    def compute(self):

        return True

    def startup_check(self):
        print(f"Testing RoboCompCameraSimple.TImage from ifaces.RoboCompCameraSimple")
        test = ifaces.RoboCompCameraSimple.TImage()
        print(f"Testing RoboCompLEDArray.Pixel from ifaces.RoboCompLEDArray")
        test = ifaces.RoboCompLEDArray.Pixel()
        QTimer.singleShot(200, QApplication.instance().quit)



    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of StartGame method from Pasapalabra interface
    #
    def Pasapalabra_StartGame(self):
        self.boton = False
        self.centrar_ventana(self.ui2)
        self.ui2.show()

        # Espera activa suave a que therapist() ponga self.boton=True
        while not self.boton and self.ui2.isVisible():
            QApplication.processEvents()
            time.sleep(0.05)

        print("Juego terminado o ventana cerrada")

    def centrar_ventana(self, ventana):
        # Obtener la geometría de la pantalla
        pantalla = QApplication.primaryScreen().availableGeometry()

        # Obtener el tamaño de la ventana
        tamano_ventana = ventana.size()

        # Calcular las coordenadas para centrar la ventana
        x = (pantalla.width() - tamano_ventana.width()) // 2
        y = (pantalla.height() - tamano_ventana.height()) // 2

        # Mover la ventana a la posición calculada
        ventana.move(x, y)
    ######################
    # From the RoboCompCameraSimple you can call this methods:
    # self.camerasimple_proxy.getImage(...)

    ######################
    # From the RoboCompCameraSimple you can use this types:
    # RoboCompCameraSimple.TImage

    ######################
    # From the RoboCompEmotionalMotor you can call this methods:
    # self.emotionalmotor_proxy.expressAnger(...)
    # self.emotionalmotor_proxy.expressDisgust(...)
    # self.emotionalmotor_proxy.expressFear(...)
    # self.emotionalmotor_proxy.expressJoy(...)
    # self.emotionalmotor_proxy.expressSadness(...)
    # self.emotionalmotor_proxy.expressSurprise(...)
    # self.emotionalmotor_proxy.isanybodythere(...)
    # self.emotionalmotor_proxy.listening(...)
    # self.emotionalmotor_proxy.pupposition(...)
    # self.emotionalmotor_proxy.talking(...)

    ######################
    # From the RoboCompGestorSG you can call this methods:
    # self.gestorsg_proxy.LanzarApp(...)

    ######################
    # From the RoboCompLEDArray you can call this methods:
    # self.ledarray_proxy.getLEDArray(...)
    # self.ledarray_proxy.setLEDArray(...)

    ######################
    # From the RoboCompLEDArray you can use this types:
    # RoboCompLEDArray.Pixel

    ######################
    # From the RoboCompSpeech you can call this methods:
    # self.speech_proxy.isBusy(...)
    # self.speech_proxy.say(...)


