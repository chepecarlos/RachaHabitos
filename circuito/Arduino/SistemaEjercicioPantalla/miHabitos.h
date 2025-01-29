struct estadoIndicador {
  int Actual;
  int Anterior;
};

struct habito {
  String Nombre;
  String Topic;
  estadoIndicador Hoy;
  estadoIndicador Racha;
  estadoIndicador Porcentaje;
};

#define cantidadHabitos 6

habito listaHabitos[cantidadHabitos] = {
  { "ejercicio", "ejercicio", { noConfig, noConfig }, { -1, -1 }, { -1, -1 } },
  { "ordenar", "ordenar", { noConfig, noConfig }, { -1, -1 }, { -1, -1 } },
  { "tiktok", "tiktok", { noConfig, noConfig }, { -1, -1 }, { -1, -1 } },
  { "youtube", "youtube", { noConfig, noConfig }, { -1, -1 }, { -1, -1 } },
  { "cepillarme", "cepillarme", { noConfig, noConfig }, { -1, -1 }, { -1, -1 } },
  { "planeacion semanal", "r-semanal", { noConfig, noConfig }, { -1, -1 }, { -1, -1 } }
};