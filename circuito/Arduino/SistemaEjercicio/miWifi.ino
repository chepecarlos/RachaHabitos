
void conectarWifi() {

  wifiMulti.addAP(ssid_1, password_1);
  wifiMulti.addAP(ssid_2, password_2);

  Serial.println("Conectando con Wifi...");
  if (wifiMulti.run() == WL_CONNECTED) {
    Serial.println("");
    Serial << "SSID:" << WiFi.SSID() << " IP:" << WiFi.localIP() << "\n";
    estadoWifi.Actual = noMQTT;
  }

  MDNS.begin(nombre);
  // configurarOTA();
  ConfigurarMQTT();

  MDNS.addService("telnet", "tcp", 23);
  TelnetStream.begin();
}

void actualizarWifi() {

  if (wifiMulti.run() != WL_CONNECTED) {
    Serial.println("Wifi No Conectada!");
    delay(500);
    estadoWifi.Actual = noWifi;
    return;
  } else if (estadoWifi.Actual == conectado) {

  } else {
    estadoWifi.Actual = noMQTT;
  }

  client.loop();
  delay(10);

  if (!client.connected()) {
    Serial.println("MQTT - No Conectada!");
    if (!client.connect(nombre)) {
      delay(500);
      return;
    }
    for (int i = 0; i < cantidadHabitos; i++) {
      client.subscribe("habito/" + listaHabitos[i].Topic + "/#");
    }
    Serial.println("MQTT - Conectada!");
  }
  estadoWifi.Actual = conectado;
}


void LeerTelnet() {
  if (TelnetStream.available()) {
    char Letra = TelnetStream.read();
    switch (Letra) {
      case 'R':
        TelnetStream.stop();
        delay(100);
        ESP.restart();
        break;
      case 'e':
      case 'E':
        // estadoRele();
        break;
      case 'f':
      case 'F':
        if (!LittleFS.format()) {
          TelnetStream.println("Error formatiando");
          return;
        } else {
          TelnetStream.println("Se boro todo");
        }
        break;
    }
  }
}
