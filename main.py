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

# LED kytkennät

led1 = Pin(6, Pin.OUT)
led2 = Pin(5, Pin.OUT)
led3 = Pin(4, Pin.OUT)
led4 = Pin(3, Pin.OUT)
led5 = Pin(2, Pin.OUT)

# Funktio jännitteen mittaukseen
def read_voltage():
    total = 0
    for _ in range(SAMPLES):
        total += adc.read_u16()   # lue raaka-arvo 0–65535
        sleep(0.02)
    average = total / SAMPLES
    voltage = (average / 65535) * VCC
    return voltage

# Funktio LED indikaattorille

def light_leds(count):
    leds = [led1, led2, led3, led4, led5]

    for i, led in enumerate(leds):
        if i < count:
            led.on()
        else:
            led.off()

# Pääohjelmasilmukka
while True:
    voltage = read_voltage()
    
    # Laske lämpötila siirtofunktion avulla
    temperature = 145.1 * voltage - 68.25

    if temperature < 0:
        light_leds(0)

    elif temperature >= 0 and temperature <= 10:
        light_leds(1)

    elif temperature >= 11 and temperature <= 20:
        light_leds(2)

    elif temperature >= 21 and temperature <= 30:
        light_leds(3)

    elif temperature >= 31 and temperature <= 40:
        light_leds(4)

    elif temperature >= 41 and temperature <= 50:
        light_leds(5)

    # Ylikuumeneminen
    elif temperature > 50:

        # LED vilkutus
        while temperature > 50:
            light_leds(5)
            sleep (0.2)
            light_leds(0)
            sleep(0.2)

            print("!! Ylikuumeneminen !!  {:.1f} C".format(temperature))
            lcd.move_to(0, 0)
            lcd.putstr("VAROITUS!      ")
            lcd.move_to(0, 1)
            lcd.putstr("{:.1f}{}C      ".format(temperature, DEG))


            voltage = read_voltage()
            temperature = 145.1 * voltage - 68.25

    # Tulosta molemmat arvot
    print("Jännite: {:.3f} V  |  Lämpötila: {:.1f} °C".format(voltage, temperature))

    # Tulostus LCD:lle
    lcd.clear()
    lcd.putstr("Lampotila:\n{:.1f}{}C".format(temperature, DEG))

    
    sleep(DELAY)
