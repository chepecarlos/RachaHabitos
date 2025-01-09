
// Pantalla Tinta Electronica

#ifndef BOARD_HAS_PSRAM
#error "Please enable PSRAM, Arduino IDE -> tools -> PSRAM -> OPI !!!"
#endif

#include <Arduino.h>
#include "epd_driver.h"
#include "utilities.h"
#include "firasans.h"

uint8_t *framebuffer = NULL;
char buf[128];

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
int Racha = 0;
int RachaAnterior = -1;

void setup() {
  Serial.begin(115200);
  delay(1000);
  framebuffer = (uint8_t *)ps_calloc(sizeof(uint8_t), EPD_WIDTH * EPD_HEIGHT / 2);
  if (!framebuffer) {
    Serial.println("alloc memory failed !!!");
    while (1)
      ;
  }
  memset(framebuffer, 0xFF, EPD_WIDTH * EPD_HEIGHT / 2);

  epd_init();

  // epd_poweron();
  // epd_clear();
  epd_poweroff();
  // pinMode(ledEstado, OUTPUT);
  // pinMode(ledIndicador, OUTPUT);
  // pinMode(boton, INPUT);
  conectarWifi();
}

// the loop function runs over and over again forever
void loop() {
  actualizarWifi();
  actualizarRacha();
  // bool estado = digitalRead(boton);
  // if (digitalRead(boton)) {
  //   // digitalWrite(ledEstado, HIGH);
  //   enviarMQTT("habito/ejercicio/reportar", "si");
  //   delay(5000);
  //   // digitalWrite(ledEstado, LOW);
  // }
  // actualizarIndicador();
  delay(500);
}

void actualizarRacha() {
  if (estadoRacha != estadoRachaAnterior || Racha != RachaAnterior) {
    Serial.print("Racha: ");
    Serial.print(Racha);
    Serial.print(" Hoy:");
    Serial.println(estadoRacha == racha ? "Si" : "No");

    estadoRachaAnterior = estadoRacha;
    RachaAnterior = Racha;
    epd_poweron();
    epd_clear();

    int cursor_x = 200;
    int cursor_y = 200;
    if (estadoRacha == noRacha) {
      String Texto = "Racha Ejercicio: " + String(Racha) + " Hoy: No";
      epd_fill_rect(10, 10, 80, 80, 150, framebuffer);
      writeln((GFXfont *)&FiraSans, (char *)Texto.c_str(), &cursor_x, &cursor_y, NULL);
    } else if (estadoRacha == racha) {
      String Texto = "Racha Ejercicio: " + String(Racha) + " Hoy: Si";
      epd_fill_rect(10, 10, 80, 80, 150, framebuffer);
      writeln((GFXfont *)&FiraSans, (char *)Texto.c_str(), &cursor_x, &cursor_y, NULL);
    }
    epd_poweroff();
  }
}

// void funcionLedRacha() {
//   EstadoLed = !EstadoLed;
//   digitalWrite(ledEstado, EstadoLed ? HIGH : LOW);
// }

// void funcionLedIndicador() {
//   EstadoLedIndicador = !EstadoLedIndicador;
//   digitalWrite(ledIndicador, EstadoLedIndicador ? HIGH : LOW);
// }

// void actualizarRacha() {
//   if (estadoRacha != estadoRachaAnterior) {
//     Serial.print("Cambiando Racha ");
//     Serial.println(estadoRacha);

//     estadoRachaAnterior = estadoRacha;

//     switch (estadoRacha) {
//       case noConfig:
//         cambiarLed.attach(2, funcionLedRacha);
//         break;
//       case noRacha:
//         cambiarLed.attach(0.5, funcionLedRacha);
//         break;
//       case racha:
//         cambiarLed.detach();
//         digitalWrite(ledEstado, HIGH);
//         break;
//     }
//   }
// }


// void actualizarIndicador() {
//   if (estadoIndicador != estadoIndicadorAnterior) {
//     Serial.print("Cambiando Estado ");
//     Serial.println(estadoIndicador);

//     estadoIndicadorAnterior = estadoIndicador;

//     switch (estadoIndicador) {
//       case noWifi:
//         cambiarIndicador.attach(2, funcionLedIndicador);
//         break;
//       case noMQTT:
//         cambiarIndicador.attach(1, funcionLedIndicador);
//         break;
//       case conectado:
//         cambiarIndicador.attach(0.25, funcionLedIndicador);
//         break;
//     }
//   }
// }
