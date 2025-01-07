import requests
import json
from datetime import datetime, timedelta


class miHábitos():

    def __init__(self, data: dict, notion: dict) -> None:
        self.nombre = data.get("nombre")
        self.tipo = data.get("tipo")
        self.topic = data.get("topic")
        self.id_proyecto = data.get("id_proyecto")
        self.token = notion.get("token")
        self.id_database = notion.get("database")

    def habitoHoy(self) -> bool:
        listaHábitos = self.obtenerHábitos()
        fechaHoy = datetime.now()
        textoFechaHoy = fechaHoy.strftime("%Y-%m-%d")
        for habito in listaHábitos:
            if habito["fecha"] == textoFechaHoy:
                return True
        return False

    def rachaHabito(self) -> int:
        listaHábitos = self.obtenerHábitos()
        fechaHoy = datetime.now()
        racha = 0
        fechaActual = fechaHoy

        if not self.habitoHoy():
            fechaActual = fechaHoy - timedelta(days=1)

        for habito in listaHábitos:
            textoFechaActual = fechaActual.strftime("%Y-%m-%d")
            if habito["fecha"] == textoFechaActual:
                racha = racha + 1
            else:
                return racha
            fechaActual = fechaActual - timedelta(days=1)

        return racha

    def obtenerHábitos(self) -> list:
        listaHábitos = list()

        urlPregunta = f"https://api.notion.com/v1/databases/{self.id_database}/query"

        cabeza = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16"
        }

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

        tareas = respuesta.json()["results"]

        for tarea in tareas:
            propiedad = tarea["properties"]
            titulo = propiedad["Nombre"]["title"]
            if len(titulo) > 0:
                hecho = propiedad["Hacer para"]["date"]["start"]
                titulo = titulo[0]['plain_text']
                listaHábitos.append({"titulo": titulo, "fecha": hecho})

        return listaHábitos
