import serial, time

from signals import signals

class MyFunctions:
    def __init__(self):
        self.ser = None

        # ===== SIGNALS =====
        signals.get_selected_stimuli.connect(self.getExpStim)

    def connectTeensy(self):
        PORT = 'COM8'
        BAUD = 115200

        self.ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)

        signals.teensy_connected_event.emit()

    def populateSongList(self):
        stimuli = []
        self.ser.write(b'LIST\n')
        while True:
            line = self.ser.readline().decode(errors='ignore').strip()
            if not line:
                continue
            if 'FILE' in line:
                print(line.split(' ')[1])
                stimuli.append(line.split(' ')[1])
            if line == 'END':
                break

        signals.populate_list_event.emit(stimuli)

    def requestExpStim(self):
        signals.request_selected_stimuli.emit()

    def getExpStim(self, list, num_repetitions, time_between_stim, jitter_bool, jitter_time):
        self.ExpStimList = list
        self.num_repetitions = num_repetitions
        self.time_between_stim = time_between_stim
        self.jitter_bool = jitter_bool
        self.jitter_time = jitter_time

    def readyExperiment(self):
        self.requestExpStim()

        # print(self.ExpStimList)
        # print(self.num_repetitions)
        # print(self.time_between_stim)
        # print(self.jitter_bool)
        # print(self.jitter_time)

    def beginExperiment(self):

        for stim in self.ExpStimList:
            print(f'Playing {stim}\n')
            self.ser.write(f'PLAY {stim}\n'.encode('utf-8'))
            time.sleep(3)