#include <Arduino.h>
#include <DHT.h>
#include <ESP32Servo.h>  // Importa la librería ESP32Servo

// Definición de pines
const int pinLM35_1 = 34;
const int pinLM35_2 = 35;
const int pinLM35_3 = 32;
const int foco = 19;
const int ventilador = 18;
const int BOMBAPIN = 4;         // Pin para la bomba de agua
const int SERVOPIN1 = 2;        // Pin para el servomotor
#define DHTPIN 15               // Pin donde está conectado el sensor DHT11
#define DHTTYPE DHT11           // Tipo de sensor DHT

// Configuración del sensor DHT y servomotor
DHT dht(DHTPIN, DHTTYPE);
Servo servo1;                   // Declara el servomotor

// Variables de control
int temperaturaObjetivo = 20;
bool temperaturaEstablecida = false;
bool ventiladorEncendido = false;
bool focoEncendido = false;
bool anularVentiladorApagado = false;
bool anularFocoApagado = false;

unsigned long ultimaActualizacion = 0;
const unsigned long intervaloActualizacion = 500;
const int intensidadMinima = 50;

void setup() {
  Serial.begin(115200);

  // Configuración de dispositivos
  dht.begin();                  // Inicia el sensor DHT
  pinMode(ventilador, OUTPUT);
  pinMode(foco, OUTPUT);
  pinMode(BOMBAPIN, OUTPUT);
  analogWrite(ventilador, 0);   // Apagar ventilador
  analogWrite(foco, 0);         // Apagar foco
  digitalWrite(BOMBAPIN, LOW);  // Bomba inicialmente apagada
  
  // Configuración de servomotor
  servo1.attach(SERVOPIN1);     // Conecta el servomotor al pin definido
  servo1.write(0);              // Posición inicial del servomotor
}

void loop() {
  unsigned long tiempoActual = millis();
  if (tiempoActual - ultimaActualizacion >= intervaloActualizacion) {
    ultimaActualizacion = tiempoActual;

    // Leer y calcular la temperatura promedio de los sensores LM35
    float temperatura1 = analogRead(pinLM35_1) * (5 / 4095.0) * 100.0;
    float temperatura2 = analogRead(pinLM35_2) * (5 / 4095.0) * 100.0;
    float temperatura3 = analogRead(pinLM35_3) * (5 / 4095.0) * 100.0;
    float temperaturaPromedio = (temperatura1 + temperatura2 + temperatura3) / 3.0;

    // Leer la humedad del sensor DHT11
    float humedad = dht.readHumidity();

    // Enviar datos de temperatura promedio y humedad al puerto serie
    Serial.print("TEMP:");
    Serial.println(temperaturaPromedio);
    Serial.print("HUMIDITY:");
    Serial.println(humedad);
    Serial.print("LIGHT:");
    Serial.println(focoEncendido ? "ON" : "OFF");
    Serial.print("FAN:");
    Serial.println(ventiladorEncendido ? "ON" : "OFF");

    // Control de foco y ventilador solo si se ha recibido una temperatura
    if (temperaturaEstablecida && !anularFocoApagado && !anularVentiladorApagado) {
      if (temperaturaPromedio < temperaturaObjetivo - 2 && !ventiladorEncendido) {
        focoEncendido = true;
        int intensidadFoco = map(temperaturaObjetivo - (int)temperaturaPromedio, 0, 10, intensidadMinima, 255);
        analogWrite(foco, intensidadFoco);
        ventiladorEncendido = false;
        analogWrite(ventilador, 0);
      } else if (temperaturaPromedio > temperaturaObjetivo + 2 && !focoEncendido) {
        ventiladorEncendido = true;
        int intensidadVentilador = map((int)temperaturaPromedio - temperaturaObjetivo, 0, 10, intensidadMinima, 255);
        analogWrite(ventilador, intensidadVentilador);
        focoEncendido = false;
        analogWrite(foco, 0);
      } else if (temperaturaPromedio >= temperaturaObjetivo - 2 && temperaturaPromedio <= temperaturaObjetivo + 2) {
        if (focoEncendido) {
          analogWrite(foco, intensidadMinima);
        } else if (ventiladorEncendido) {
          analogWrite(ventilador, intensidadMinima);
        }
      } else {
        ventiladorEncendido = false;
        focoEncendido = false;
        analogWrite(ventilador, 0);
        analogWrite(foco, 0);
      }
    }

    // Apagar dispositivos manualmente
    if (anularFocoApagado) {
      focoEncendido = false;
      analogWrite(foco, 0);
    }
    if (anularVentiladorApagado) {
      ventiladorEncendido = false;
      analogWrite(ventilador, 0);
    }
  }

  // Procesar comandos de la GUI
  if (Serial.available()) {
    char comando = Serial.read();

    switch (comando) {
      case 'T': {  // Configuración de la temperatura objetivo
        String tempStr = Serial.readStringUntil('\n');
        temperaturaObjetivo = tempStr.toInt();
        temperaturaEstablecida = true;
        anularVentiladorApagado = false;
        anularFocoApagado = false;
        break;
      }
      case 'L':  // Apagar el foco
        anularFocoApagado = true;
        focoEncendido = false;
        analogWrite(foco, 0);
        break;

      case 'F':  // Apagar el ventilador
        anularVentiladorApagado = true;
        ventiladorEncendido = false;
        analogWrite(ventilador, 0);
        break;

      case 'B':  // Activa la bomba de agua
        digitalWrite(BOMBAPIN, HIGH);
        break;

      case 'b':  // Desactiva la bomba de agua
        digitalWrite(BOMBAPIN, LOW);
        break;

      case 'O':  // Abre la "ventana" (servomotor a 90°)
        servo1.write(90);
        break;

      case 'C':  // Cierra la "ventana" (servomotor a 0°)
        servo1.write(0);
        break;

      default:
        Serial.println("Comando no reconocido");
        break;
    }
  }
}