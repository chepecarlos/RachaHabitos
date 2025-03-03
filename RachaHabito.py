from pytz import utc
import threading

from claseHabitos import miHábitos
from miGui import miGui
from MiLibrerias.FuncionesArchivos import ObtenerArchivo

from apscheduler.schedulers.background import BackgroundScheduler

import paho.mqtt.client as mqtt
import os

listaHábitos = list()

client = mqtt.Client()
miApp = None


def procesarHábitos():
    for hábito in listaHábitos:
        hábito.publicarMQTT()
    miApp.actualizarGui()


def conectadoMQTT(client, userdata, flags, rc):
    print("Se conecto con mqtt " + str(rc))
    client.subscribe("habito/#")
    procesarHábitos()


def mensajeMQTT(client, userdata, mensaje):
    topic = mensaje.topic
    texto = mensaje.payload
    # print(f"{topic} - {texto}")

    for hábito in listaHábitos:
        # TODO:  capturar error si no hay internet
        if hábito.topic in topic and "reportar" in topic:
            print(f"creando habito {texto}")
            hábito.mantenerRacha()
            hábito.publicarMQTT()


def iniciarMQTT() -> None:
    client.on_connect = conectadoMQTT
    client.on_message = mensajeMQTT

    archivoMQTT = f"{os.path.dirname(os.path.realpath(__file__))}/data/mqtt.md"

    dataMQTT = ObtenerArchivo(archivoMQTT, False)

    client.connect(dataMQTT.get("servidor"), dataMQTT.get("puerto"), 60)
    for hábito in listaHábitos:
        hábito.clienteMQTT = client

    Hilo = threading.Thread(target=HiloServidor)
    Hilo.start()


def HiloServidor():
    print(f"Iniciando MQTT nuevo hilo")
    client.loop_forever()


def rutaAbsoluta(ruta: str):
    return f"{os.path.dirname(os.path.realpath(__file__))}/{ruta}"


if __name__ == '__main__':
    print("Iniciando Sistema de Hábitos")

    archivoNotion = rutaAbsoluta("data/notion.md")
    archivoHábitos = rutaAbsoluta("data/listaHabitos.md")

    dataNotion = ObtenerArchivo(archivoNotion, False)
    dataHábitos = ObtenerArchivo(archivoHábitos, False)

    for hábitos in dataHábitos:
        archivoHabito = rutaAbsoluta(hábitos)
        dataHabito = ObtenerArchivo(archivoHabito, False)
        habitoActual = miHábitos(dataHabito, dataNotion)
        rutaNotion = habitoActual.urlNotion()
        print(f"Cargando: {habitoActual.nombre} URL: {rutaNotion}")
        listaHábitos.append(habitoActual)

    # TODO error cuando data es None
    repetición = dataNotion.get("repetición", 60)
    print(f"Repetición: {repetición} Segundos")

    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(procesarHábitos, 'interval', seconds=repetición)
    scheduler.start()

    try:
        while True:
            iniciarMQTT()
            miApp = miGui()
            miApp.listaHábitos = listaHábitos
            miApp.iniciarGui()

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
