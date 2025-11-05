from machine import ADC, Pin
from time import sleep

# =============================
# LUSIKKA-ANTURI / JÄNNITEJAKO
# =============================

# ADC0 on fyysisesti GP26
adc = ADC(Pin(26))

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
    print("Jännite: {:.3f} V".format(voltage))
    sleep(DELAY)
