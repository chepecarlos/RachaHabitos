struct habito {
  String Nombre;
  String Topic;
  int Racha;
  int Hoy;
  int Porcentaje;
  int RachaAnterior;
  int HoyAnterior;
  int PorcentajeAnterior;
};

#define cantidadHabitos 6

habito listaHabitos[cantidadHabitos] = {
  { "ejercicio", "ejercicio", -1, noConfig, -1, -1, noConfig, -1 },
  { "ordenar", "ordenar", -1, noConfig, -1, -1, noConfig, -1 },
  { "tiktok", "tiktok", -1, noConfig, -1, -1, noConfig, -1 },
  { "youtube", "youtube", -1, noConfig, -1, -1, noConfig, -1 },
  { "cepillarme", "cepillarme", -1, noConfig, -1, -1, noConfig, -1 },
  { "planeacion semanal", "r-semanal", -1, noConfig, -1, -1, noConfig, -1 }
};