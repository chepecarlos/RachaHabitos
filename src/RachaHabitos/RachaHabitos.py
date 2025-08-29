from pytz import utc
import threading

from RachaHabitos.claseHabitos import miHábitos
from RachaHabitos.miGui import miGui
from RachaHabitos.MiLibrerias.FuncionesArchivos import ObtenerArchivo
from RachaHabitos.MiLibrerias import ConfigurarLogging, ObtenerFolderConfig

from apscheduler.schedulers.background import BackgroundScheduler

# librerías MQTT https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
import paho.mqtt.client as mqtt
import os

listaHábitos: list[miHábitos] = list()
miApp: miGui = None

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# nombrePrograma("RachaHabito")

logger = ConfigurarLogging(__name__)

def procesarHábitos():
    for hábito in listaHábitos:
        hábito.publicarMQTT()
        
    # TODO: reparar actualizar interface
    if miApp is not None:
        miApp.actualizarGui()
    else:
        logger.error("App Grafica no carga")


def conectadoMQTT(client, userdata, flags, reason_code, properties):
    logger.info("Se conecto con mqtt " + str(reason_code))
    client.subscribe("habito/#")
    procesarHábitos()


def mensajeMQTT(client, userdata, mensaje):
    topic = mensaje.topic
    texto = mensaje.payload
    # print(f"{topic} - {texto}")

    for hábito in listaHábitos:
        # TODO:  capturar error si no hay internet
        if hábito.topic in topic and "reportar" in topic:
            logger.info(f"Creando Registro de habito {hábito.nombre}")
            hábito.mantenerRacha()
            hábito.publicarMQTT()


def desconectarMQTT(client, userdata, rc):
    logger.info("Desconectando mqtt " + str(rc))


def errorConectarMQTT(client, userdata):
    logger.info(f"No se puede conectar MQTT - Re-intentando {userdata}")


def iniciarMQTT() -> None:
    """Iniciando sistema de MQTT para enviar y recibir mensajes de hábitos desde los esp
    """
    client.on_connect = conectadoMQTT
    client.on_message = mensajeMQTT
    client.on_disconnect = desconectarMQTT
    client.on_connect_fail = errorConectarMQTT

    dataMQTT = ObtenerArchivo("data/mqtt.md")

    puertoMQTT = dataMQTT.get("puerto")
    if puertoMQTT is None:
        puertoMQTT = 1883
    servidorMQTT = dataMQTT.get("servidor")
    if servidorMQTT is None:
        servidorMQTT = "localhost"

    client.reconnect_delay_set(1, 20)
    client.enable_logger()

    client.connect_async(servidorMQTT, puertoMQTT, 60)

    for hábito in listaHábitos:
        hábito.clienteMQTT = client

    Hilo = threading.Thread(target=HiloServidor)
    Hilo.start()


def HiloServidor():
    logger.info(f"Iniciando MQTT nuevo hilo")
    client.loop_forever(retry_first_connection=True)

def main():
    global miApp
    logger.info("Iniciando Sistema de Hábitos")

    dataNotion = ObtenerArchivo("data/notion.md")
    dataHábitos = ObtenerArchivo("data/listaHabitos.md")
    
    if dataNotion is None or dataHábitos is None:
        logger.error("No se encuentran los archivos de configuración")
        return
    
    print(dataHábitos)

    for rutaHábitos in dataHábitos:
        print(rutaHábitos)
        dataHabito = ObtenerArchivo(rutaHábitos)
        habitoActual = miHábitos(dataHabito, dataNotion)
        listaHábitos.append(habitoActual)

    # TODO error cuando data es None
    repetición = dataNotion.get("repetición", 60)
    logger.info(f"Repetición: {repetición} Segundos")

    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(procesarHábitos, "interval", seconds=repetición)
    scheduler.start()

    try:
        while True:
            iniciarMQTT()
            miApp = miGui()
            miApp.listaHábitos = listaHábitos
            miApp.iniciarGui()

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
    pass

if __name__ == "__main__":
    main()