
from PyQt5.QtCore import QObject, pyqtSignal

class GlobalSignals(QObject):
    teensy_connected_event = pyqtSignal()
    populate_list_event = pyqtSignal(list)
    end = pyqtSignal()
    get_selected_stimuli = pyqtSignal(list, int, float, bool, float)
    request_selected_stimuli = pyqtSignal()
    send_predicted_time = (float)


signals = GlobalSignals()
