#include <Arduino.h>
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// Pin definitions
const int TTL_PIN = 2;                // TTL out to Intan
const int SD_CS   = BUILTIN_SDCARD;   // Teensy 4.1 SD card

// Audio objects
AudioPlaySdWav           playWav1;
AudioOutputI2S           audioOut;   // I²S output to Audio Shield
AudioConnection          patchCord1(playWav1, 0, audioOut, 0);
AudioConnection          patchCord2(playWav1, 1, audioOut, 1);

void setup() {
  pinMode(TTL_PIN, OUTPUT);
  digitalWrite(TTL_PIN, LOW);

  Serial.begin(115200);
  AudioMemory(12);

  if (!SD.begin(SD_CS)) {
    Serial.println("SD init failed");
    while (1) delay(1000);
  }
  Serial.println("Ready. Send: PLAY filename.wav");
}

void playFile(const char *filename) {
  // make sure file exists
  if (!SD.exists(filename)) {
    Serial.print("Missing file: ");
    Serial.println(filename);
    return;
  }

  // TTL high immediately before playback
  digitalWrite(TTL_PIN, HIGH);

  playWav1.play(filename);
  delay(1); // let it start

  // wait until finished
  while (playWav1.isPlaying()) {
    // could also check Serial here for STOP commands, etc.
    delay(1);
  }

  digitalWrite(TTL_PIN, LOW);

  // notify PC
  Serial.print("DONE ");
  Serial.println(filename);
}

void loop() {
  static char cmd[64];
  static size_t idx = 0;

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (idx > 0) {
        cmd[idx] = '\0';
        idx = 0;
        // Parse "PLAY filename.wav"
        if (strncmp(cmd, "PLAY ", 5) == 0) {
          playFile(cmd + 5);
        } else {
          Serial.print("Unknown cmd: ");
          Serial.println(cmd);
        }
      }
    } else if (idx < sizeof(cmd) - 1) {
      cmd[idx++] = c;
    }
  }
}
