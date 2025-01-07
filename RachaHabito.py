from pytz import utc

from claseHabitos import miHábitos
from MiLibrerias.FuncionesArchivos import ObtenerArchivo

from apscheduler.schedulers.background import BackgroundScheduler

import paho.mqtt.client as mqtt

listaHábitos = list()

client = mqtt.Client()


def procesarHábitos():
    print("Indicando sistema")
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


def mensajeMQTT(client, userdata, msg):
    print(f"{msg.topic} - {msg.payload}")


def iniciarMQTT() -> None:
    client.on_connect = conectadoMQTT
    client.on_message = mensajeMQTT

    dataMQTT = ObtenerArchivo("data/mqtt.md", False)

    client.connect(dataMQTT.get("servidor"), dataMQTT.get("puerto"), 60)
    client.loop_forever()


if __name__ == '__main__':
    print("Iniciando Sistema de Hábitos")

    dataEjercicio = ObtenerArchivo("data/habitoEjercicio.md", False)
    dataNotion = ObtenerArchivo("data/notion.md", False)

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
