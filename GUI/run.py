import os
import sys
print(f'current working directory: {os.getcwd()}')


from PyQt5.QtWidgets import QApplication,QDialog,QSizeGrip
from PyQt5 import QtCore, QtGui, uic, QtWidgets

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

        # ===== SIGNALS =====
        signals.teensy_connected_event.connect(self.teensy_connected)

        # ===== DEFAULT CONDITION =====
        self.BeginExperimentButton.setEnabled(False)
        self.TeensyStatusLabel.setText("Status: Disconnected")


    def teensy_connected(self):
        self.TeensyStatusLabel.setText("Status: Connected")

if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        ui = MainWindow()
        ui.show()
        sys.exit(app.exec_())
    finally:
        self.ser.close()