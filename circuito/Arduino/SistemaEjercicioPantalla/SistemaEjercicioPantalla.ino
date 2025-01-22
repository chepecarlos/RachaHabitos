
// https://github.com/Xinyuan-LilyGO/LilyGo-EPD47/tree/esp32s3

// Tools ->
//  *      Board:"ESP32S3 Dev Module"
//  *      USB CDC On Boot:"Enable"
//  *      USB DFU On Boot:"Disable"
//  *      Flash Size : "16MB(128Mb)"
//  *      Flash Mode"QIO 80MHz
//  *      Partition Scheme:"16M Flash(3M APP/9.9MB FATFS)"
//  *      PSRAM:"OPI PSRAM"
//  *      Upload Mode:"UART0/Hardware CDC"
//  *      USB Mode:"Hardware CDC and JTAG"

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
#include "miHabitos.h"


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
  Serial.println("Iniciando Sistema de Habitos");

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

  Serial.println("Habitos Cargados");
  for (int i = 0; i < cantidadHabitos; i++) {
    Serial.print(listaHabitos[i].Nombre);
    Serial.print(" - ");
    Serial.println(listaHabitos[i].Topic);
  }
  Serial.println();
}

// the loop function runs over and over again forever
void loop() {
  actualizarWifi();
  actualizarRacha();
  delay(500);
}

void actualizarRacha() {
  bool Cambio = false;

  for (int i = 0; i < cantidadHabitos; i++) {
    if (listaHabitos[i].Racha.Actual != listaHabitos[i].Racha.Anterior || listaHabitos[i].Hoy.Actual != listaHabitos[i].Hoy.Anterior || listaHabitos[i].Porcentaje.Actual != listaHabitos[i].Porcentaje.Anterior) {
      Cambio = true;
      Serial.print(listaHabitos[i].Nombre);
      Serial.print(" ");
      Serial.print(listaHabitos[i].Racha.Actual);
      Serial.print(" Racha, Hoy ");
      Serial.print(listaHabitos[i].Hoy.Actual == racha ? "Si" : "No");
      Serial.println();
      listaHabitos[i].Racha.Anterior = listaHabitos[i].Racha.Actual;
      listaHabitos[i].Hoy.Anterior = listaHabitos[i].Hoy.Actual;
      listaHabitos[i].Porcentaje.Anterior = listaHabitos[i].Porcentaje.Actual;
    }
  }


  if (Cambio) {

    epd_poweron();
    epd_clear();

    int cursorX = 30;
    int cursorY = 30;

    for (int i = 0; i < cantidadHabitos; i++) {
      String Texto = "" + Texto += listaHabitos[i].Nombre + ": ";
      Texto += String(listaHabitos[i].Racha.Actual) + " Racha, ";
      Texto += "Hoy ";
      if (listaHabitos[i].Hoy.Actual == racha) {
        Texto += "SI";
      } else {
        Texto += "NO";
      }

      if (listaHabitos[i].Hoy.Actual == noRacha && listaHabitos[i].Porcentaje.Actual >= 0) {
        Texto += ", " + String(listaHabitos[i].Porcentaje.Actual) + "%";
      }

      cursorX = 30;
      cursorY += 50;
      writeln((GFXfont *)&FiraSans, (char *)Texto.c_str(), &cursorX, &cursorY, NULL);
    }

    epd_poweroff();
  }
}
