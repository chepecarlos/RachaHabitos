struct estadoIndicador {
  int Actual;
  int Anterior;
};

struct habitoIndicador {
  String Nombre;
  String Topic;
  int Boton;
  int Led;
  bool EstadoLed;
  estadoIndicador Hoy;
  estadoIndicador Racha;
  estadoIndicador Porcentaje;
  Ticker Cambiador;
};

#define cantidadHabitos 1
habitoIndicador listaHabitos[cantidadHabitos] = {
  { "Ejercicio", "ejercicio", 33, 18, false, { noConfig, noConfig }, { -1, -1 }, { -1, -1 } }
};
