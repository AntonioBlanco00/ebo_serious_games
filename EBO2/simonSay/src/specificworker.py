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

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces
from time import sleep
from pynput import keyboard
import random
from PySide6 import QtUiTools
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
import pygame
import time
import pandas as pd
from datetime import datetime



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

        self.sounds = {
            "rojo": pygame.mixer.Sound('src/rojo.wav'),
            "verde": pygame.mixer.Sound('src/verde.wav'),
            "azul": pygame.mixer.Sound('src/azul.wav'),
            "amarillo": pygame.mixer.Sound('src/amarillo.wav'),
            "win": pygame.mixer.Sound('src/win.wav'),
            "click": pygame.mixer.Sound('src/click.wav'),
            "game_over": pygame.mixer.Sound('src/game_over.wav'),
        }

        self.nombre = ""
        self.dificultad = ""
        self.intentos = 0
        self.running = False
        self.respuesta = []
        self.rondas = ""


        self.colores_primarios = {
            "negro": (0, 0, 0),
            "rojo": (255, 0, 0),
            "verde": (0, 255, 0),
            "azul": (0, 0, 255),
            "amarillo": (255, 255, 0),
        }

        # self.listener = keyboard.Listener(on_press=self.on_pressed) # Comentado para quitar lo de escape y salir
        # self.listener.start()
        self.ayuda = False

        self.ui = self.load_ui()
        self.ui2 = self.therapist_ui()
        self.ui3 = self.load_check()
        self.ui4 = self.comenzar_checked()

        self.boton = False
        self.reiniciar = False
        self.gameOver = False
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

        self.rondas_complet = 0
        self.fecha = 0
        self.hora = 0
        self.fallos = 0

        self.v1 = 2
        self.v2 = 1

        self.start_question_time = None
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0

        self.df = pd.DataFrame(columns=[
            "Nombre", "Intentos", "Rondas", "Dificultad", "Fecha", "Hora",
            "Rondas completadas", "Fallos", "Tiempo transcurrido (min)", "Tiempo transcurrido (seg)", "Tiempo medio respuesta (seg):"
        ])

        ########## BATERÍA DE RESPUESTAS Y FUNCIÓN PARA ALEATORIZAR ##########

        self.bateria_responder = [
            "Responde ahora!",
            "Te toca responder!",
            "Es tu turno, adelante!",
            "Vamos, responde ya!",
            "Es tu momento, responde ahora!",
            "¡Adelante, es tu turno!",
            "¡Responde con confianza!",
            "¡Vamos, tú puedes responder ahora!"
        ]

        self.bateria_aciertos = [
            "¡Has acertado!",
            "¡Lo estás haciendo genial!",
            "¡Acertaste, increíble!",
            "¡Eso es correcto, muy bien hecho!",
            "¡Perfecto, acertaste!",
            "¡Muy bien, respuesta correcta!",
            "¡Qué acierto tan brillante!",
            "¡Excelente, lo conseguiste!"
        ]

        self.bateria_fallos = [
            "Fallo, pero no te preocupes!",
            "No pasa nada, todos fallamos!",
            "Sigue intentándolo, ¡lo harás mejor!",
            "Es un error, pero no te rindas!",
            "¡Ánimo, la próxima será mejor!",
            "¡No te preocupes, sigue adelante!",
            "¡Un tropiezo no define tu esfuerzo!",
            "¡No pasa nada, la práctica hace al maestro!"
        ]

        self.bateria_rondas = [
            "Es hora de la ronda número {ronda}!",
            "¡Ronda número {ronda}, vamos allá!",
            "¡Toca la ronda número {ronda}!",
            "Preparados para la ronda número {ronda}!",
            "Comienza la ronda número {ronda}, ¡suerte!",
            "¡Atentos, comienza la ronda {ronda}!",
            "¡Vamos con la emocionante ronda número {ronda}!",
            "¡Que comience la ronda número {ronda}, mucha suerte!"
        ]

        self.bateria_fin_juego = [
            "El juego ha terminado, ¡lo has hecho genial!",
            "¡Fin del juego, muy bien jugado!",
            "Esto ha sido todo, ¡excelente trabajo!",
            "¡Gran final, lo hiciste estupendamente!",
            "Juego terminado, ¡felicitaciones por tu esfuerzo!",
            "¡Increíble, has completado el juego!",
            "¡Fantástico, qué gran partida!",
            "¡Finalizado, te has lucido!"
        ]

        ######################################################################

    def agregar_resultados(self, nombre, intentos, rondas, dificultad, fecha, hora, rondas_completadas, fallos, tiempo_transcurrido_min, tiempo_transcurrido_seg, tiempo_medio_respuesta):
        # Crea un diccionario con los datos nuevos
        nuevo_resultado = {
            "Nombre": nombre,
            "Intentos": intentos,
            "Rondas": rondas,
            "Dificultad": dificultad,
            "Fecha": fecha,
            "Hora": hora,
            "Rondas completadas": rondas_completadas,
            "Fallos": fallos,
            "Tiempo transcurrido (min)": tiempo_transcurrido_min,
            "Tiempo transcurrido (seg)": tiempo_transcurrido_seg,  # Corregido aquí
            "Tiempo medio respuesta (seg):": tiempo_medio_respuesta  # Corregido aquí
        }

        # Convierte el diccionario en un DataFrame de una fila
        nuevo_df = pd.DataFrame([nuevo_resultado])

        # Agrega la nueva fila al DataFrame existente
        self.df = pd.concat([self.df, nuevo_df], ignore_index=True)


    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    ########## BATERÍA DE RESPUESTAS Y FUNCIÓN PARA ALEATORIZAR ##########

    def elegir_respuesta(self, bateria, **kwargs):
        if "ronda" in kwargs:
            # Si el kwargs contiene 'ronda', formatea las respuestas de las rondas
            bateria = [respuesta.format(ronda=kwargs["ronda"]) if "ronda" in respuesta else respuesta for respuesta in
                       bateria]
        return random.choice(bateria)

    ######################################################################

    def procesoJuego(self):
        if self.dificultad == "facil":
            self.v1 = 2
            self.v2 = 1
        elif self.dificultad == "medio":
            self.v1 = 1
            self.v2 = 0.5
        elif self.dificultad == "dificil":
            self.v1 = 0.5
            self.v2 = 0.25
        else:
            self.v1 = 1
            self.v2 = 0.5

        self.color_aleatorio = []
        i = 0

        # self.speech_proxy.say("Por cierto, recuerda que yo te diré cuando debes empezar a responder.", False)
        sleep(0.5)

        while i < int(self.rondas) and self.running:
            self.speech_proxy.say(self.elegir_respuesta(self.bateria_rondas, ronda= i+1), False)

            print(f"Ronda número {i + 1}")
            self.rondas_complet = i+1

            self.terminaHablar()

            self.random_color()
            print(self.color_aleatorio)

            for color in self.color_aleatorio:
                self.encender_LEDS(color)
                sleep(self.v1)
                self.encender_LEDS("negro")
                sleep(self.v2)

            # self.speech_proxy.say(self.elegir_respuesta(self.bateria_responder), False)
            self.start_question_time = None
            self.get_respuesta()
            print("Tu respuesta ha sido:", self.respuesta)

            if not self.running:
                break
            i += 1

        if i == int(self.rondas):
            self.finJuego()



    def finJuego(self):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time  # Tiempo en segundos

        # Convertir el tiempo a minutos y segundos
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        self.speech_proxy.say(self.elegir_respuesta(self.bateria_fin_juego), False)

        print(f"Juego terminado. Tiempo transcurrido: {minutes} minutos y {seconds} segundos.")

        self.terminaHablar()
        pygame.mixer.stop()
        self.sounds["win"].play()
        self.set_all_LEDS_colors(0, 255, 0, 0)
        self.emotionalmotor_proxy.expressSurprise()
        sleep(0.5)
        self.encender_LEDS("negro")
        sleep(0.5)
        self.boton = False

        self.media = sum(self.responses_times) / len(self.responses_times)
        self.agregar_resultados(self.nombre, self.intentos, self.rondas, self.dificultad, self.fecha, self.hora, self.rondas_complet, self.fallos, minutes, seconds, self.media)

        self.guardar_resultados()

        self.gestorsg_proxy.LanzarApp()

        return


    # def on_pressed(self,key):
    #     if key == keyboard.Key.esc:  # Detener cuando se presiona 'esc'
    #         print("Tecla ESC presionada, deteniendo.")
    #         self.running = False
    #         self.stop_detection()
    #
    # def stop_detection(self):
    #     print("Deteniendo el juego...")
    #     self.running = False
    #     self.reiniciar = True
    #     if self.ui.show():
    #         self.ui.close()
    #     elif self.ui2.show():
    #         self.ui2.close()
    #     elif self.ui3.show():
    #         self.ui3.close()
    #     elif self.ui4.show():
    #         self.ui4.close()
    #     self.reinit()


    def random_color(self):
        color = random.choice(["rojo", "azul", "verde", "amarillo"])
        # Comprobar si el último color es el mismo que el nuevo
        while self.color_aleatorio and self.color_aleatorio[-1] == color:
            color = random.choice(["rojo", "azul", "verde", "amarillo"])
        self.color_aleatorio.append(color)

    def encender_LEDS(self,color):

        if color == "rojo" and self.gameOver:
            self.sounds["game_over"].play()

        elif color in self.sounds:
            pygame.mixer.stop()
            self.sounds[color].play()

        if color== "negro":
            self.set_all_LEDS_colors(0, 0, 0, 0)
        elif color == "rojo":
            self.set_all_LEDS_colors(255, 0, 0, 0)
        elif color== "verde":
            self.set_all_LEDS_colors(0, 255, 0, 0)
        elif color == "azul":
            self.set_all_LEDS_colors(0, 0, 255, 0)
        elif color == "amarillo":
            self.set_all_LEDS_colors(255, 255, 0, 0)
        else:
            print("Error, apagando LEDS")
            self.set_all_LEDS_colors(0, 0, 0, 0)

    def set_all_LEDS_colors(self, red=0, green=0, blue=0, white=0):
        pixel_array = {i: ifaces.RoboCompLEDArray.Pixel(red=red, green=green, blue=blue, white=white) for i in
                       range(self.NUM_LEDS)}
        self.ledarray_proxy.setLEDArray(pixel_array)

    def introduccion (self):

        QApplication.processEvents()

        self.emotionalmotor_proxy.expressJoy()

        self.speech_proxy.say(f"Hola {self.nombre}, vamos a jugar a Simón Dice.", False)

        print (f"Hola {self.nombre}, vamos a jugar a Simón Dice.")

        self.speech_proxy.say("Simón Dice es un juego de memoria en el que debes repetir la secuencia de colores que se ilumina. ", False)

        print("Simón Dice es un juego de memoria en el que debes repetir la secuencia de colores que se ilumina. ")

        self.speech_proxy.say ("¿Quieres que te explique el juego?", False)

        print("¿Quieres que te explique el juego?")

        self.terminaHablar()

        # exp = input ("Introduce Si o No si quieres que explique el juego: "). lower()
        self.check = ""
        self.centrar_ventana(self.ui3)
        self.ui3.show()
        QApplication.processEvents()
        self.ui3.exec_()



        if self.check == "si":
            self.speech_proxy.say("A medida que avances, la secuencia se volverá más larga, poniendo a prueba tu memoria y concentración. "
                                  "Cómo jugar: Se mostrará un color en mis luces, por ejemplo rojo. ", False)

            print ("A medida que avances, la secuencia se volverá más larga, poniendo a prueba tu memoria y concentración. "
                                  "Cómo jugar: Se mostrará un color en mis luces, por ejemplo rojo. ")

            self.terminaHablar()

            self.set_all_LEDS_colors(255, 0, 0, 0)
            sleep(1)
            self.set_all_LEDS_colors(0,0,0,0)


            self.speech_proxy.say("Deberás introducir ese mismo color. "
                                  "Al acertar, añadiré otro color a la secuencia, por ejemplo rojo + azul). ", False)

            print("Deberás introducir ese mismo color. "
                                  "Al acertar, añadiré otro color a la secuencia, por ejemplo rojo + azul). ")

            self.terminaHablar()

            self.set_all_LEDS_colors(255, 0, 0, 0)
            sleep(1)
            self.set_all_LEDS_colors(0, 0, 0, 0)
            sleep(1)
            self.set_all_LEDS_colors(0, 0, 255, 0)
            sleep(1)
            self.set_all_LEDS_colors(0, 0, 0, 0)



            self.speech_proxy.say("Ahora debes repetir ambos en el orden correcto. "
                                  "Con cada turno, la secuencia crece y debes recordar cada color en el orden correcto.", False)

            print("Ahora debes repetir ambos en el orden correcto. "
                                  "Con cada turno, la secuencia crece y debes recordar cada color en el orden correcto.")


        # DESCOMENTAR PARA ACTIVAR EL QUE PREGUNTE SI QUIERES HACER UNA PRUEBA

        # self.speech_proxy.say("¿Quieres hacer una prueba?", False)
        #
        # print("¿Quieres hacer una prueba?")
        #
        # self.terminaHablar()
        #
        # # prueb = input("¿Quieres hacer una prueba?: ") . lower()
        #
        # self.check = ""
        # self.centrar_ventana(self.ui3)
        # self.ui3.show()
        # self.ui3.exec_()
        #
        #
        # if self.check == "si":
        #     self.prueba()

        ##########################################################################

        if self.check == "no":
            if int(self.intentos) == 1:
                self.speech_proxy.say("Vamos a ver cuánto tiempo eres capaz de seguir la secuencia sin equivocarte", False)
                print("Vamos a ver cuánto tiempo eres capaz de seguir la secuencia sin equivocarte")

            elif int(self.intentos) > 1:
                self.speech_proxy.say(f"""Tienes un número limitado de intentos. Si te equivocas en algún color {self.intentos}
                                        veces antes de completar la secuencia, el juego terminará.""", False)

                print(f"""Tienes un número limitado de intentos. Si te equivocas en algún color {self.intentos}
                                        veces antes de completar la secuencia, el juego terminará.""")

            self.speech_proxy.say("¡Comencemos con el juego!", False)

            print("¡Comencemos con el juego!")

        self.terminaHablar()

        # print("Presiona Enter para iniciar el juego...")
        # input()
        # self.running = True
        self.centrar_ventana(self.ui4)
        self.ui4.show()
        self.ui4.exec_()
        self.start_time =time.time()
        self.fecha = datetime.now().strftime("%d-%m-%Y")
        self.hora = datetime.now().strftime("%H:%M:%S")

    def get_respuesta(self):
        self.respuesta = []
        self.intent = 0
        
        if self.start_question_time is None:
            self.start_question_time = time.time()

        print("Introduce la secuencia de colores uno en uno")

        # Inicio de la ronda, aparecen los 4 botones.
        while len(self.respuesta) < len(self.color_aleatorio) and self.running is True:
            # Mostrar la interfaz gráfica con botones
            self.centrar_ventana(self.ui)
            self.ui.show()
            QApplication.processEvents()

            self.emotionalmotor_proxy.expressJoy()
            # Verifica si la respuesta es correcta hasta el momento, cada pulsado de botón.
            for idx in range(len(self.respuesta)):
                if self.respuesta[idx] != self.color_aleatorio[idx]:
                    self.intent += 1
                    self.restantes = int(self.intentos) - int(self.intent)
                    # self.end_question_time = time.time()

                    if self.restantes > 1:
                        self.speech_proxy.say(
                            f"Respuesta incorrecta. {self.elegir_respuesta(self.bateria_fallos)} .Te quedan {self.restantes} intentos.", False)

                    elif self.restantes == 1:
                        self.speech_proxy.say(
                            f"Respuesta incorrecta. {self.elegir_respuesta(self.bateria_fallos)}.Este es tu último intento.", False)
                    else:
                        self.speech_proxy.say(
                            f"Respuesta incorrecta, no te quedan más intentos.", False)

                    self.cerrar_ui(1)
                    self.terminaHablar()

                    if self.restantes <= 0:
                        self.end_time = time.time()
                        self.elapsed_time = self.end_time - self.start_time  # Tiempo en segundos
                        # self.response_time = self.end_question_time - self.start_question_time
                        # self.responses_times.append(self.response_time)
                        self.media = sum(self.responses_times) / len(self.responses_times)
                        # Convertir el tiempo a minutos y segundos
                        minutes = int(self.elapsed_time // 60)
                        seconds = int(self.elapsed_time % 60)
                        rondas = int(self.rondas_complet) - 1 # Si perdías ponía siempre una ronda completada de más
                        print("Game Over")
                        self.speech_proxy.say(self.elegir_respuesta(self.bateria_fin_juego), False)
                        # print("Has perdido. El juego ha terminado")
                        print(f"Juego terminado. Tiempo transcurrido: {minutes} minutos y {seconds} segundos.")
                        # self.resultados.append([self.nombre, self.fecha, self.rondas_complet, self.elapsed_time])
                        # print(f"nombre: {self.resultados[0][0]}, fecha: {self.resultados[0][1]}, rondas_complet: {self.resultados[0][2]}, "
                        #     f"tiempo transcurrido (en segundos): {self.resultados[0][3]}")
                        self.terminaHablar()
                        self.fantasia_color()
                        # self.ui.close()  # Cierra la ventana
                        self.running = False
                        self.boton = False
                        self.agregar_resultados(self.nombre, self.intentos, self.rondas, self.dificultad, self.fecha, self.hora,
                                                rondas, self.fallos, minutes, seconds ,self.media)

                        self.guardar_resultados()

                        self.gestorsg_proxy.LanzarApp()
                        return

                    self.fallos = self.fallos + 1
                    print("Mostrando la secuencia nuevamente...")
                    self.speech_proxy.say("Atención, repito la secuencia.", False)
                    self.respuesta = []  # Reinicia la respuesta
                    self.terminaHablar()


                    print(self.color_aleatorio)
                    for color in self.color_aleatorio:
                        self.encender_LEDS(color)
                        sleep(self.v1)
                        self.encender_LEDS("negro")
                        sleep(self.v2)

                    break
        
        if self.running is True:
            self.cerrar_ui(1) # Cierra la ventana cuando el juego termine
            # Si llegamos hasta aqui, la respuesta es correcta
            self.speech_proxy.say(self.elegir_respuesta(self.bateria_aciertos), False)
            self.terminaHablar()
            print("Tu respuesta ha sido:", self.respuesta)


    def fantasia_color(self):
        i = 0
        self.emotionalmotor_proxy.expressJoy()
        self.gameOver = True
        while i < 3:
            self.encender_LEDS("rojo")
            sleep(0.5)
            self.encender_LEDS("negro")
            sleep(0.5)
            i += 1
        self.gameOver = False


    def prueba (self):
        self.speech_proxy.say("¡Genial! Comencemos con la prueba. Vamos a hacer 2 rondas",False)

        print("¡Genial! Comencemos con la prueba. Vamos a hacer 2 rondas")

        self.terminaHablar()

        self.color_aleatorio = []
        self.running = True
        i = 0
        while i <= 1 and self.running:
            self.speech_proxy.say(f"Ronda número {i + 1}", False)
            print(f"Ronda número {i + 1}")
            self.terminaHablar()
            self.random_color()
            print(self.color_aleatorio)

            for color in self.color_aleatorio:
                self.encender_LEDS(color)
                sleep(1)
                self.encender_LEDS("negro")
                sleep(0.5)

            self.get_respuesta()
            print("Tu respuesta ha sido:", self.respuesta)
            i += 1

        if i == 2:
            self.running = False
            self.speech_proxy.say ("¡Lo has hecho muy bien!",False)
            print("¡Lo has hecho muy bien!")

    def terminaHablar(self):
        sleep(2.5)
        while self.speech_proxy.isBusy():
            pass

    ####################################################################################################################################
    
    def load_ui (self):
        #Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("igs/mainUI.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.rojo.clicked.connect(self.rojo_clicked)
        ui.azul.clicked.connect(self.azul_clicked)
        ui.verde.clicked.connect(self.verde_clicked)
        ui.amarillo.clicked.connect(self.amarillo_clicked)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 1  
        ui.installEventFilter(self) 

        return ui

    def rojo_clicked(self):
        self.respuesta.append("rojo")
        self.sounds["rojo"].play()
        self.register_time_until_pressed()
        print("Respuesta: Rojo")

    def azul_clicked(self):
        self.respuesta.append("azul")
        self.sounds["azul"].play()
        self.register_time_until_pressed()
        print("Respuesta: Azul")

    def verde_clicked(self):
        self.respuesta.append("verde")
        self.sounds["verde"].play()
        self.register_time_until_pressed()
        print("Respuesta: Verde")

    def amarillo_clicked(self):
        self.respuesta.append("amarillo")
        self.sounds["amarillo"].play()
        self.register_time_until_pressed()
        print("Respuesta: Amarillo")
    
    def register_time_until_pressed(self):
        if self.end_question_time is None:
            self.end_question_time = time.time()
        
        self.response_time = self.end_question_time - self.start_question_time
        if self.response_time < 0.00001:
            print("Error, valor no almacenado")
        else:
            self.responses_times.append(self.response_time)

        self.start_question_time = None
        self.end_question_time = None

        if self.start_question_time is None:
            self.start_question_time = time.time()
        
        print("------------------------------")
        print(f"Tiempo de respuesta: {self.response_time}")
        print("------------------------------")

    ####################################################################################################################################

    def therapist_ui (self):
        #Cargar interfaz
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("igs/therapistUI.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()
        ui.facil.clicked.connect(self.facil_clicked)
        ui.medio.clicked.connect(self.medio_clicked)
        ui.dificil.clicked.connect(self.dificil_clicked)

        ui.confirmar_button.clicked.connect(self.therapist)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 2  
        ui.installEventFilter(self) 

        return ui

    def facil_clicked(self):
        self.dificultad = "facil"
        self.sounds["click"].play()
        self.ui2.dificultad_elegida.setText("Dificultad elegida: Fácil")
        print("Dificultad elegida: Fácil")

    def medio_clicked(self):
        self.dificultad = "medio"
        self.sounds["click"].play()
        self.ui2.dificultad_elegida.setText("Dificultad elegida: Medio")
        print("Dificultad seleccionada: Medio")

    def dificil_clicked(self):
        self.dificultad = "dificil"
        self.sounds["click"].play()
        self.ui2.dificultad_elegida.setText("Dificultad elegida: Difícil")
        print("Dificultad seleccionada: Difícil")

    def therapist(self):
        # Obtiene los valores ingresados en los campos
        self.nombre = self.ui2.usuario.toPlainText()
        self.intentos = self.ui2.intentos.toPlainText()
        self.rondas = self.ui2.rondas.toPlainText()

        # Validaciones simples
        if not self.nombre:
            print("Por favor ingresa un nombre de usuario.")
            return
        if not self.intentos.isdigit() or int(self.intentos) <= 0:
            print("Por favor ingresa un número válido de intentos.")
            return
        if not self.rondas.isdigit() or int(self.rondas) <= 0:
            print("Por favor ingresa un número válido de rondas.")
            return
        if not self.dificultad:
            print("Por favor selecciona una dificultad.")
            return

        # Muestra los valores en consola
        print(f"Usuario: {self.nombre}")
        print(f"Intentos: {self.intentos}")
        print(f"Rondas: {self.rondas}")
        print(f"Dificultad: {self.dificultad}")

        print("Valores confirmados. Juego listo para comenzar.")
        self.boton = True
        self.fallos = 0 # Reinicia contador al empezar juego
        self.sounds["click"].play()
        self.cerrar_ui(2)
        self.ui2.usuario.clear()
        self.ui2.intentos.clear()
        self.ui2.rondas.clear()
        self.introduccion()
        # self.nivel() # Ya no se usa nivel, el nivel se cambia al pulsar y se usa directamente procesoJuego
        self.procesoJuego()

    ####################################################################################################################################
    
    def load_check(self):
        # Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("igs/botonUI.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.si.clicked.connect(self.si_clicked)
        ui.no.clicked.connect(self.no_clicked)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 3  
        ui.installEventFilter(self) 

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
        
    ####################################################################################################################################

    def comenzar_checked(self):
        # Carga la interfaz desde el archivo .ui
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("igs/comenzarUI.ui")
        file.open(QtCore.QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        # Conectar botones a funciones
        ui.comenzar.clicked.connect(self.comenzar)
        
        # Cerrar con la x
        if not hasattr(self, 'ui_numbers'):
            self.ui_numbers = {}
            
        self.ui_numbers[ui] = 4  
        ui.installEventFilter(self) 

        return ui

    def comenzar (self):
        self.running = True
        self.set_all_LEDS_colors(0, 0, 0, 0)
        print("¡El juego ha comenzado!")
        self.ui4.accept()  # Cierra el diálogo cuando el botón es presionado
        self.sounds["click"].play()


    ####################################################################################################################################
    
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
                    self.set_all_LEDS_colors(0, 0, 0, 0)
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


    # def reinit (self):
    #         print("Presiona Enter para reiniciar el juego o 'q' para salir...")
    #         user_input = input()
    #         if user_input.lower() == 'q':
    #             print("Saliendo del juego. ¡Adiós!")
    #
    #         elif user_input == "":
    #             print("Reiniciando el juego...")
    #             self.reiniciar = False
    #             self.boton = False
    #             self.ui2.show()

    def guardar_resultados(self):
        archivo = "resultados_juego.json"

        # Inicializar un DataFrame vacío para los datos existentes
        datos_existentes = pd.DataFrame()

        # Intentar leer el archivo existente si existe
        if os.path.exists(archivo):
            try:
                datos_existentes = pd.read_json(archivo, orient='records', lines=True)
            except ValueError:
                print("El archivo JSON existente tiene un formato inválido o está vacío. Sobrescribiendo el archivo.")

        # Verificar que el DataFrame actual no esté vacío
        if self.df.empty:
            print("El DataFrame de nuevos resultados está vacío. No se guardará nada.")
            return

        # Concatenar los datos existentes con los nuevos (si existen)
        if not datos_existentes.empty:
            self.df = pd.concat([datos_existentes, self.df], ignore_index=True)

        # Eliminar duplicados basados en todas las columnas
        self.df = self.df.drop_duplicates()

        # Guardar el DataFrame combinado en formato JSON
        self.df.to_json(archivo, orient='records', lines=True)

        print(f"Resultados guardados correctamente en {archivo}")

        # Leer y mostrar el archivo actualizado para verificar
        df_resultados = pd.read_json(archivo, orient='records', lines=True)
        print(df_resultados)

        # Reiniciar la variable self.df para la próxima partida
        self.reiniciar_variables()
        print("Variable self.df reiniciada para la próxima partida.")

    def reiniciar_variables(self):
        self.nombre = ""
        self.dificultad = ""
        self.intentos = 0
        self.running = False
        self.respuesta = []
        self.rondas = ""
        
        self.boton = False
        self.reiniciar = False
        self.gameOver = False
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

        self.rondas_complet = 0
        self.fecha = 0
        self.hora = 0
        self.fallos = 0

        self.v1 = 2
        self.v2 = 1

        self.start_question_time = None
        self.end_question_time = 0
        self.response_time = 0
        self.responses_times = []
        self.media = 0

        self.df = pd.DataFrame(columns=[
            "Nombre", "Intentos", "Rondas", "Dificultad", "Fecha", "Hora",
            "Rondas completadas", "Fallos", "Tiempo transcurrido (min)", "Tiempo transcurrido (seg)", "Tiempo medio respuesta (seg):"
        ])


    @QtCore.Slot()
    def compute(self):
        # self.get_respuesta()

        return True

    def startup_check(self):
        print(f"Testing RoboCompCameraSimple.TImage from ifaces.RoboCompCameraSimple")
        test = ifaces.RoboCompCameraSimple.TImage()
        print(f"Testing RoboCompLEDArray.Pixel from ifaces.RoboCompLEDArray")
        test = ifaces.RoboCompLEDArray.Pixel()
        QTimer.singleShot(200, QApplication.instance().quit)


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
    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of StartGame method from JuegoSimonSay interface
    #
    def JuegoSimonSay_StartGame(self):
        self.set_all_LEDS_colors(255,0,0,0)
        self.boton = False # Gitaneada para que vaya la x
        while not self.boton:
            self.boton = True # Gitaneada para que vaya la x
            self.centrar_ventana(self.ui2)
            self.ui2.show()
            QApplication.processEvents()
            sleep(1)

        print("Juego terminado o ventana cerrada")
        # pass


    # ===================================================================
    # ===================================================================


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


