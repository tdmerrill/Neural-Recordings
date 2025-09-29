import serial, time, random, csv, os
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from signals import signals

class MyFunctions:
    def __init__(self):
        self.ser = None

        # ===== SIGNALS =====
        signals.get_selected_stimuli.connect(self.getExpStim)

    def connectTeensy(self, PORT):
        PORT = str(PORT)
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
                #print(line.split(' ')[1])
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

    # def beginExperiment(self):
    #     for i in range(0, self.num_repetitions):
    #         print(f'Beginning Block #{i+1}.')
    #         signals.write_block.emit(str(i+1))
    #
    #         self.run()
    #
    # def run(self):
    #     sounds = self.ExpStimList[:]
    #     random.shuffle(sounds)
    #
    #     for s, sound in enumerate(sounds):
    #         signals.write_sound.emit(sound)
    #         wait_time = None
    #         if self.jitter_bool:
    #             wait_time = self.time_between_stim + random.uniform(float(-self.jitter_time), float(self.jitter_time))
    #         elif not self.jitter_bool:
    #             wait_time = self.time_between_stim
    #
    #         print(f'Playing sound {sound}, then waiting {wait_time} seconds.')
    #
    #         self.ser.write(f'PLAY {sound}\n'.encode('utf-8'))
    #         time.sleep(wait_time)

class ExperimentWorker(QObject):
    finished = pyqtSignal()
    write_block = pyqtSignal(str)
    write_sound = pyqtSignal(str)

    def __init__(self, expstimlist, num_reps, time_between, jitter, jitter_time, ser, filename):
        super().__init__()
        self.ExpStimList = expstimlist
        self.num_repetitions = num_reps
        self.time_between_stim = time_between
        self.jitter_bool = jitter
        self.jitter_time = jitter_time
        self.ser = ser
        self.filename = filename
        self._stop = False

    def stop(self):
        signals.write_to_output_window.emit('Stopping the experiment...')
        self._stop = True

    def run(self):
        for i in range(self.num_repetitions):
            if self._stop:
                break
            signals.write_to_output_window.emit(f'Starting repetition {i+1}/{self.num_repetitions}.')

            self.write_block.emit(f'{str(i+1)}/{self.num_repetitions}')
            sounds = self.ExpStimList[:]
            random.shuffle(sounds)

            for sound in sounds:
                if self._stop:
                    break

                # ---- PLay Sound ----
                self.write_sound.emit(sound)
                signals.write_to_output_window.emit(f'Playing sound {sound}, then waiting {wait_time:.2f} seconds.')

                wait_time = (self.time_between_stim +
                             random.uniform(-self.jitter_time, self.jitter_time)
                             if self.jitter_bool else self.time_between_stim)

                self.ser.write(f'PLAY {sound}\n'.encode('utf-8'))

                # -- Wait for arduino to respond that song is finished playing --
                done_received = False
                while not done_received and not self._stop:
                    line = self.ser.readline().decode(errors='ignore').strip()
                    if line == f'DONE {sound}':
                        done_received = True

                # -- write output to csv file --
                self.write_to_csv(sound, wait_time)

                # -- sleep between sounds --
                time.sleep(wait_time)
        self.finished.emit()

    def write_to_csv(self, stimulus, delay_post):
        # Base folder same as settings
        home = os.path.expanduser('~')
        base_folder = os.path.join(home, 'Neural Recordings App', 'logs')
        os.makedirs(base_folder, exist_ok=True)

        # Log file path
        fp = os.path.join(base_folder, self.filename)

        # Check if file exists and create header if empty
        file_exists = os.path.isfile(fp)

        with open(fp, 'a', newline='') as logfile:
            writer = csv.writer(logfile)

            if not file_exists or os.stat(fp).st_size == 0:
                writer.writerow(["Stimulus", "Delay Post"])

            writer.writerow([stimulus, delay_post])


