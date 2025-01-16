from pytz import utc

from claseHabitos import miHábitos
from MiLibrerias.FuncionesArchivos import ObtenerArchivo

from apscheduler.schedulers.background import BackgroundScheduler

import paho.mqtt.client as mqtt
import os

listaHábitos = list()

client = mqtt.Client()


def procesarHábitos():
    for hábitos in listaHábitos:
        hábitos.descargarHábitos()
        titulo = hábitos.nombre
        hoy = hábitos.habitoHoy()
        racha = hábitos.rachaHabito()
        tipo = hábitos.tipo
        repeticiones = hábitos.repeticion
        porcentaje = 0

        if repeticiones > 1 and not hoy:
            porcentaje = hábitos.porcentaje()
            print(f"{titulo}: Hoy No - {porcentaje}% y {racha} Racha {tipo}")
        elif not hoy:
            print(f"{titulo}: Hoy No y {racha} Racha {tipo}")
        else:
            print(f"{titulo}: Hoy SI y {racha} Racha {tipo}")

        if client.is_connected():
            client.publish(f"habito/{hábitos.topic}/hoy", f"{hoy}")
            client.publish(f"habito/{hábitos.topic}/racha", f"{racha}")
            if repeticiones > 1 and not hoy:
                client.publish(
                    f"habito/{hábitos.topic}/porcentaje", f"{porcentaje}")


def conectadoMQTT(client, userdata, flags, rc):
    print("Se conecto con mqtt " + str(rc))
    client.subscribe("habito/#")
    procesarHábitos()


def mensajeMQTT(client, userdata, mensaje):
    topic = mensaje.topic
    texto = mensaje.payload
    # print(f"{topic} - {texto}")

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

    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(procesarHábitos, 'interval', seconds=25)
    scheduler.start()

    try:
        while True:
            iniciarMQTT()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
