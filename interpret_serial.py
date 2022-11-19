from threading import Event, Thread
import serial
import serial.tools.list_ports
from time import strftime
from pathlib import Path
import csv
import pandas as pd
import gc
from random import randrange

serialPort = serial.Serial()
serialPort.timeout = 0.5

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
    'tempo': [0],
    'temp_obj': [0],
    'temp_amb': [0],
    'RPM_motor': [0],
    'VEL_E': [0],
    'capacitivo': [0],
    'button_lap': [0],
    'ACC': [0],
    'RPM_roda': [0],
    'Distancia': [0],
    'VEL_D': [0],
}
df = pd.DataFrame(sensors)

# VEL, counter_laps, tempo_inicio = 0, 0, 0


# ======================================
local_lap_count = 0
def read_serial(n):
    tempo = n
    temp_obj = randrange(40, 60)
    temp_amb = randrange(50, 60)
    RPM = randrange(600, 800)
    VEL = randrange(20, 30)
    capacitivo = randrange(0, 3)
    button = 0
    # tempo, temp_obj, temp_amb, RPM, VEL, capacitivo, button = serialPort.readline().decode("utf-8").split(',')
    Distancia = round(VEL / 3.6 + float(df["Distancia"].tail(1)), 2)  # Metros
    ACC = round(VEL - float(df["VEL_E"].tail(1)), 2)
    RPMroda = VEL / ((18 / 60) * 0.04625 * 1.72161199 * 3.6)
    line = [tempo, temp_obj, temp_amb, RPM, VEL, capacitivo, button, ACC, RPMroda, Distancia, 0]
    df.loc[len(df)] = line

    # df_tempo = df.loc[df["tempo"] == tempo_inicio:df["tempo"] == tempo]
    # acc_avg = df_tempo["ACC"].mean()
    # vel_avg = df_tempo["VEL"].mean()
    # distancia_lap = df_tempo["Distancia"].head(1) - df_tempo["Distancia"].tail(1)
    # tempo_percorrido = df_tempo["tempo"].head(1) - df_tempo["tempo"].tail(1)
    #
    # if button != counter_laps:
    #     tempo_inicio = tempo
    #     counter_laps = button

    with open(f"Arquivos_CSV/{arquivo}.csv", 'a+', newline='') as f:
        thewriter = csv.writer(f)
        thewriter.writerow(line)

    gc.collect()


def connect_serial(self):
    serialPort.port = portList[0]
    serialPort.baudrate = 9600

    try:
        serialPort.open()  # Tenta abrir a porta serial
    except:
        print("ERROR SERIAL")
