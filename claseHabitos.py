import requests
import json
from datetime import datetime, timedelta


class miHábitos():
    listaHábitos: list = list()

    def __init__(self, data: dict, notion: dict) -> None:
        self.nombre = data.get("nombre")
        self.tipo = data.get("tipo")
        self.topic = data.get("topic")
        self.id_proyecto = data.get("id_proyecto")
        self.repeticion = data.get("repeticion", 1)
        self.token = notion.get("token")
        self.id_database = notion.get("database")
        self.listaHábitos = list()

    def descargarHábitos(self):
        self.listaHábitos = self.obtenerHábitos()

    def habitoHoy(self) -> bool:
        fechaHoy = datetime.now()
        textoFechaHoy = fechaHoy.strftime("%Y-%m-%d")

        if self.tipo == "diario":
            for habito in self.listaHábitos:
                if habito.get("fecha") == textoFechaHoy:
                    if habito.get("cantidad") >= self.repeticion:
                        return True
                    else:
                        return False
        elif self.tipo == "semanal":
            listaSemana = self.obtenerHábitosSemana()
            textoSemana = f"{fechaHoy.isocalendar().week}-{fechaHoy.year}"
            for semana in listaSemana:
                if semana.get("fecha") == textoSemana:
                    if semana.get("cantidad") >= self.repeticion:
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
                    if habito.get("cantidad") >= self.repeticion:
                        racha += 1
                    else:
                        return racha
                else:
                    return racha
                fechaActual = fechaActual - timedelta(days=1)
        if self.tipo == "semanal":

            listaSemana = self.obtenerHábitosSemana()
            if not self.habitoHoy():
                fechaActual = fechaHoy - timedelta(days=7)

            for habito in listaSemana:
                textoSemana = f"{fechaActual.isocalendar().week}-{fechaActual.year}"
                if habito.get("fecha") == textoSemana:
                    if habito.get("cantidad") >= self.repeticion:
                        # TODO: contar repeticion en repeticion de la semana
                        racha += 1
                    else:
                        return racha
                else:
                    return racha

                fechaActual = fechaActual - timedelta(days=1)
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

        urlPregunta = f"https://api.notion.com/v1/databases/{self.id_database}/query"

        cabeza = self.obtenerCabeza()

        búsqueda = {
            "filter": {
                "property": "Proyecto",
                "relation": {
                    "contains": self.id_proyecto,
                }
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

        return listaHábitos

    def obtenerHábitosSemana(self) -> list:

        listaSemana = list()
        for habito in self.listaHábitos:
            fechaDia = habito.get("fecha")
            fechaSemana = datetime.strptime(fechaDia, '%Y-%m-%d')
            textoSemana = f"{fechaSemana.isocalendar().week}-{fechaSemana.year}"

            encontrado = False
            for semana in listaSemana:
                if semana.get("fecha") == textoSemana:
                    semana["cantidad"] += 1
                    encontrado = True

            if not encontrado:
                listaSemana.append({"fecha": textoSemana, "cantidad": 1})

        return listaSemana

    def mantenerRacha(self):
        fechaHoy = datetime.now().astimezone()
        textoFechaHoy = fechaHoy.replace(microsecond=0).isoformat()

        urlPregunta = f"https://api.notion.com/v1/pages"

        habitoHoy = self.habitoHoy()

        if habitoHoy:
            titulo = f"{self.rachaHabito() + 1} en rachas"
        else:
            porcentaje = self.porcentaje(incrementor=True)
            if porcentaje >= 100:
                titulo = f"{self.rachaHabito() + 1} en rachas"
            else:
                titulo = f"{self.rachaHabito()} en rachas - {porcentaje}%"

        cabeza = self.obtenerCabeza()

        pagina = {
            "parent": {
                "database_id": self.id_database
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

    def porcentaje(self, incrementor: bool = False) -> int:

        fechaHoy = datetime.now()
        porcentaje = 0
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
        porcentaje = (repeticiones/self.repeticion) * 100
        return int(porcentaje)
