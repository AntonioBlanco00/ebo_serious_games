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

from PySide6 import QtUiTools
from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import traceback
import time
import threading  # Necesario para ejecutar el bucle en segundo plano
import math

UI_TEST = "src/TEST.ui"

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class JuegoSelector(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Seleccionar Juego y Mensaje")
        self.setFixedSize(600, 325)  # Fija el tamaño de la ventana

        # Layout principal
        layout = QVBoxLayout()

        # Etiqueta para el juego
        self.juego_label = QLabel("Selecciona un juego:")
        layout.addWidget(self.juego_label)

        # ComboBox para seleccionar el juego
        self.juego_combo = QComboBox()
        self.juego_combo.addItem("Conversation_Game")
        self.juego_combo.addItem("Conversation_Test")
        self.juego_combo.addItem("De_charla_con_EBO")
        self.juego_combo.addItem("Colegios")
        self.juego_combo.addItem("Ebo_autonomo_test")
        layout.addWidget(self.juego_combo)

        # Etiqueta para el mensaje
        self.mensaje_label = QLabel("Introduce un mensaje inicial:")
        layout.addWidget(self.mensaje_label)

        # Campo de texto para el mensaje
        self.mensaje_input = QLineEdit()
        layout.addWidget(self.mensaje_input)

        # Botones de Aceptar y Atrás
        self.aceptar_button = QPushButton("Aceptar")
        self.aceptar_button.clicked.connect(self.aceptar)
        layout.addWidget(self.aceptar_button)

        self.atras_button = QPushButton("Atrás")
        self.atras_button.clicked.connect(self.reject)  # Cierra el widget
        layout.addWidget(self.atras_button)

        # Establecer el layout del widget
        self.setLayout(layout)

        self.autonomo = False

    def aceptar(self):
        # Al hacer clic en Aceptar, almacenamos los valores seleccionados
        self.juego_seleccionado = self.juego_combo.currentText()
        self.mensaje_inicial = self.mensaje_input.text()
        self.accept()  # Cierra el widget


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        self.NUM_LEDS = 54
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)
        self.ui.texto_gpt.setVisible(False)

        # Inicializar el lock de ASR de forma segura
        self._asr_lock = getattr(self, "_asr_lock", threading.Lock())
        self.autonomo_thread = None  # Inicializar el hilo

        # Botón para hablar
        self.ui.pushButton.clicked.connect(self.enviar_tts)

        # Agregar evento de teclado para detectar Enter
        self.ui.plainTextEdit.installEventFilter(self)

        # Botón para el modo chatGPT
        self.ui.GPT_mode.clicked.connect(self.activar_gpt)

        # Botones de emociones
        self._emociones = {
            "Feliz": self.ebomoods_proxy.expressJoy,
            "Asco": self.ebomoods_proxy.expressDisgust,
            "Sorpresa": self.ebomoods_proxy.expressSurprise,
            "Triste": self.ebomoods_proxy.expressSadness,
            "Enfado": self.ebomoods_proxy.expressAnger,
            "Miedo": self.ebomoods_proxy.expressFear,
        }

        self.ui.feliz.clicked.connect(lambda: self.emotion_clicked("Feliz"))
        self.ui.asco.clicked.connect(lambda: self.emotion_clicked("Asco"))
        self.ui.sorpresa.clicked.connect(lambda: self.emotion_clicked("Sorpresa"))
        self.ui.triste.clicked.connect(lambda: self.emotion_clicked("Triste"))
        self.ui.enfado.clicked.connect(lambda: self.emotion_clicked("Enfado"))
        self.ui.miedo.clicked.connect(lambda: self.emotion_clicked("Miedo"))

        # Botones de movimiento
        self._movimientos = {
            "Adelante": (0, 50),
            "Izquierda": (-50, 0),
            "Derecha": (50, 0),
            "Atras": (0, -50),
            "Quieto": (0, 0),
        }

        self.ui.adelante.clicked.connect(lambda: self.move_clicked("Adelante"))
        self.ui.izquierda.clicked.connect(lambda: self.move_clicked("Izquierda"))
        self.ui.derecha.clicked.connect(lambda: self.move_clicked("Derecha"))
        self.ui.atras.clicked.connect(lambda: self.move_clicked("Atras"))
        self.ui.quieto.clicked.connect(lambda: self.move_clicked("Quieto"))

        # Apagar LEDs
        self.ui.leds_off.clicked.connect(self.apagar_leds)

        console.print("[bold green]APP INICIADA[/bold green]")

    def __del__(self):
        """Destructor"""

    def setParams(self, params):

        return True

    @QtCore.Slot()
    def compute(self):

        return True

    def set_all_LEDS_colors(self, red=0, green=0, blue=0, white=0):
        try:
            pixel = ifaces.RoboCompLEDArray.Pixel(red=red, green=green, blue=blue, white=white)
            pixel_array = {i: pixel for i in range(self.NUM_LEDS)}
            self.ledarray_proxy.setLEDArray(pixel_array)
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al actualizar LEDs: {e}")

    def apagar_leds(self):
        self.set_all_LEDS_colors(red=0, green=0, blue=0, white=0)

    def _iniciar_ebo_autonomo_thread(self):
        """MÉTODO AÑADIDO: Ejecuta la lógica de inicio y el bucle en un hilo separado."""

        # 1. Asegurarse de que el lock existe (aunque ya se hizo en __init__)
        self._asr_lock = getattr(self, "_asr_lock", threading.Lock())

        # 2. ADQUIRIR el lock para evitar que el ASR escuche la respuesta de startChat
        self._asr_lock.acquire()
        try:
            self.gpt_proxy.startChat()
            time.sleep(2)  # Pausa inicial para que la respuesta de TTS comience

            # 3. Esperar a que termine de hablar, mientras el lock está activo
            ok = self.wait_for_speech_cycle_forgiving(
                wait_for_start_timeout=5,
                wait_for_end_timeout=120.0,
                poll_interval=0.05,
                post_silence_grace=0.5,
                fallback_wait_after_no_start=0.8
            )
            if not ok:
                time.sleep(1.0)
        finally:
            # 4. LIBERAR el lock después de que el robot haya terminado de hablar.
            self._asr_lock.release()

        # 5. Iniciar el bucle autónomo (que se queda bloqueado en este hilo secundario)
        self.ebo_autonomo_test()

    def activar_gpt(self):
        print("ACTIVAR CHATGPT PULSADO")

        # Crear y mostrar el widget para seleccionar juego y mensaje
        self.juego_selector = JuegoSelector()

        # Mostrar el widget como un diálogo modal
        if self.juego_selector.exec() == QDialog.Accepted:
            # Al aceptar, obtenemos los valores seleccionados
            self.juego_seleccionado = self.juego_selector.juego_seleccionado
            print("JUEGO SELECCIONADO HA SIDO::::: ", self.juego_seleccionado)
            self.mensaje_inicial = self.juego_selector.mensaje_inicial

            print(f"\nEstableciendo GameInfo: {self.juego_seleccionado} con mensaje: {self.mensaje_inicial}\n")
            self.gpt_proxy.setGameInfo(self.juego_seleccionado, self.mensaje_inicial)

            if self.juego_seleccionado == "Ebo_autonomo_test":
                self.autonomo = True
                self.actualizar_interfaz()
                print("ACTUALIZANDO INTERFAZ")

                # *** MODIFICACIÓN CLAVE: INICIAR EN HILO SEPARADO ***
                self.autonomo_thread = threading.Thread(target=self._iniciar_ebo_autonomo_thread)
                self.autonomo_thread.daemon = True  # Esto permite que la aplicación se cierre sin esperar al hilo.
                self.autonomo_thread.start()
                # **************************************************

            else:
                # Actualizamos la interfaz principal con los nuevos valores
                self.actualizar_interfaz()

                # Aquí, podrías almacenar la variable juego_seleccionado para usarla en otros lugares
                print(f"Juego seleccionado: {self.juego_seleccionado}")
                print(f"Mensaje inicial: {self.mensaje_inicial}")

                print(f"\nIniciando el juego: {self.juego_seleccionado} para el usuario: {self.mensaje_inicial}...\n")
                self.gpt_proxy.setGameInfo(self.juego_seleccionado, self.mensaje_inicial)
                self.gpt_proxy.startChat()

    def actualizar_interfaz(self):
        """Activa el modo GPT en la UI y reconecta señales de forma segura."""
        self.ui.GPT_mode.setText("Salir modo GPT")
        self.ui.textEdit.clear()
        self.ui.textEdit.insertPlainText("Escribe aquí lo que decir a EBO")
        self.ui.texto_gpt.setVisible(True)

        # pushButton: pasar de TTS → GPT
        try:
            self.ui.pushButton.clicked.disconnect()
        except TypeError:
            pass
        self.ui.pushButton.clicked.connect(self.enviar_gpt)

        # GPT_mode: pasar de activar → desactivar
        try:
            self.ui.GPT_mode.clicked.disconnect()
        except TypeError:
            pass
        self.ui.GPT_mode.clicked.connect(self.desactivar_gpt)

        # Limpia el input
        self.ui.plainTextEdit.clear()

    def regenerar_interfaz(self):
        """Vuelve al modo TTS normal y reconecta señales de forma segura."""
        self.ui.GPT_mode.setText("Entrar modo GPT")
        self.ui.textEdit.clear()
        self.ui.textEdit.setPlainText("Escribe aquí lo que quieres que diga EBO")
        self.ui.texto_gpt.setVisible(False)

        # pushButton: pasar de GPT → TTS
        try:
            self.ui.pushButton.clicked.disconnect()
        except TypeError:
            pass
        self.ui.pushButton.clicked.connect(self.enviar_tts)

        # GPT_mode: pasar de desactivar → activar
        try:
            self.ui.GPT_mode.clicked.disconnect()
        except TypeError:
            pass
        self.ui.GPT_mode.clicked.connect(self.activar_gpt)

        # Limpia el input
        self.ui.plainTextEdit.clear()

    def enviar_gpt(self):
        """Envía el texto actual al chat GPT y limpia el campo."""
        mensaje = self.ui.plainTextEdit.toPlainText()
        self.ui.plainTextEdit.clear()
        try:
            self.gpt_proxy.continueChat(mensaje)
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al enviar mensaje a GPT: {e}")

    def desactivar_gpt(self):
        """Sale del modo GPT y restaura la interfaz."""
        try:
            # Poner 'autonomo' a False para salir del bucle en el hilo
            self.autonomo = False
            self.gpt_proxy.continueChat("03827857295769204")

            # Esperar un poco a que el hilo termine (opcional, pero recomendable)
            if self.autonomo_thread and self.autonomo_thread.is_alive():
                # Nota: Si el hilo está bloqueado en listenandtranscript, puede que no termine inmediatamente.
                time.sleep(0.5)

        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al salir de GPT: {e}")

        self.regenerar_interfaz()

    def eventFilter(self, source, event):
        """Detecta Enter en el plainTextEdit y envía según modo activo."""
        if source is self.ui.plainTextEdit and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if self.ui.texto_gpt.isVisible():
                    self.enviar_gpt()
                else:
                    self.enviar_tts()
                return True  # Consumimos el evento
        return super().eventFilter(source, event)

    def enviar_tts(self):
        """Envía el texto a TTS; intenta animar alegría y muestra mensajes claros."""
        try:
            self.emotionalmotor_proxy.expressJoy()
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold yellow]Aviso[/bold yellow]: no se pudo expresar alegría: {e}")

        texto = self.ui.plainTextEdit.toPlainText().strip()
        if not texto:
            console.print("[bold yellow]Aviso[/bold yellow]: no hay texto para enviar a TTS.")
            return

        console.print(f"Texto enviado a TTS: {texto}")
        self.ui.plainTextEdit.clear()

        try:
            self.speech_proxy.say(texto, False)
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al enviar TTS: {e}")

    def emotion_clicked(self, emo):
        try:
            accion = self._emociones.get(emo)
            if accion:
                accion()
            else:
                console.print(f"[bold yellow]Emoción desconocida:[/bold yellow] {emo}")
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al cambiar emoción: {e}")

    def turn(self, duration: float, angular_speed: float):
        """Gira durante `duration` segundos a velocidad angular `angular_speed`."""
        self._set_base_speed(0, angular_speed)
        time.sleep(duration)
        try:
            self.differentialrobot_proxy.stopBase()
        except Exception:
            # Fallback para drivers que no implementan stopBase
            self._set_base_speed(0, 0)

    def _set_base_speed(self, linear, angular):
        self.differentialrobot_proxy.setSpeedBase(linear, angular)

    def move_clicked(self, mov):
        try:
            v = self._movimientos.get(mov)
            if v is None:
                console.print(f"[bold yellow]Movimiento desconocido:[/bold yellow] {mov}")
                return
            self._set_base_speed(*v)
        except Exception as e:
            traceback.print_exc()
            console.print(f"[bold red]Error[/bold red] al mover el robot: {e}")

    def startup_check(self):
        print(f"Testing RoboCompDifferentialRobot.TMechParams from ifaces.RoboCompDifferentialRobot")
        test = ifaces.RoboCompDifferentialRobot.TMechParams()
        print(f"Testing RoboCompLEDArray.Pixel from ifaces.RoboCompLEDArray")
        test = ifaces.RoboCompLEDArray.Pixel()
        QTimer.singleShot(200, QApplication.instance().quit)

    # PROGRAMACIÓN ESPECIAL PARA PROBAR EL EBO AUTÓNOMO ######################################
    def ebo_autonomo_test(self):
        self._asr_lock = getattr(self, "_asr_lock", threading.Lock())

        while getattr(self, "autonomo", True):
            with self._asr_lock:
                # Esta línea es bloqueante y es la razón principal para usar un hilo.
                text = self.eboasr_proxy.listenandtranscript()
                print("EBO HA ESCUCHADO: ", text)

            if not text:
                # nada reconocido, espera breve y repite
                time.sleep(0.1)
                continue

            self._asr_lock.acquire()
            try:
                self.gpt_proxy.continueChat(text)

                ok = self.wait_for_speech_cycle_forgiving(
                    wait_for_start_timeout=5,  # s: máximo tiempo para detectar que ha empezado a hablar
                    wait_for_end_timeout=120.0,  # s: máximo tiempo para esperar a que termine de hablar
                    poll_interval=0.05,  # s: cada cuánto comprobar isBusy() (sondeo)
                    post_silence_grace=0.5,  # s: tiempo extra tras detectar fin para confirmar silencio
                    fallback_wait_after_no_start=0.8
                    # s: si no detectó inicio, espera esto y continúa (modo "forgiving")
                )
                if not ok:
                    time.sleep(1.0)
            finally:
                # 5) Liberar ASR para volver a escuchar
                self._asr_lock.release()

            time.sleep(0.1)

    def wait_for_speech_cycle_forgiving(self,
                                        wait_for_start_timeout: float = 1.5,
                                        wait_for_end_timeout: float = 30.0,
                                        poll_interval: float = 0.05,
                                        post_silence_grace: float = 0.25,
                                        fallback_wait_after_no_start: float = 0.8) -> bool:

        start_deadline = time.time() + wait_for_start_timeout
        saw_start = False

        # 1) Esperar inicio hasta timeout
        while time.time() < start_deadline:
            try:
                if self.speech_proxy.isBusy():
                    saw_start = True
                    break
            except Exception:
                # toleramos fallos temporales de proxy
                pass
            time.sleep(poll_interval)

        if not saw_start:
            # No empezó a hablar: fallback corto y salir (modo forgiving)
            time.sleep(fallback_wait_after_no_start)
            return True

        # 2) Si empezó a hablar, esperar a que termine
        end_deadline = time.time() + wait_for_end_timeout
        while time.time() < end_deadline:
            try:
                if not self.speech_proxy.isBusy():
                    # pequeña confirmación post-silence
                    time.sleep(post_silence_grace)
                    if not self.speech_proxy.isBusy():
                        return True
                    # si volvió a activarse, seguir esperando
            except Exception:
                pass
            time.sleep(poll_interval)

        # timeout esperando a que termine de hablar
        return False

    # PROGRAMACIÓN ESPECIAL PARA PROBAR EL EBO AUTÓNOMO #######################################

    ######################
    # From the RoboCompDifferentialRobot you can call this methods:
    # self.differentialrobot_proxy.correctOdometer(...)
    # self.differentialrobot_proxy.getBasePose(...)
    # self.differentialrobot_proxy.getBaseState(...)
    # self.differentialrobot_proxy.resetOdometer(...)
    # self.differentialrobot_proxy.setOdometer(...)
    # self.differentialrobot_proxy.setOdometerPose(...)
    # self.differentialrobot_proxy.setSpeedBase(...)
    # self.differentialrobot_proxy.stopBase(...)

    ######################
    # From the RoboCompDifferentialRobot you can use this types:
    # RoboCompDifferentialRobot.TMechParams

    ######################
    # From the RoboCompEboASR you can call this methods:
    # self.eboasr_proxy.listenandtranscript(...)

    ######################
    # From the RoboCompEboMoods you can call this methods:
    # self.ebomoods_proxy.expressAnger(...)
    # self.ebomoods_proxy.expressDisgust(...)
    # self.ebomoods_proxy.expressFear(...)
    # self.ebomoods_proxy.expressJoy(...)
    # self.ebomoods_proxy.expressSadness(...)
    # self.ebomoods_proxy.expressSurprise(...)

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
    # From the RoboCompGPT you can call this methods:
    # self.gpt_proxy.continueChat(...)
    # self.gpt_proxy.setGameInfo(...)
    # self.gpt_proxy.startChat(...)

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
    # self.speech_proxy.setPitch(...)
    # self.speech_proxy.setTempo(...)