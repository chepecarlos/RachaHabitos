from pytz import utc

from claseHabitos import miHábitos
from MiLibrerias.FuncionesArchivos import ObtenerArchivo

from apscheduler.schedulers.background import BackgroundScheduler

import paho.mqtt.client as mqtt
import os

listaHábitos = list()

client = mqtt.Client()


def procesarHábitos():
    print("Consultando Notion")
    for hábitos in listaHábitos:
        hoy = hábitos.habitoHoy()
        racha = hábitos.rachaHabito()
        print(f"Hoy {hoy} y {racha} días")

        if client.is_connected():
            client.publish(f"habito/{hábitos.topic}/hoy", f"{hoy}")
            client.publish(f"habito/{hábitos.topic}/racha", f"{racha}")


def conectadoMQTT(client, userdata, flags, rc):
    print("Se conecto con mqtt " + str(rc))
    client.subscribe("habito/#")


def mensajeMQTT(client, userdata, mensaje):
    topic = mensaje.topic
    texto = mensaje.payload
    print(f"{topic} - {texto}")

    for hábito in listaHábitos:
        if hábito.topic in topic and "reportar" in topic:
            print(f"creando habito {texto}")
            hábito.mantenerRacha()


def iniciarMQTT() -> None:
    client.on_connect = conectadoMQTT
    client.on_message = mensajeMQTT
    
    archivoMQTT = f"{os.path.dirname(os.path.realpath(__file__))}/data/mqtt.md"

    dataMQTT = ObtenerArchivo(archivoMQTT, False)

    client.connect(dataMQTT.get("servidor"), dataMQTT.get("puerto"), 60)
    client.loop_forever()


if __name__ == '__main__':
    print("Iniciando Sistema de Hábitos")

    archivoEjercicio = f"{os.path.dirname(os.path.realpath(__file__))}/data/habitoEjercicio.md"
    archivoNotion =  f"{os.path.dirname(os.path.realpath(__file__))}/data/notion.md"

    dataEjercicio = ObtenerArchivo(archivoEjercicio, False)
    dataNotion = ObtenerArchivo(archivoNotion, False)

    # TODO error cuando data es None

    habitoActual = miHábitos(dataEjercicio, dataNotion)

    listaHábitos.append(habitoActual)

    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(procesarHábitos, 'interval', seconds=15)
    scheduler.start()

    try:
        while True:
            iniciarMQTT()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
