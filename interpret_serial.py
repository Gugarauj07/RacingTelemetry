from threading import Event, Thread
import serial
import serial.tools.list_ports
from time import strftime
from pathlib import Path
import csv
import pandas as pd
import gc

serialPort = serial.Serial()
serialPort.timeout = 0.5
alive = Event()

arquivo = strftime("%d.%m.%Y_%Hh%M")
path = Path("Arquivos_CSV")
path.mkdir(parents=True, exist_ok=True)
with open(f"Arquivos_CSV/{arquivo}.csv", 'w', newline='') as f:
    thewriter = csv.writer(f)
    thewriter.writerow(['tempo', 'temp_obj', 'temp_amb', 'RPM', 'VEL', 'DISTANCIA', 'ACC', 'capacitivo'])
portList = []

sensors = {
    'tempo': [],
    'temp_obj': [],
    'temp_amb': [],
    'RPM': [],
    'VEL': [],
    'DISTANCIA': [],
    'ACC': [],
    'capacitivo': [],
}
df = pd.DataFrame(sensors)


def update_ports():
    portList = [port.device for port in serial.tools.list_ports.comports()]


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
    update_ports()

    serialPort.port = portList[0]
    serialPort.baudrate = 9600

    try:
        serialPort.open()  # Tenta abrir a porta serial
    except:
        print("ERROR SERIAL")

    if serialPort.is_open:
        start_thread()
