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

boolean EstadoLed = false;
boolean EstadoLedIndicador = false;

Ticker cambiarLed;
Ticker cambiarIndicador;

int ledEstado = 17;
int ledIndicador = 2;
int boton = 18;

int estadoIndicador = noWifi;
int estadoIndicadorAnterior = -1;

int estadoRacha = noConfig;
int estadoRachaAnterior = -1;

void setup() {
  Serial.begin(115200);
  pinMode(ledEstado, OUTPUT);
  pinMode(ledIndicador, OUTPUT);
  pinMode(boton, INPUT);
  conectarWifi();
}

// the loop function runs over and over again forever
void loop() {
  actualizarWifi();
  bool estado = digitalRead(boton);
  if (digitalRead(boton)) {
    digitalWrite(ledEstado, HIGH);
    enviarMQTT("habito/ejercicio/reportar", "si");
    delay(5000);
    digitalWrite(ledEstado, LOW);
  }
  actualizarRacha();
  actualizarIndicador();
  delay(500);
}

void funcionLedRacha() {
  EstadoLed = !EstadoLed;
  digitalWrite(ledEstado, EstadoLed ? HIGH : LOW);
}

void funcionLedIndicador() {
  EstadoLedIndicador = !EstadoLedIndicador;
  digitalWrite(ledIndicador, EstadoLedIndicador ? HIGH : LOW);
}

void actualizarRacha() {
  if (estadoRacha != estadoRachaAnterior) {
    Serial.print("Cambiando Racha ");
    Serial.println(estadoRacha);

    estadoRachaAnterior = estadoRacha;

    switch (estadoRacha) {
      case noConfig:
        cambiarLed.attach(2, funcionLedRacha);
        break;
      case noRacha:
        cambiarLed.attach(0.5, funcionLedRacha);
        break;
      case racha:
        cambiarLed.detach();
        digitalWrite(ledEstado, HIGH);
        break;
    }
  }
}


void actualizarIndicador() {
  if (estadoIndicador != estadoIndicadorAnterior) {
    Serial.print("Cambiando Estado ");
    Serial.println(estadoIndicador);

    estadoIndicadorAnterior = estadoIndicador;

    switch (estadoIndicador) {
      case noWifi:
        cambiarIndicador.attach(2, funcionLedIndicador);
        break;
      case noMQTT:
        cambiarIndicador.attach(1, funcionLedIndicador);
        break;
      case conectado:
        cambiarIndicador.attach(0.25, funcionLedIndicador);
        break;
    }
  }
}
