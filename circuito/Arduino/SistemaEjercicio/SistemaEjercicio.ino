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

#include <MQTT.h>
#include <TelnetStream.h>
#include "data.h"

int led = 17;
int boton = 18;

int estado = noWifi;
int estadoAnterior = -1;

void setup() {
  Serial.begin(115200);
  pinMode(led, OUTPUT);
  pinMode(boton, INPUT);
  conectarWifi();
}

// the loop function runs over and over again forever
void loop() {
  actualizarWifi();
  bool estado = digitalRead(boton);
  // Serial.print("Estado: ");
  // Serial.println(estado);
  if (digitalRead(boton)) {
    digitalWrite(led, HIGH);
    delay(1000);
    digitalWrite(led, LOW);
    delay(1000);
  }
  delay(500);
}
