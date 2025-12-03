from machine import ADC, Pin, I2C
from time import sleep
from pico_i2c_lcd import I2cLcd
import network
import urequests

# =============================
# LUSIKKA-ANTURI (LÄMPÖMITTARI)
# PAPERI-FOLIO-ANTURI (VUOTOVAHTI)
# =============================

# ADC0 (Lämpömittari)
adc = ADC(Pin(26))
# ADC1 (Vuotovahti)
adc_hum = ADC(Pin(27))

# I2C-yhteys LCD:lle
i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
DEG = chr(223)                   # °-merkki

# Perusasetukset
VCC = 3.3           # käyttöjännite (Picon 3.3V)
SAMPLES = 10        # montako lukemaa keskiarvoistetaan
DELAY = 2.0         # sekuntia mittausten välillä
THRESHOLD = 40000   # Vuotovahdin raja-arvo

# Lämpötilailmaisimen LED kytkennät

led1 = Pin(6, Pin.OUT)
led2 = Pin(5, Pin.OUT)
led3 = Pin(4, Pin.OUT)
led4 = Pin(3, Pin.OUT)
led5 = Pin(2, Pin.OUT)

# Vuotovahdin LED kytkennät
led_green = Pin(10, Pin.OUT)
led_red = Pin(11, Pin.OUT)

# =============================
# THINGSPEAK-ASETUKSET
# =============================
SSID = "Wokwi-GUEST"
PASSWORD = ""

WRITE_API_KEY = "RDNRM48C5ODU3MSR"
CHANNEL_ID = "Y3190908"

# -----------------------------
# WIFI-YHTEYS
# -----------------------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("WiFi: Connecting", end="")
    while not wlan.isconnected():
        print(".", end="")
        sleep(0.3)

    print("\nWiFi Connected:", wlan.ifconfig()[0])

# -----------------------------
# THINGSPEAK-LÄHETYS
# -----------------------------
def send_to_thingspeak(temp, leak_value):
    url = (
        f"https://api.thingspeak.com/update?"
        f"api_key={WRITE_API_KEY}"
        f"&field1={temp}"
        f"&field2={leak_value}"
    )

    try:
        r = urequests.get(url)
        print("ThingSpeak:", r.text)
        r.close()
    except Exception as e:
        print("TS error:", e)


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

# Funktio vuotovahdille
def check_leak():
    value = adc_hum.read_u16()

    if value > THRESHOLD:
        # Märkä → punainen LED palaa
        led_green.off()
        led_red.on()
        print("!! Vuoto havaittu !!")
    else:
        # Kuiva → vihreä LED palaa
        led_red.off()
        led_green.on()
        print("Vuotovahti: ", value)
    return value

# Pääohjelmasilmukka
connect_wifi()
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
        light_leds(5)
        sleep (1)
        light_leds(0)
        sleep(0.01)

        print("!! Ylikuumeneminen !!  {:.1f} C".format(temperature))
        lcd.move_to(0, 0)
        lcd.putstr("VAROITUS!      ")
        lcd.move_to(0, 1)
        lcd.putstr("{:.1f}{}C      ".format(temperature, DEG))


        voltage = read_voltage()
        temperature = 145.1 * voltage - 68.25

    # Tulosta molemmat arvot
    print("Jännite: {:.3f} V  |  Lämpötila: {:.1f} °C".format(voltage, temperature))

    # LCD-näyttö
    if temperature > 50:
        lcd.clear()
        lcd.putstr("VAROITUS!\n{:.1f}{}C".format(temperature, DEG))
    else:
        lcd.clear()
        lcd.putstr("Lampotila:\n{:.1f}{}C".format(temperature, DEG))

    leak_value = check_leak()

    # -------------------------
    # Lähetä tiedot ThingSpeakiin
    # -------------------------
    send_to_thingspeak(temperature, leak_value)

    # Ylikuumenemisen aikana pidä silmukka nopeana,
    # jotta LED-vilkku ja LCD-päivitys toimivat oikein

    if temperature > 50:
        sleep(0.01)
    else:
        sleep(DELAY)

