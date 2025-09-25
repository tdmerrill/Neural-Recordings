import serial, csv, random, time

ser = serial.Serial('COM3', 115200, timeout=1)

sounds = ['a.wav', 'b.wav', 'c.wav']
random.shuffle(sounds)

with open('log.csv','a',newline='') as f:
    writer = csv.writer(f)
    for s in sounds:
        t = time.time()  # when we sent command
        ser.write(f"PLAY {s}\n".encode())
        # optionally wait for Teensy to say DONE
        line = ser.readline().decode().strip()
        print(line)
        writer.writerow([t, s, line])
        f.flush()
