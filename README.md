# IoT Weather Station / Nutistu Ilmajaam

### 🇬🇧
##### This is an Internet of Things Weather Tracking Project that combines an Arduino Weather Station with an Automated Python Analysis Script.

#### 🌡 Weather Station

The C++ code is made to run on a tiny [ESP-12E microchip](https://en.wikipedia.org/wiki/ESP8266) paired with a [BME280 sensor](https://www.bosch-sensortec.com/bst/products/all_products/bme280) that measures ***Temperature***, ***Humidity*** and ***Barometric Pressure***. The current setup takes a new set of measurements approximately once a minute and uploads them to my Adafruit IO account. All of the weather readings of the current weather behind my window in Tallinn are [public](https://io.adafruit.com/paulpall/dashboards/ilmateade-koduouel).

#### 🤖 Analysis Script

The Python script runs on virtually any device, but will be set up for a scheduled run on my personal cloud/NAS. As I am by no means a meteorologistm, the analysis calculations are very simplistic. The statistics provide a ***Highest***, ***Lowest*** and ***Mean*** reading for each element, and for longer duration analysis, the ***Average Change Over Time*** is also shown. In addition, the script plots the readings either minute-by-minute or day-by-day (*average reading with the extremes displayed with error bars*). The report is then published on Twitter under the bot account [@ArukasPilv](https://twitter.com/ArukasPilv).

### 🇪🇪

##### See on Asjade Interneti Ilmavaatlus Projekt, mis ühildab Arduino Ilmajaama Automatiseeritud Püütoni Analüüsi Skriptiga.

#### 🌡 Ilmajaam

C++ kood on tehtud [BME280 sensoriga](https://www.bosch-sensortec.com/bst/products/all_products/bme280) ühendatud väiksel [ESP-12E mikrokiibil](https://et.wikipedia.org/wiki/ESP8266) jooksutamiseks, mis mõõdab *Temperatuuri*, *Niiskust* ja *Õhurõhku*. Praeguse häälestuse kohaselt tehakse uus kogum mõõte umbes kord minutis, mille järel need laetakse minu Adafruit IO kasutajale. Kõik ilma näidud minu akna tagant Tallinnas on [avalikult saadaval](https://io.adafruit.com/paulpall/dashboards/ilmateade-koduouel).

#### 🤖 Analüüsi Skript

Kuigi see püütoni skript toimib pea igal seadmel on ta mul üles seatud regulaarseks tööks isiklikus pilves/võrgumälus. Analüüsi arvutused on vägagi lihtsad, kuna ma ei ole meteoroloog. Statistika näitab iga elemendi ***Kõrgeimat***, ***Madalaimat*** ja ***Keskmist*** näitu, ja pikema ajaperioodi kasutusel ka ***Keskmise Muutust Üle Aja***. Lisaks, skript joonestab näidud minuti või päeva haaval (*keskmine, päeva ekstreemsused on lisatud nn vearibadena*). Seejärel esitatakse raport Twitteris [@ArukasPilv](https://twitter.com/ArukasPilv)e robot kasutajana.

## Requirements

- Arduino IDE
- [ESP8266 Board Manager](https://randomnerdtutorials.com/how-to-install-esp8266-board-arduino-ide/)
- [Adafruit BME280 Library](https://github.com/adafruit/Adafruit_BME280_Library) (Alongside it's requirements)
- [Adafruit MQTT Library](https://github.com/adafruit/Adafruit_MQTT_Library)

## Construction

Coming Soon ...

## Contributing
Open to any tips and feedback!

## Credits
- Various Adafruit IO Arduino Connection Tutorials
- [Adafruit BME280 Arduino Tutorial](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/arduino-test)

## License
[MIT](https://choosealicense.com/licenses/mit/)
