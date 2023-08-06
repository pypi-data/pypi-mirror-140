import serial.tools.list_ports
import serial

import logging

log = logging.getLogger(__name__)


class MXSerial:
    def __init__(self, com, bps):
        self.ser = serial.Serial(com, bps, timeout=5)

    def send(self, data):
        self.ser.write(data.encode())

    def readline(self):
        return self.ser.readline().decode().strip("\r\n")

    def read(self):
        return self.ser.read().decode().strip("\r\n")

    def close(self):
        self.ser.close()
