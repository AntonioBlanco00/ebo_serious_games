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

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

# from pydsr import *
import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime
import os
import sys
import threading

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        load_dotenv()

        self.client = openai.OpenAI()
        self.conversacion_en_curso = False
        self.asisstantName  = ""
        self.userInfo = ""

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        # print("MIAU")
        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)

    def get_assistant_id_by_name(self, name, filename='src/assistants.txt'):
        # Reemplazar los espacios en el nombre por barras bajas
        name_with_underscores = name.replace(" ", "_")

        # Leer el archivo y buscar el asistente por nombre
        with open(filename, 'r') as file:
            for line in file:
                stored_name, stored_id = line.strip().split(';')
                if stored_name == name_with_underscores:
                    return stored_id
        return None  # Si no se encuentra el asistente

    def wait_for_run_completion(self, client, thread_id, run_id, sleep_interval=1):
        """
        Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
        :param thread_id: The ID of the thread.
        :param run_id: The ID of the run.
        :param sleep_interval: Time in seconds to wait between checks.
        """
        while True:
            try:
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                if run.completed_at:
                    elapsed_time = run.completed_at - run.created_at
                    formatted_elapsed_time = time.strftime(
                        "%H:%M:%S", time.gmtime(elapsed_time)
                    )
                    print(f"Run completed in {formatted_elapsed_time}")
                    logging.info(f"Run completed in {formatted_elapsed_time}")
                    # Get messages here once Run is completed!
                    messages = client.beta.threads.messages.list(thread_id=thread_id)
                    last_message = messages.data[0]
                    response = last_message.content[0].text.value
                    response_final, last_word = self.split_last_word(response)
                    print(f"Assistant Response: {response_final}")
                    print(f"Last word: {last_word}")
                    self.set_emotion(last_word)
                    self.speech_proxy.say(response_final, False)
                    break
            except Exception as e:
                logging.error(f"An error occurred while retrieving the run: {e}")
                break
            logging.info("Waiting for run to complete...")
            time.sleep(sleep_interval)

    def split_last_word(self, text):
        text = text.strip().rstrip('.')
        words = text.split()
        if words:
            last_word = words[-1]  # La última palabra
            remaining_text = ' '.join(words[:-1])  # El texto sin la última palabra
            return remaining_text, last_word
        else:
            return "", ""  # Si el texto está vacío, retorna dos strings vacíos

    def set_emotion(self, emotion):
        print("Activando emoción")
        emo = emotion.lower()
        if emo == "asco":
            self.emotionalmotor_proxy.expressDisgust()
        elif emo == "contento":
            self.emotionalmotor_proxy.expressJoy()
        elif emo == "triste":
            self.emotionalmotor_proxy.expressSadness()
        elif emo == "enfado":
            self.emotionalmotor_proxy.expressAnger()
        elif emo == "miedo":
            self.emotionalmotor_proxy.expressFear()
        elif emo == "sorpresa":
            self.emotionalmotor_proxy.expressSurprise()
        else:
            pass

    def guardar_chat(self, client, thread_id, folder="conversaciones", filename_prefix="chat"):
        """
        Guarda todos los mensajes de un hilo en un archivo de texto.

        Args:
            client: Cliente que interactúa con la API para obtener los mensajes.
            thread_id: ID del hilo del que se extraen los mensajes.
            folder: Carpeta donde se guardará el archivo. Por defecto, "conversaciones".
            filename_prefix: Prefijo para el nombre del archivo. Por defecto, "chat".
        """
        try:
            # Obtener los mensajes del hilo
            messages = client.beta.threads.messages.list(thread_id=thread_id)

            # Invertir el orden de los mensajes para que estén en orden cronológico
            chronological_messages = list(reversed(messages.data))

            # Crear una lista con los textos de todos los mensajes
            all_messages = [
                f"{message.role.capitalize()}: {message.content[0].text.value}"
                for message in chronological_messages
            ]

            # Unir los mensajes en un solo bloque de texto
            conversation = "\n".join(all_messages)

            # Crear la carpeta si no existe
            os.makedirs(folder, exist_ok=True)

            # Generar un nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.txt"
            filepath = os.path.join(folder, filename)

            # Guardar la conversación en el archivo
            with open(filepath, "w", encoding="utf-8") as file:
                file.write("--- Conversación completa ---\n")
                file.write(conversation)
                file.write("\n--- Fin de la conversación ---\n")

            print(f"Conversación guardada en: {filepath}")

        except Exception as e:
            print(f"Error al guardar el chat: {e}")

    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of continueChat method from GPT interface
    #
    def GPT_continueChat(self, message):
        if message.strip().lower() == "03827857295769204":
            print("Almacenando chat...")
            self.guardar_chat(self.client, self.thread_id)
            print("Saliendo del programa...")
            self.exit_program()
        else:
            # self.set_all_LEDS_colors(0,0,0,0)
            # self.start_rotating_effect()
            run_id = self.send_message_to_assistant(self.client, self.thread_id, self.assistant_id, message)
            response = self.get_assistant_response(self.client, self.thread_id, run_id)
            # print(f"Respuesta del asistente: {response}")
            # self.actualizar_to_say(response)
            response_final, last_word = self.split_last_word(response)
            print(f"Assistant Response: {response_final}")
            print(f"Last word: {last_word}")
            self.speech_proxy.say(response_final, False)
            # self.stop_rotating_effect()
            self.set_emotion(last_word)
        pass


    #
    # IMPLEMENTATION of setGameInfo method from GPT interface
    #
    def GPT_setGameInfo(self, asisstantName, userInfo):
        self.asisstantName = asisstantName
        self.userInfo = userInfo
        pass


    #
    # IMPLEMENTATION of startChat method from GPT interface
    #
    def GPT_startChat(self):
        self.assistant_id = self.get_assistant_id_by_name(self.asisstantName)
        if self.assistant_id:
            print(f"El ID del asistente '{self.asisstantName}' es: {self.assistant_id}")
        else:
            print(f"No se encontró un asistente con el nombre '{self.asisstantName}'")
            sys.exit()  # Termina la ejecución del programa

        ### Creación del hilo de conversación
        self.thread = self.client.beta.threads.create()
        self.thread_id = self.thread.id
        print(f"Thread creado con ID: {self.thread_id}")

        # Primer mensaje, el cual envia el json y la respuesta es el inicio del juego
        self.message = self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=self.userInfo,
        )

        ### Ejecución del asistente ###
        self.run = self.client.beta.threads.runs.create(
            assistant_id=self.assistant_id,
            thread_id=self.thread_id
        )
        self.run_id = self.run.id

        # instructions="Para iniciar la conversación solo saluda al usuario y presentate como EBO, el robot mas simpatico del mundo creado en Robolab."

        ### Ejecución ###
        self.wait_for_run_completion(client=self.client, thread_id=self.thread_id, run_id=self.run_id)

        ### Ver los logs ###
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread_id,
            run_id=self.run_id
        )

        pass

    def send_message_to_assistant(self, client, thread_id, assistant_id, user_message):
        # Enviar el mensaje del usuario al asistente
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Ejecutar el asistente con instrucciones (si se proporcionan)
        # run = client.beta.threads.runs.create(
        #     thread_id=thread_id,
        #     assistant_id=assistant_id,
        #     instructions="Continua la conversación como tú sabes"
        # )
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id      ###### AQUI SE PUEDEN AÑADIR MAS INSTRUCTIONS
        )
        run_id = run.id
        print(f"Mensaje enviado. Run ID: {run_id}")
        return run_id


    def exit_program(self):
        print("-------------------- El programa ha terminado --------------------")
        self.delete_thread(thread_id=self.thread_id)
        print("-------------------- Hilo borrado --------------------")
        self.conversacion_en_curso = False

    def delete_thread(self, thread_id):
        self.client.beta.threads.delete(thread_id)
        print(f"El hilo con ID: {thread_id} ha sido eliminado.")

    def get_assistant_response(self, client, thread_id, run_id):
        # Esperar hasta que el asistente termine de procesar la respuesta
        print("Esperando la respuesta del asistente...")
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run.status == "completed":
                break
            time.sleep(1)

        # Recuperar los mensajes del asistente
        messages = client.beta.threads.messages.list(thread_id=thread_id)

        # Filtrar el mensaje del asistente
        assistant_messages = [
            message
            for message in messages.data
            if message.role == "assistant" and message.run_id == run_id
        ]

        if assistant_messages:
            # Extraer y devolver la respuesta
            assistant_response = assistant_messages[0].content[0].text.value
            return assistant_response
        else:
            return "No se recibió respuesta del asistente."
    # ===================================================================
    # ===================================================================


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

