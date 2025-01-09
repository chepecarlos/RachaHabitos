WiFiClient net;
MQTTClient client;

void ConfigurarMQTT() {
  client.begin(BrokerMQTT, net);
  client.onMessage(mensajeMQTT);
}

// estados c - cambiar e - encender a - apagar
// Cambiar todos alsw/estudio/estado/t - c
// Cambiar individual alsw/estudio/estado/2 - c
void mensajeMQTT(String &topic, String &payload) {
  Serial.println("Mensaje: " + topic + " - " + payload);
  TelnetStream.println("Mensaje: " + topic + " - " + payload);

  int UltimoPleca = topic.lastIndexOf('/');
  int LongitudTopic = topic.length();
  String Mensaje = topic.substring(UltimoPleca + 1, LongitudTopic);


  if (Mensaje.equals("hoy")) {
    if (payload.equals("True") || Mensaje.equals("true")) {
      estadoRacha = racha;
      Serial.println("Habito hecho Hoy");
    } else {
      estadoRacha = noRacha;
      Serial.println("Habito NO hecho Hoy");
    }
  } else if (Mensaje.equals("racha")) {
    int numeroRacha = payload.toInt();
    if (numeroRacha < 0) {
      return;
    }
    Racha = numeroRacha;
  }

  // if (Mensaje.equals("t") || Mensaje.equals("T")) {
  //   boolean EstadoCambiar = true;
  //   if (payload.equals("c") || payload.equals("C")) {
  //     boolean Igual = true;
  //     for (int i = 1; i < CantidadLampara - 1; i++) {
  //       if (EstadosLampara[0] != EstadosLampara[i]) {
  //         Igual = false;
  //       }
  //     }
  //     if (Igual) {
  //       EstadoLampara = !EstadosLampara[0];
  //     } else {
  //       EstadoLampara = !EstadoLampara;
  //     }
  //     EstadoCambiar = EstadoLampara;
  //   } else if (payload.equals("e") || payload.equals("E")) {
  //     EstadoCambiar = true;
  //   } else {
  //     EstadoCambiar = false;
  //   }
  //   for (int i = 0; i < CantidadLampara; i++) {
  //     EstadosLampara[i] = EstadoCambiar;
  //     escrivirArchivo(i, EstadosLampara[i] ? "encendido" : "apagado");
  //   }
  // } else {
  //   int ID = Mensaje.toInt();
  //   if (ID < 0) return;
  //   if (payload.equals("c") || payload.equals("C")) {
  //     EstadosLampara[ID - 1] = !EstadosLampara[ID - 1];
  //   } else if (payload.equals("e") || payload.equals("E")) {
  //     EstadosLampara[ID - 1] = true;
  //   } else {
  //     EstadosLampara[ID - 1] = false;
  //   }
  //   escrivirArchivo(ID - 1, EstadosLampara[ID - 1] ? "encendido" : "apagado");
  // }
}

void enviarMQTT(String tipic, String mensaje) {
  Serial.print("Enviando[");
  Serial.print(tipic);
  Serial.print("] ");
  Serial.println(mensaje);
  client.publish(tipic, mensaje);
}
