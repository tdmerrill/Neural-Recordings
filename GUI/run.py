import os
import sys
#print(f'current working directory: {os.getcwd()}')

from PyQt5.QtWidgets import QApplication, QDialog, QSizeGrip, QListWidgetItem, QMessageBox
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
import sys, traceback, time, json

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
from functions import MyFunctions, ExperimentWorker

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # super().__init__(parent)
        self.fns = MyFunctions()

        # ===== CONNECTIONS =====
        self.TeensyConnectButton.clicked.connect(lambda: self.fns.connectTeensy(self.COMPortBox.text()))
        self.PopulateSongListButton.clicked.connect(self.fns.populateSongList)
        self.ReadyExperimentButton.clicked.connect(self.fns.readyExperiment)
        self.BeginExperimentButton.clicked.connect(self.start_experiment)
        self.StopExperimentButton.clicked.connect(self.stop_experiment)
        self.BFPresetButton.clicked.connect(lambda: self.preset("Bengalese Finch"))
        self.ZFPresetButton.clicked.connect(lambda: self.preset("Zebra Finch"))
        self.ResetGUIButton.clicked.connect(self.reset)

        # ===== SIGNALS =====
        signals.teensy_connected_event.connect(self.teensy_connected)
        signals.populate_list_event.connect(self.populate_list)
        signals.end.connect(self.stop_runtime)
        signals.request_selected_stimuli.connect(self.requested_stimuli)
        signals.write_block.connect(self.write_block)
        signals.write_sound.connect(self.write_sound)
        signals.write_to_output_window.connect(self.write_to_output_window)
        signals.finished.connect(self.finished_experiment)

        # ===== DEFAULT CONDITION =====
        self.BeginExperimentButton.setEnabled(False)
        self.TeensyStatusLabel.setText("Status: Disconnected")
        self.ReadyExperimentButton.setEnabled(False)
        self.StopExperimentButton.setEnabled(False)
        self.PopulateSongListButton.setEnabled(False)

        self.load_settings()

    def load_settings(self):
        path = self.settings_path()
        if os.path.isfile(path):
            with open(path, "r") as f:
                settings = json.load(f)

            # restore values
            self.NumRepSpinBox.setValue(settings.get("NumRepSpinBox", 10))
            self.TimeBetweenStimuliSpinBox.setValue(settings.get("TimeBetweenStimuliSpinBox", 10.0))
            self.JitterCheckbox.setChecked(settings.get("JitterCheckbox", True))
            self.JitterSpinBox.setValue(settings.get("JitterSpinBox", 2.0))
            self.COMPortBox.setText(settings.get("COMPortBox", "COM4"))


    def preset(self, p):
        bf_stim = ['BF_B_1800ir1.wav', 'BF_B_1800reg.wav']
        zf_stim = ['ZF_A_1200reg.wav', 'ZF_A_1800reg.wav', 'ZF_A_1200ir1.wav', 'ZF_A_1800ir1.wav']
        if p == "Bengalese Finch":
            for i in range(self.SelectedStimuliList.count()):
                item = self.SelectedStimuliList.item(i)
                text = item.text()  # the item's text
                if text in bf_stim:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
        elif p == "Zebra Finch":
            for i in range(self.SelectedStimuliList.count()):
                item = self.SelectedStimuliList.item(i)
                text = item.text()  # the item's text
                if text in zf_stim:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)


    def write_to_output_window(self, text):
        self.OutputWindow.append(text)

    def write_block(self,x):
        self.RoundLabel.setText(f'Round: {str(x)}')

    def write_sound(self,x):
        self.CurrentStimulusLabel.setText(f'Current Stimulus: {str(x)}')

    def teensy_connected(self):
        self.TeensyStatusLabel.setText("Status: Connected")
        self.PopulateSongListButton.setEnabled(True)

    def populate_list(self, list):
        self.SelectedStimuliList.clear()

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

            self.save_settings()

    def requested_stimuli(self):
        filename = self.LogFilenameLineEdit.text()
        if not filename:
            QMessageBox.warning(
                self,  # parent widget (your main window)
                "Missing filename",  # window title
                "Please enter a filename first."  # message text
            )
        else:
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

    def start_experiment(self):
        # create worker
        self.worker = ExperimentWorker(
            self.fns.ExpStimList,
            self.fns.num_repetitions,
            self.fns.time_between_stim,
            self.fns.jitter_bool,
            self.fns.jitter_time,
            self.fns.ser,
            self.LogFilenameLineEdit.text()
        )
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # connect signals
        self.worker.write_block.connect(self.write_block)
        self.worker.write_sound.connect(self.write_sound)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.started.connect(self.worker.run)
        self.thread.start()

        self.StopExperimentButton.setEnabled(True)
        self.start_time = time.time()


    def stop_experiment(self):
        if hasattr(self, 'worker'):
            reply = QMessageBox.question(
                self,  # parent window
                "Confirm Stop",  # window title
                "Are you sure you want to stop the experiment?",  # message text
                QMessageBox.Yes | QMessageBox.No,  # buttons
                QMessageBox.No  # default
            )
            if reply == QMessageBox.Yes:
                self.worker.stop()

                elapsed = time.time() - self.start_time  # seconds as float
                total_seconds = int(elapsed)  # drop fractions
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.OutputWindow.append(f"Experiment Interrupted by User after {hours:02d}:{minutes:02d}:{seconds:02d}")


    def finished_experiment(self):
        elapsed = time.time() - self.start_time  # seconds as float
        total_seconds = int(elapsed)  # drop fractions
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.OutputWindow.append(f"Experiment Finished after {hours:02d}:{minutes:02d}:{seconds:02d}")

    def reset(self):
        if hasattr(self, 'worker'):
            reply = QMessageBox.question(
                self,  # parent window
                "Confirm Reset",  # window title
                "Are you sure you want to reset the GUI?",  # message text
                QMessageBox.Yes | QMessageBox.No,  # buttons
                QMessageBox.No  # default
            )
            if reply == QMessageBox.Yes:
                self.BeginExperimentButton.setEnabled(False)
                self.ReadyExperimentButton.setEnabled(False)
                self.StopExperimentButton.setEnabled(False)

                self.PredictedTimeLabel.setText("Predicted Time:")
                self.RoundLabel.setText("Round:")
                self.CurrentStimulusLabel.setText("Current Stimulus:")

                self.OutputWindow.append("Resetting GUI...")
                time.sleep(1.5)
                self.OutputWindow.clear()

    def settings_path(self):
        home = os.path.expanduser('~')
        folder = os.path.join(home, 'Neural Recordings App')
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, 'settings.json')

    def save_settings(self):
        settings = {
            "NumRepSpinBox": self.NumRepSpinBox.value(),
            "TimeBetweenStimuliSpinBox": self.TimeBetweenStimuliSpinBox.value(),
            "JitterCheckbox": self.JitterCheckbox.isChecked(),
            "JitterSpinBox": self.JitterSpinBox.value(),
            "COMPort": self.COMPortBox.text()
        }

        with open(self.settings_path(), "w") as f:
            json.dump(settings, f, indent=2)

if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        ui = MainWindow()
        ui.show()
        sys.exit(app.exec_())
    finally:
        print('closing program...')
        signals.end.emit()

