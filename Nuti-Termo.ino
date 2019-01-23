// Nuti-Termomeeter - Paul

//Teegid:
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <ESP8266WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

// WiFi sätted
//#define WLAN_SSID       "LISA WI-FI NIMI"
//#define WLAN_PASS       "LISA WI-FI PÄSS"
 
// Adafruit IO sätted
#define AIO_SERVER      "io.adafruit.com"
#define AIO_SERVERPORT  1883
#define AIO_USERNAME    "paulpall"
//#define AIO_KEY         "LISA ADAFRUIT IO VÕTI"
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);
Adafruit_MQTT_Publish temperature = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/temperature");
Adafruit_MQTT_Publish humidity = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/humidity");
Adafruit_MQTT_Publish pressure = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/pressure");

//Muutujad:
unsigned long ValimiTihedusAeg;

// Sensori ühendus viis
Adafruit_BME280 bme;


// Esmalaadimisel
void setup() {
  Serial.begin(9600);
  Serial.println(F("Nuti-Termomeeter"));
  ValimiTihedusAeg = 60000;
  Serial.println();

// Punane LED Probleemi Teavitamiseks
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

// Ühenda Sensor
  if (! bme.begin(0x76)) {
        Serial.println("Sensoriga ei saa ühendust!");
        digitalWrite(LED_BUILTIN, LOW);   // Turn the LED on (Note that LOW is the voltage level)
        while (1);
  }

// Ühenda Internetti
  Nett();
}

// Põhiline Kood
void loop() {
    NetiKontroll();
    ServeriKontroll();
    LogiValimi();
    delay(ValimiTihedusAeg);
}

// Logi Mõõtmised
void LogiValimi() {
    // Tee Mõõdud
    float Niiskus = bme.readHumidity();
    float Temperatuur = bme.readTemperature();
    float Ohurohk = bme.readPressure();
    Ohurohk = Ohurohk / 100.0F;
    // Lae üles Temperatuur
    Serial.print("Temperatuur = ");
    Serial.print(Temperatuur);
    Serial.println(" *C");
    if (! temperature.publish(Temperatuur))
      Serial.println(F("Temperatuuri üleslaadimine ebaõnnestus"));
    else
      Serial.println(F("Temperatuur üleslaetud!"));
    // Lae üles Õhurõhk
    Serial.print("Õhurõhk = ");
    Serial.print(Ohurohk);
    Serial.println(" hPa");
        if (! pressure.publish(Ohurohk))
      Serial.println(F("Õhurõhu üleslaadimine ebaõnnestus"));
    else
      Serial.println(F("Õhurõhk üleslaetud!"));
    // Lae üles Niiskus
    Serial.print("Niiskus = ");
    Serial.print(Niiskus);
    Serial.println(" %");
    if (! humidity.publish(Niiskus))
      Serial.println(F("Niiskuse üleslaadimine ebaõnnestus"));
    else
      Serial.println(F("Niiskus üleslaetud!"));

    Serial.println();
}

// Kontrolli Ühendust Serveriga
void ServeriKontroll() {
    if(! mqtt.ping(3)) {
      Serial.print(F("Serveri Ühendus on Ära Kadunud"));
      digitalWrite(LED_BUILTIN, LOW);   // Turn the LED on (Note that LOW is the voltage level)
      // reconnect to adafruit io
      if(! mqtt.connected())
        connect();
    }
}

// Kontrolli Wi-Fi Ühendust
void NetiKontroll() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print(F("Wi-Fi Ühendus on Ära Kadunud"));
    digitalWrite(LED_BUILTIN, LOW);   // Turn the LED on (Note that LOW is the voltage level)
    Nett();
  }
}

// Ühenda Wi-Fi
void Nett() {
  Serial.println(); Serial.println();
  delay(10);
  Serial.print(F("Ühendan "));
  Serial.println(WLAN_SSID);
  WiFi.begin(WLAN_SSID, WLAN_PASS);
  // Wi-Fi Ühendamine Aegub 5 Minuti Pärast
  for (int i = 0; i < 600; i++) {
       delay(500);
       Serial.print(F("."));
       if (WiFi.status() == WL_CONNECTED) {
          i = 600;
       }
  }
  Serial.println();
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi't Ei Leitud");
    digitalWrite(LED_BUILTIN, LOW);   // Turn the LED on (Note that LOW is the voltage level)
  } else {
    digitalWrite(LED_BUILTIN, HIGH);  // Turn the LED off by making the voltage HIGH
    Serial.println(F("WiFi ühendatud"));
    Serial.print(F("IP aadress: "));
    Serial.println(WiFi.localIP());
    connect();
  }
}

// Ühenda Serveriga
void connect() {
  Serial.print(F("Ühendan Adafruit IO'ga... "));
  int8_t ret;
  while ((ret = mqtt.connect()) != 0) {
    switch (ret) {
      case 1: Serial.println(F("Wrong protocol")); break;
      case 2: Serial.println(F("ID rejected")); break;
      case 3: Serial.println(F("Server unavail")); break;
      case 4: Serial.println(F("Bad user/pass")); break;
      case 5: Serial.println(F("Not authed")); break;
      case 6: Serial.println(F("Failed to subscribe")); break;
      default: Serial.println(F("Connection failed")); break;
    }
    if(ret >= 0)
      mqtt.disconnect();
    Serial.println(F("Proovin uuesti ühendada..."));
    delay(5000);
  }
  digitalWrite(LED_BUILTIN, HIGH);  // Turn the LED off by making the voltage HIGH
  Serial.println(F("Adafruit IO Ühendatud!"));
}
