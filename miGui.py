from nicegui import ui
from MiLibrerias import ConfigurarLogging

logger = ConfigurarLogging(__name__)


class miGui():

    listaHábitos = list()

    def __init__(self):
        logger.info("Creando app GUI")

    def iniciarGui(self):

        with ui.column().classes('fixed-center'):
            with ui.row().classes("flex-wrap justify-center"):
                for habito in self.listaHábitos:
                    habito.tarjeta = ui.card().classes("m-2")
                    with habito.tarjeta:
                        ui.label(f"Habito {habito.nombre}: Cargando").style(
                            "font-weight: bold; text-align: center; width: 100%; display: block;")

        ui.run(title="RachaHabito", port=8282, reload=False, show=False,
               dark=True, uvicorn_logging_level="warning", favicon="📃")

    def actualizarGui(self):
        for habito in self.listaHábitos:
            racha = habito.racha
            if habito.tipo == "diario":
                tipo = "Dias"
            else:
                tipo = "Semanas"
            habito.tarjeta.clear()
            with habito.tarjeta:
                ui.label(f"{habito.nombre}").style(
                    "font-weight: bold; text-align: center; width: 100%; display: block;")
                with ui.row().style("text-align: center; width: 100%; display: block;"):
                    if habito.hoy:
                        ui.label(f"🔥 Racha: {racha} {tipo}").style(
                            "font-weight: bold; color: green;")
                    else:
                        ui.label(f"🔴 No Racha: {racha} {tipo}").style(
                            "font-weight: bold; color: red;")
                        if habito.repetición > 1:
                            ui.label(f"{habito.repeticiones} de {habito.repetición}").style(
                                "font-weight: bold; color: orange;")

        ui.update()
