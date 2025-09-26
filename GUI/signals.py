
from PyQt5.QtCore import QObject, pyqtSignal

class GlobalSignals(QObject):
    teensy_connected_event = pyqtSignal()


signals = GlobalSignals()
