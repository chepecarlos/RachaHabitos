from nicegui import ui


class miGui():

    listaHábitos = list()

    def __init__(self):
        print("Creando app GUI")

    def iniciarGui(self):

        for habito in self.listaHábitos:
            habito.linea = ui.row()
            with habito.linea:
                ui.label(f"Habito {habito.nombre}:")
                ui.label(f"0")

        ui.run(title="RachaHabito", port=8282, reload=False, show=False,
               dark=True, uvicorn_logging_level="warning", favicon="📃")

    def actualizarGui(self):
        for habito in self.listaHábitos:
            habito.linea.clear()
            with habito.linea:
                ui.label(f"{habito.nombre}:")
                ui.label(f"Hoy: {habito.hoy}")
                ui.label(f"Racha: {habito.racha}")
        ui.update()
