template<class T> inline Print &operator<<(Print &obj, T arg) {
  obj.print(arg);
  return obj;
}


#if defined(ESP32)
//Librerias para ESP32
#include <WiFi.h>
#include <WiFiMulti.h>
#include <ESPmDNS.h>
WiFiMulti wifiMulti;

#elif defined(ESP8266)
//Librerias para ESP8266
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266mDNS.h>
ESP8266WiFiMulti wifiMulti;

#endif

#define noWifi 0
#define noMQTT 1
#define conectado 2

#define noConfig 0
#define noRacha 1
#define racha 2

#include <MQTT.h>
#include <TelnetStream.h>
#include <Ticker.h>
#include "data.h"
#include "miHabitos.h"

boolean EstadoLed = false;
boolean EstadoLedIndicador = false;

Ticker cambiarIndicador;

int ledIndicador = 15;

estadoIndicador estadoWifi = { noWifi, -1 };

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Habitos Cargados");
  for (int i = 0; i < cantidadHabitos; i++) {
    Serial.print(listaHabitos[i].Nombre);
    Serial.print(" - ");
    Serial.println(listaHabitos[i].Topic);
    pinMode(listaHabitos[i].Led, OUTPUT);
    pinMode(listaHabitos[i].Boton, INPUT);
  }
  Serial.println();

  pinMode(ledIndicador, OUTPUT);
  conectarWifi();
}

void loop() {
  actualizarWifi();
  actualizarBotones();
  actualizarRacha();
  actualizarIndicador();
  delay(500);
}

void actualizarBotones() {
  for (int i = 0; i < cantidadHabitos; i++) {
    bool estado = digitalRead(listaHabitos[i].Boton);
    if (estado) {
      Serial.print("Reportando por MQTT ");
      Serial.println(listaHabitos[i].Nombre);
      listaHabitos[i].Cambiador.attach(0.1, funcionLedRacha, i);
      enviarMQTT("habito/" + listaHabitos[i].Topic + "/reportar", "si");
      delay(5000);
      listaHabitos[i].Racha.Anterior = -1;
    }
  }
}

void funcionLedRacha(int id) {
  listaHabitos[id].EstadoLed = !listaHabitos[id].EstadoLed;
  digitalWrite(listaHabitos[id].Led, listaHabitos[id].EstadoLed ? HIGH : LOW);
}

void funcionLedIndicador() {
  EstadoLedIndicador = !EstadoLedIndicador;
  digitalWrite(ledIndicador, EstadoLedIndicador ? HIGH : LOW);
}

void actualizarRacha() {
  for (int i = 0; i < cantidadHabitos; i++) {
    if (listaHabitos[i].Racha.Actual != listaHabitos[i].Racha.Anterior) {
      Serial.print("Cambiando ");
      Serial.print(listaHabitos[i].Nombre);
      Serial.print(" Racha: ");

      listaHabitos[i].Racha.Anterior = listaHabitos[i].Racha.Actual;

      switch (listaHabitos[i].Racha.Actual) {
        case noConfig:
          Serial.print("No configurado");
          listaHabitos[i].Cambiador.attach(2, funcionLedRacha, i);
          break;
        case noRacha:
          Serial.print("NO");
          listaHabitos[i].Cambiador.attach(0.5, funcionLedRacha, i);
          break;
        case racha:
          Serial.print("SI");
          listaHabitos[i].Cambiador.detach();
          digitalWrite(listaHabitos[i].Led, HIGH);
          break;
      }
      Serial.println();
    }
  }
}



void actualizarIndicador() {
  if (estadoWifi.Actual != estadoWifi.Anterior) {
    Serial.print("Estado Wifi: ");
    Serial.print(estadoWifi.Actual);
    Serial.print(" - ");

    estadoWifi.Anterior = estadoWifi.Actual;

    switch (estadoWifi.Actual) {
      case noWifi:
        Serial.print("NoWifi");
        cambiarIndicador.attach(2, funcionLedIndicador);
        break;
      case noMQTT:
        Serial.print("NoMQTT");
        cambiarIndicador.attach(1, funcionLedIndicador);
        break;
      case conectado:
        Serial.print("MQTT");
        cambiarIndicador.attach(0.25, funcionLedIndicador);
        break;
    }
    Serial.println();
  }
}
