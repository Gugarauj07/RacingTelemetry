from threading import Event, Thread
import serial
import serial.tools.list_ports
from time import strftime
from pathlib import Path
import csv
import pandas as pd
from random import randint
import gc

serialPort = serial.Serial()
serialPort.timeout = 0.5
alive = Event()

arquivo = strftime("%d.%m.%Y_%Hh%M")
path = Path("Arquivos_CSV")
path.mkdir(parents=True, exist_ok=True)
with open(f"Arquivos_CSV/{arquivo}.csv", 'w', newline='') as f:
    thewriter = csv.writer(f)
    thewriter.writerow(
        ['tempo', 'temp_obj', 'temp_amb', 'RPM_motor', 'RPM_roda', 'capacitivo', 'VEL_D', 'VEL_E', 'ACC', 'Distancia',
         'button_lap'])
portList = [port.device for port in serial.tools.list_ports.comports()]

# TESTING
N = 100
sensors = {
    'tempo': [x for x in range(N)],
    'temp_obj': [x + 30 for x in range(N)],
    'temp_amb': [x + 3 for x in range(N)],
    'RPM_motor': [x * 3 for x in range(N)],
    'VEL_E': [x + 32 for x in range(N)],
    'capacitivo': [x for x in range(N)],
    'button_lap': [x for x in range(N)],
    'ACC': [x for x in range(N)],
    'RPM_roda': [x * 4 for x in range(N)],
    'Distancia': [x + 200 for x in range(N)],
    'VEL_D': [x + 50 for x in range(N)],
}
df = pd.DataFrame(sensors)

df_laps = pd.DataFrame(columns=['lap_time', 'Vel_med', 'Acc_med', 'Distance'])


# ======================================
def read_serial():
    global VEL
    while alive.is_set() and serialPort.is_open:
        VEL_anterior = VEL
        tempo, temp_obj, temp_amb, RPM, VEL, capacitivo, button = serialPort.readline().decode("utf-8").split(',')
        Distancia = VEL / 3.6  # Metros
        ACC = VEL - VEL_anterior
        RPMroda = VEL / ((18 / 60) * 0.04625 * 1.72161199 * 3.6)
        line = [tempo, temp_obj, temp_amb, RPM, VEL, capacitivo, button, ACC, RPMroda, Distancia]
        df.loc[len(df)] = line

        if button == 1:
            lap_time = df['tempo']
            df_laps.loc[len(df_laps)] = []

        with open(f"Arquivos_CSV/{arquivo}.csv", 'a+', newline='') as f:
            thewriter = csv.writer(f)
            thewriter.writerow(line)

        gc.collect()


def start_thread():
    thread = Thread(target=read_serial)
    thread.daemon = True
    alive.set()
    thread.start()


def connect_serial(self):
    serialPort.port = portList[0]
    serialPort.baudrate = 9600

    try:
        serialPort.open()  # Tenta abrir a porta serial
    except:
        print("ERROR SERIAL")

    if serialPort.is_open:
        start_thread()
