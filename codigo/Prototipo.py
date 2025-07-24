from machine import Pin, SPI, ADC
from hx711 import HX711
from max6675 import MAX6675
import time

# --- Inicialización de sensores de presión (HX711) ---
sensor_antes = HX711(dout=4, pd_sck=5)      # HX711_1
sensor_despues = HX711(dout=18, pd_sck=19)  # HX711_2

# --- Inicialización del sensor de temperatura (MAX6675) ---
spi = SPI(1, baudrate=5000000, polarity=0, phase=0,
          sck=Pin(23), mosi=None, miso=Pin(21))
cs = Pin(22, Pin.OUT)
termocupla = MAX6675(spi, cs)

# --- Inicialización del sensor de polvo (GP2Y10) ---
sensor_polvo = ADC(Pin(33))  # Vo conectado a GPIO33
sensor_polvo.atten(ADC.ATTN_11DB)  # Escala para leer hasta 3.3V

led_gate = Pin(26, Pin.OUT)  # Control del LED del sensor de polvo

# --- Función de conversión (bruto a kPa) ---
def convertir_a_kpa(valor_bruto):
    return valor_bruto / 209715  # Ajusta según calibración real

# --- Función para leer sensor de polvo (con activación del LED) ---
def leer_polvo():
    led_gate.on()
    time.sleep_us(280)  # Según hoja de datos del GP2Y10
    raw = sensor_polvo.read()
    time.sleep_us(40)
    led_gate.off()
    time.sleep_us(9680)
    voltaje = raw * 3.3 / 4095
    return voltaje

# --- Tarear sensores de presión (si están en reposo) ---
print("Tareando sensores de presión...")
sensor_antes.tare()
sensor_despues.tare()
print("Listo. Iniciando lecturas...\n")

# --- Loop principal ---
while True:
    try:
        # Lectura de presión
        p1_raw = sensor_antes.read()
        p2_raw = sensor_despues.read()

        p1_kpa = convertir_a_kpa(p1_raw)
        p2_kpa = convertir_a_kpa(p2_raw)
        delta_kpa = p1_kpa - p2_kpa

        # Lectura de temperatura
        temperatura = termocupla.read()

        # Lectura del sensor de polvo
        voltaje_polvo = leer_polvo()

        # Mostrar resultados
        print("📈 Presión antes: {:.2f} kPa | después: {:.2f} kPa | ΔP: {:.2f} kPa".format(p1_kpa, p2_kpa, delta_kpa))
        if delta_kpa > 1.5:
            print("⚠ ¡FILTRO OBSTRUIDO!")
        else:
            print("✅ Filtro funcionando normalmente.")

        if temperatura is None:
            print("🌡 Temperatura: ⚠ Sensor no conectado o error")
        else:
            print("🌡 Temperatura: {:.2f} °C".format(temperatura))

        print("🌫 Concentración de partículas (voltaje): {:.2f} V".format(voltaje_polvo))

        print("-" * 50)
        time.sleep(2)

    except Exception as e:
        print("❌ Error en lectura:", e)
        time.sleep(2)
