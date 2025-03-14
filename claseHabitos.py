import requests
import json
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt


class miHábitos():
    listaHábitos: list = list()
    clienteMQTT = None
    hoy: bool = False
    "Se a realizado el hábito hoy"
    racha: int = -1
    "Cuantos días seguidos se a realizado el hábito"
    porcentaje: int = -1
    repeticiones: int = -1
    repetición: int = 1
    "cuantas veces se debe repetir el hábito"

    def __init__(self, data: dict, notion: dict) -> None:
        self.nombre: str = data.get("nombre")
        self.tipo: str = data.get("tipo")
        self.topic: str = data.get("topic")
        self.id_proyecto: str = data.get("id_proyecto")
        self.id_area: str = data.get("id_area")
        self.repetición: int = data.get("repeticion", 1)
        self.canal: str = data.get("canal")
        self.token: str = notion.get("token")
        self.id_database_tarea: str = notion.get("database_tarea")
        self.id_database_proyecto: str = notion.get("database_proyecto")
        self.listaHábitos: list = list()
        self.clienteMQTT = None
        print(f"Creado Hábito {self.nombre} - {self.urlNotion()}")
        print(f"Repetición: {self.repetición}")
        print(f"Tipo: {self.tipo}")
        print(f"Topic: habito/{self.topic}")
        print(f"-"*20)
        

    def urlNotion(self) -> str:
        if self.id_proyecto is not None:
            return f"https://www.notion.so/{self.id_proyecto.replace('-','')}"
        elif self.id_area is not None:
            return f"https://www.notion.so/{self.id_area.replace('-','')}"

    def descargarHábitos(self) -> list:
        self.listaHábitos = self.obtenerHábitos()

    def habitoHoy(self) -> bool:
        fechaHoy = datetime.now()
        textoFechaHoy = fechaHoy.strftime("%Y-%m-%d")

        if self.tipo == "diario":
            for habito in self.listaHábitos:
                if habito.get("fecha") == textoFechaHoy:
                    if habito.get("cantidad") >= self.repetición:
                        return True
                    else:
                        return False
        elif self.tipo == "semanal":
            listaSemana = self.obtenerHábitosSemana()
            textoSemana = f"{fechaHoy.isocalendar().week}-{fechaHoy.year}"
            for semana in listaSemana:
                if semana.get("fecha") == textoSemana:
                    if semana.get("cantidad") >= self.repetición:
                        return True
                    else:
                        return False
        return False

    def rachaHabito(self) -> int:
        # TODO: crear código para hábitos que ho sean diarios
        fechaHoy = datetime.now()
        fechaActual = fechaHoy
        racha = 0

        if self.tipo == "diario":
            if not self.habitoHoy():
                fechaActual = fechaHoy - timedelta(days=1)

            for habito in self.listaHábitos:
                textoFechaActual = fechaActual.strftime("%Y-%m-%d")
                if habito.get("fecha") == textoFechaActual:
                    if habito.get("cantidad") >= self.repetición:
                        racha += 1
                        fechaActual = fechaActual - timedelta(days=1)
                    else:
                        return racha
        elif self.tipo == "semanal":

            listaSemana = self.obtenerHábitosSemana()
            # print(json.dumps(listaSemana, sort_keys=False, indent=4))

            if not self.habitoHoy():
                fechaActual = fechaHoy - timedelta(days=7)

            for habito in listaSemana:
                textoSemana = f"{fechaActual.isocalendar().week}-{fechaActual.year}"
                if habito.get("fecha") == textoSemana:
                    if habito.get("cantidad") >= self.repetición:
                        # TODO: contar repeticion en repeticion de la semana
                        racha += 1
                        fechaActual = fechaActual - timedelta(days=7)
                    else:
                        return racha

        else:

            semanaActual = fechaActual.isocalendar().week
            diaSemana = fechaActual.isocalendar().weekday
            print(f"Semana: {semanaActual} - Dia: {diaSemana}")

        return racha

    def obtenerCabeza(self) -> str:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16"
        }

    def obtenerHábitos(self) -> list:

        listaHábitos = list()

        if self.id_proyecto is not None:

            urlPregunta = f"https://api.notion.com/v1/databases/{self.id_database_tarea}/query"

            cabeza = self.obtenerCabeza()

            búsqueda = {
                "filter": {
                    "and": [
                        {
                            "property": "Proyecto",
                            "relation": {
                                "contains": self.id_proyecto,
                            }
                        },
                        {
                            "property": "Terminado",
                            "checkbox": {
                                "equals": True
                            }
                        },
                    ]
                },
                "sorts": [
                    {
                        "property": "Hacer para",
                        "direction": "descending"
                    }
                ]
            }

            respuesta = requests.post(
                urlPregunta, headers=cabeza, data=json.dumps(búsqueda))

            # print(json.dumps(respuesta.json(), sort_keys=False, indent=4))

            tareas = respuesta.json()["results"]

            for tarea in tareas:
                propiedad = tarea["properties"]
                titulo = propiedad["Nombre"]["title"]
                # print("titulo")
                if len(titulo) > 0:
                    # TODO: agregar error por si no encuentra fecha
                    hecho = propiedad["Hacer para"]["date"]["start"]
                    fechaTarea = datetime.fromisoformat(hecho)
                    textoFechaTarea = fechaTarea.strftime("%Y-%m-%d")
                    titulo = titulo[0]['plain_text']
                    encontrado = False
                    for habito in listaHábitos:
                        if habito.get("fecha") == textoFechaTarea:
                            habito["cantidad"] += 1
                            encontrado = True
                    if not encontrado:
                        listaHábitos.append({
                            "titulo": titulo,
                            "fecha": textoFechaTarea,
                            "cantidad": 1
                        })

        elif self.id_area is not None:

            urlPregunta = f"https://api.notion.com/v1/databases/{self.id_database_proyecto}/query"

            cabeza = self.obtenerCabeza()

            búsqueda = {
                "filter": {
                    "and": [
                        {
                            "property": "Área",
                            "relation": {
                                "contains": self.id_area,
                            }
                        },
                        {
                            "property": "Terminado",
                            "checkbox": {
                                "equals": True
                            }
                        },
                        {
                            "property": "Canal",
                            "select": {
                                "equals": self.canal
                            }
                        }
                    ]

                },
                "sorts": [
                    {
                        "property": "Hacer para",
                        "direction": "descending"
                    }
                ]
            }

            respuesta = requests.post(
                urlPregunta, headers=cabeza, data=json.dumps(búsqueda))

            # print(json.dumps(respuesta.json(), sort_keys=False, indent=4))

            tareas = respuesta.json()["results"]

            for tarea in tareas:
                propiedad = tarea["properties"]
                titulo = propiedad["Nombre"]["title"]
                if len(titulo) > 0:
                    hecho = propiedad["Hacer para"]["date"]
                    if hecho is None:
                        continue
                    hecho = hecho["start"]
                    fechaTarea = datetime.fromisoformat(hecho)
                    textoFechaTarea = fechaTarea.strftime("%Y-%m-%d")
                    titulo = titulo[0]['plain_text']
                    encontrado = False
                    for habito in listaHábitos:
                        if habito.get("fecha") == textoFechaTarea:
                            habito["cantidad"] += 1
                            encontrado = True
                    if not encontrado:
                        listaHábitos.append({
                            "titulo": titulo,
                            "fecha": textoFechaTarea,
                            "cantidad": 1
                        })

        def ordenarFecha(dict):
            return dict['fecha']

        listaHábitos.sort(reverse=True, key=ordenarFecha)

        return listaHábitos

    def obtenerHábitosSemana(self) -> list:

        listaSemana = list()
        for habito in self.listaHábitos:
            fechaDia = habito.get("fecha")
            cantidadDiaria = habito.get("cantidad")
            fechaSemana = datetime.strptime(fechaDia, '%Y-%m-%d')
            textoSemana = f"{fechaSemana.isocalendar().week}-{fechaSemana.year}"

            encontrado = False
            for semana in listaSemana:
                if semana.get("fecha") == textoSemana:
                    semana["cantidad"] += cantidadDiaria
                    encontrado = True

            if not encontrado:
                listaSemana.append({"fecha": textoSemana, "cantidad": cantidadDiaria})

        return listaSemana

    def mantenerRacha(self) -> None:
        fechaHoy = datetime.now().astimezone()
        textoFechaHoy = fechaHoy.replace(microsecond=0).isoformat()

        urlPregunta = f"https://api.notion.com/v1/pages"

        habitoHoy = self.habitoHoy()

        if habitoHoy:
            titulo = f"{self.rachaHabito() + 1} en rachas"
        else:
            porcentaje = self.obtenerPorcentaje(incrementor=True)
            if porcentaje >= 100:
                titulo = f"{self.rachaHabito() + 1} en rachas"
            else:
                titulo = f"{self.rachaHabito()} en rachas - {porcentaje}%"

        cabeza = self.obtenerCabeza()

        pagina = {
            "parent": {
                "database_id": self.id_database_tarea
            },
            "properties": {
                "Nombre": {
                    "title": [
                        {
                            "text": {
                                "content": titulo
                            }
                        }
                    ]
                },
                "Terminado": {
                    "checkbox": True
                },
                "Proyecto": {
                    "relation": [
                        {
                            "id": self.id_proyecto
                        }
                    ]
                },
                "Asignado": {
                    "select": {
                        "name": "ChepeCarlos"
                    }
                },
                "Tipo": {
                    "select": {
                        "name": "Periodicas"
                    }
                },
                "Hacer para": {
                    "date": {
                        "start": textoFechaHoy
                    }
                }
            }
        }

        respuesta = requests.post(
            urlPregunta, headers=cabeza, data=json.dumps(pagina))
        url = respuesta.json().get("url")
        print(f"Consulta hecha {url}")

        # print(json.dumps(respuesta.json(), sort_keys=False, indent=4))

    def obtenerPorcentaje(self, incrementor: bool = False) -> int:

        fechaHoy = datetime.now()
        self.porcentaje = 0
        repeticiones = 0

        if self.tipo == "diario":
            for habito in self.listaHábitos:
                textoFechaActual = fechaHoy.strftime("%Y-%m-%d")
                if habito.get("fecha") == textoFechaActual:
                    repeticiones = habito.get("cantidad")
        elif self.tipo == "semanal":
            listaSemana = self.obtenerHábitosSemana()
            for habito in listaSemana:
                textoSemana = f"{fechaHoy.isocalendar().week}-{fechaHoy.year}"
                if habito.get("fecha") == textoSemana:
                    repeticiones = habito.get("cantidad")

        if incrementor:
            repeticiones += 1

        self.repeticiones = repeticiones
        self.porcentaje = (repeticiones/self.repetición) * 100
        return int(self.porcentaje)

    def publicarMQTT(self) -> None:
        if self.clienteMQTT is None:
            print("Error Cliente MQTT no configurado")

        if not self.clienteMQTT.is_connected():
            print("Error no conectado a MQTT")

        self.descargarHábitos()

        self.hoy = self.habitoHoy()
        self.racha = self.rachaHabito()
        porcentaje = 0

        self.clienteMQTT.publish(f"habito/{self.topic}/hoy", f"{self.hoy}")
        self.clienteMQTT.publish(f"habito/{self.topic}/racha", f"{self.racha}")

        if self.repetición > 1 and not self.hoy:
            porcentaje = self.obtenerPorcentaje()
            self.clienteMQTT.publish(
                f"habito/{self.topic}/porcentaje", f"{porcentaje}")
            print(
                f"{self.nombre}: Hoy No - {porcentaje}% y {self.racha} Racha {self.tipo}")
        else:
            print(
                f"{self.nombre}: Hoy {'Si' if self.hoy else 'No'} y {self.racha} Racha {self.tipo}")
