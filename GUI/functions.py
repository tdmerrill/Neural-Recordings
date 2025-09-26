import serial, time

from signals import signals

class MyFunctions:
    def __init__(self):
        pass

    def connectTeensy(self):
        PORT = 'COM7'
        BAUD = 115200

        self.ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)

        signals.teensy_connected_event.emit()