import serial, time
ser = serial.Serial('COM7', 115200, timeout=1)
time.sleep(2)  # give Teensy time to reset

# ask for list
stimuli=[]
ser.write(b'LIST\n')
while True:
    line = ser.readline().decode(errors='ignore').strip()
    if not line:
        continue
    if 'FILE' in line:
        print(line.split(' ')[1])
        stimuli.append(line.split(' ')[1])
    if line == 'END':
        break


print("TESTING PLAYBACK")
write_str = f'PLAY {stimuli[0]}\n'
ser.write(write_str.encode())
while True:
    line = ser.readline().decode(errors='ignore').strip()
    if line:
        print("got:", line)
    if line.startswith('DONE '):
        break
