WiFiClient net;
MQTTClient client;

void ConfigurarMQTT() {
  client.begin(BrokerMQTT, net);
  client.onMessage(mensajeMQTT);
}

void mensajeMQTT(String &topic, String &payload) {
  // Serial.println("Mensaje: " + topic + " - " + payload);
  // TelnetStream.println("Mensaje: " + topic + " - " + payload);

  int Habito = -1;
  for (int i = 0; i < cantidadHabitos; i++) {
    if (topic.indexOf(listaHabitos[i].Topic) >= 0) {
      Habito = i;
      break;
    }
  }

  if (Habito < 0) {
    return;
  }

  int UltimoPleca = topic.lastIndexOf('/');
  int LongitudTopic = topic.length();
  String Mensaje = topic.substring(UltimoPleca + 1, LongitudTopic);

  if (Mensaje.equals("hoy")) {
    if (payload.equals("True") || Mensaje.equals("true")) {
      listaHabitos[Habito].Racha.Actual = racha; 
    } else {
      listaHabitos[Habito].Racha.Actual = noRacha;
    }
  }
}

void enviarMQTT(String tipic, String mensaje) {
  Serial.print("Enviando[");
  Serial.print(tipic);
  Serial.print("] ");
  Serial.println(mensaje);
  client.publish(tipic, mensaje);
}
