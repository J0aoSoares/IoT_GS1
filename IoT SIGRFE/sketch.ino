#include <PubSubClient.h>
#include <WiFi.h>

#define POTENTIOMETER_PIN 34 // ESP32 D34 (ADC)

const int ANALOG_THRESHOLD = 1000;
int potValue = 0;
float volt = 0.0;
char tempAr1[6];

WiFiClient espClient;
PubSubClient mqttClient(espClient);

void setup() {
  Serial.begin(115200);
  delay(100);

  setupWiFi();
  setupMqtt();
}

void loop() {

  if (!mqttClient.connected()) {
    connectToBroker();
  }
  mqttClient.loop();

  potValue = analogRead(POTENTIOMETER_PIN);
  volt = (float)potValue / 4095 * 3.3;

  String(volt, 3).toCharArray(tempAr1, 6);
  mqttClient.publish("sigfre/medidor1", tempAr1);

  // Alerta baseado no valor lido
  if (volt < 1.5) {
    mqttClient.publish("sigfre/alerta", "Alerta: possível queda de energia!");
    Serial.println("Alerta: possível queda de energia!");
  } else if (volt < 2.5) {
    mqttClient.publish("sigfre/alerta", "Atenção: oscilação detectada");
    Serial.println("Atenção: oscilação detectada");
  } else {
    mqttClient.publish("sigfre/alerta", "Energia normal");
    Serial.println("Energia normal");
  }

  delay(1000);
}

void setupWiFi() {
  WiFi.begin("Wokwi-GUEST", "");

  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi conectado!");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());
}

void setupMqtt() {
  mqttClient.setServer("test.mosquitto.org", 1883);
}

void connectToBroker() {
  while (!mqttClient.connected()) {
    Serial.print("Conectando ao MQTT...");
    if (mqttClient.connect("ESP32_SIGRFE")) {
      Serial.println("Conectado!");
    } else {
      Serial.print("Falha. Estado: ");
      Serial.println(mqttClient.state());
      delay(2000);
    }
  }
}
