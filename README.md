# Lämpötila- ja vuotovahtijärjestelmä (Raspberry Pi Pico)

Tämä projekti käyttää kahta anturia (lämpö ja kosteus), LED-indikaattoreita sekä I2C-LCD-näyttöä.  
Dokumentaation tarkoitus on auttaa opiskelijaa tekemään ohjelmasta vuokaavio koulutehtävää varten.


## ## 1. Yleinen toiminta

- ADC0 lukee **lämpötila-anturin** jännitteen, joka muutetaan lämpötilaksi siirtofunktiolla.  
- ADC1 lukee **paperi-folio anturin** kosteusarvon ja toimii vuotovahdin rajana.  
- Lämpötilan mukaan syttyy **LED-pylväs (1–5 LEDiä)**.  
- Lämpötilan ylittäessä 50°C LED-palkki **vilkkuu** ja LCD näyttää varoitustekstin.  
- Vuotovahdin LEDit näyttävät tilanteen:
  - vihreä = ei vuotoa  
  - punainen = vuoto

LCD näyttää joko lämpötilan tai varoituksen tilanteen mukaan.


## ## 2. Kytkentätaulukko (LEDit, anturit ja LCD)

| Komponentti | Tarkoitus | Raspberry Pi Pico -pinni | Liitäntä |
|------------|-----------|---------------------------|----------|
| ADC0 lämpötila-anturi | Lusikka-anturin lämpömittaus | GP26 / ADC0 | Analoginen syöte |
| ADC1 kosteussensori | Paperi–folio-vuotovahti | GP27 / ADC1 | Analoginen syöte |
| LCD SDA | I2C-datalinja | GP14 | I2C SDA |
| LCD SCL | I2C-kellolinja | GP15 | I2C SCL |
| LED 1 | Lämpötilan alin taso | GP6 | Digital output |
| LED 2 | Lämpötilan taso | GP5 | Digital output |
| LED 3 | Lämpötilan taso | GP4 | Digital output |
| LED 4 | Lämpötilan taso | GP3 | Digital output |
| LED 5 | Lämpötilan korkein normaali taso | GP2 | Digital output |
| Vuotovahdin vihreä LED | Kuiva tila | GP10 | Digital output |
| Vuotovahdin punainen LED | Vuoto havaittu | GP11 | Digital output |


## ## 3. Funktiot

### `read_voltage()`
- Lukee ADC0:sta useita näytteitä.  
- Laskee keskiarvon ja muuntaa jännitteeksi välille 0–3.3 V.  

### `light_leds(count)`
- Ohjaa lämpötilan LED-pylvästä sytyttämällä `count` ensimmäistä LEDiä.

### `check_leak()`
- Lukee kosteussensorin arvon ADC1:stä.  
- Arvo > THRESHOLD → punainen LED ja vuotohälytys.  
- Muuten vihreä LED.

---

## ## 4. Pääohjelman kulku

1. Lue jännite → laske lämpötila.  
2. Päätä LED-pylvään valojen määrä lämpötilan mukaan.  
3. Jos lämpötila > 50°C:  
   - vilkutetaan koko LED pylvästä  
   - näytetään varoitusteksti LCD näytöllä
4. Muussa tapauksessa näytetään lämpötila LCD:ssä.  
5. Tarkistetaan vuoto (vihreä/punainen LED).  
7. Silmukka palaa alkuun.

---
