import os
import sys
print(f'current working directory: {os.getcwd()}')


from PyQt5.QtWidgets import QApplication, QDialog, QSizeGrip, QListWidgetItem
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import Qt


import sys, traceback
def except_hook(exc_type, exc_value, exc_tb):
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(tb_str)  # still print to console

    # Optional: show in a message box
    # msg = QMessageBox()
    # msg.setWindowTitle("An error occurred")
    # msg.setText("A Python exception occurred:")
    # msg.setDetailedText(tb_str)
    # msg.setIcon(QMessageBox.Critical)
    # msg.exec_()

sys.excepthook = except_hook

def ui_path():
    here = os.path.dirname(os.path.abspath(__file__))  # .../GUI
    # When frozen, PyInstaller unpacks to sys._MEIPASS
    if getattr(sys, 'frozen', False):
        # support either destination you choose in --add-data (root or GUI/)
        candidates = [
            os.path.join(sys._MEIPASS, "gui.ui"),
            os.path.join(sys._MEIPASS, "gui", "gui.ui"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
    return os.path.join(here, "gui.ui")

Ui_MainWindow, QtBaseClass = uic.loadUiType(ui_path())
# qtCreatorFile = resource_path("GUI/GUI.ui")
# Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

from signals import signals
from functions import MyFunctions

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # super().__init__(parent)
        self.fns = MyFunctions()

        # ===== CONNECTIONS =====
        self.TeensyConnectButton.clicked.connect(self.fns.connectTeensy)
        self.PopulateSongListButton.clicked.connect(self.fns.populateSongList)
        self.ReadyExperimentButton.clicked.connect(self.fns.readyExperiment)
        self.BeginExperimentButton.clicked.connect(self.fns.beginExperiment)

        # ===== SIGNALS =====
        signals.teensy_connected_event.connect(self.teensy_connected)
        signals.populate_list_event.connect(self.populate_list)
        signals.end.connect(self.stop_runtime)
        signals.request_selected_stimuli.connect(self.requested_stimuli)

        # ===== DEFAULT CONDITION =====
        self.BeginExperimentButton.setEnabled(False)
        self.TeensyStatusLabel.setText("Status: Disconnected")
        self.ReadyExperimentButton.setEnabled(False)


    def teensy_connected(self):
        self.TeensyStatusLabel.setText("Status: Connected")

    def populate_list(self, list):
        #self.SelectedStimuliList.addItems(list)

        for i in list:
            item = QListWidgetItem(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.SelectedStimuliList.addItem(item)
        self.ReadyExperimentButton.setEnabled(True)

    def stop_runtime(self):
        if self.fns.ser is not None:
            print('closing serial connection...')
            self.fns.ser.close()

    def requested_stimuli(self):
        selected = []
        for i in range(self.SelectedStimuliList.count()):
            item = self.SelectedStimuliList.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())

        # ----- also get the settings -----
        num_repetitions = self.NumRepSpinBox.value()
        time_between_stim = self.TimeBetweenStimuliSpinBox.value()
        jitter_bool = self.JitterCheckbox.isChecked()
        jitter_time = self.JitterSpinBox.value()

        predicted_time = float((2.0 + time_between_stim) * len(selected) * num_repetitions)
        mins, secs = divmod(predicted_time, 60)
        hours, mins = divmod(mins, 60)
        self.PredictedTimeLabel.setText(f'Predicted Time: {int(hours)}:{int(mins):02d}:{int(secs):02d}')
        signals.get_selected_stimuli.emit(selected, num_repetitions, time_between_stim, jitter_bool, jitter_time)

        self.BeginExperimentButton.setEnabled(True)

if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        ui = MainWindow()
        ui.show()
        sys.exit(app.exec_())
    finally:
        print('closing program...')
        signals.end.emit()

