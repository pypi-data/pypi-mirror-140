import serial
import serial.tools.list_ports


def find_com_port():
    for port in serial.tools.list_ports.comports():
        if 'USB Serial' in port:
            return port.device


class Controller:
    def __init__(self, port=None):
        port = port or find_com_port()
        self._controller = serial.Serial(port=port, baudrate=115200, timeout=0.1)

    def rotate(self, steps: int, motor: str = 'a'):
        self._controller.write(f'{motor}{steps}\n'.encode('utf-8'))
