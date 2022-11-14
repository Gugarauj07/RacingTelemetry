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
    thewriter.writerow(['tempo', 'temp_obj', 'temp_amb', 'RPM_motor', 'RPM_roda', 'capacitivo', 'VEL_E', 'VEL_D'])
portList = [port.device for port in serial.tools.list_ports.comports()]

# TESTING
N = 1000
sensors = {
    'tempo': [x for x in range(N)],
    'temp_obj': [x + 30 for x in range(N)],
    'temp_amb': [x + 3 for x in range(N)],
    'RPM_motor': [x * 3 for x in range(N)],
    'RPM_roda': [x * 2 for x in range(N)],
    'VEL_D': [x + 32 for x in range(N)],
    'capacitivo': [randint(0, 3) for _ in range(N)],
    'VEL_E': [x + 25 for x in range(N)],
    'ACC': [x + 25 for x in range(N)],
}
df = pd.DataFrame(sensors)


# ======================================


def read_serial():
    while alive.is_set() and serialPort.is_open:
        data = serialPort.readline().decode("utf-8").split(',')
        line = [data[0], data[1], data[2]]
        df.loc[len(df)] = line
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
