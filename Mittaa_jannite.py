from machine import ADC, Pin, I2C
from time import sleep
from pico_i2c_lcd import I2cLcd

# =============================
# LUSIKKA-ANTURI / JÄNNITEJAKO
# =============================

# ADC0 on fyysisesti GP26
adc = ADC(Pin(26))

# I2C-yhteys LCD:lle
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
DEG = chr(223)                   # °-merkki

# Perusasetukset
VCC = 3.3        # käyttöjännite (Picon 3.3V)
SAMPLES = 10     # montako lukemaa keskiarvoistetaan
DELAY = 2.0      # sekuntia mittausten välillä

# Funktio jännitteen mittaukseen
def read_voltage():
    total = 0
    for _ in range(SAMPLES):
        total += adc.read_u16()   # lue raaka-arvo 0–65535
        sleep(0.02)
    average = total / SAMPLES
    voltage = (average / 65535) * VCC
    return voltage

# Pääohjelmasilmukka
while True:
    voltage = read_voltage()
    
    # Laske lämpötila siirtofunktion avulla
    temperature = 145.1 * voltage - 68.25

    # Tulosta molemmat arvot
    print("Jännite: {:.3f} V  |  Lämpötila: {:.1f} °C".format(voltage, temperature))

    # Tulostus LCD:lle
    lcd.clear()
    lcd.putstr("Lampotila:\n{:.1f} C".format(temperature))
    
    sleep(DELAY)
