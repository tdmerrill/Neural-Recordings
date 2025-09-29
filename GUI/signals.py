
from PyQt5.QtCore import QObject, pyqtSignal

class GlobalSignals(QObject):
    teensy_connected_event = pyqtSignal()
    populate_list_event = pyqtSignal(list)
    end = pyqtSignal()
    get_selected_stimuli = pyqtSignal(list, int, float, bool, float)
    request_selected_stimuli = pyqtSignal()
    send_predicted_time = pyqtSignal(float)
    write_block = pyqtSignal(str)
    write_sound = pyqtSignal(str)

    write_to_output_window = pyqtSignal(str)
    finished = pyqtSignal()


signals = GlobalSignals()
