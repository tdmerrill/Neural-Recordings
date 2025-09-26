#include <Arduino.h>
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// adjust as needed:
const int TTL_PIN = 2;            // pin that goes HIGH during playback
const int SD_CS   = BUILTIN_SDCARD; // chip select for Teensy 4.1 built-in SD

AudioPlaySdWav playWav;
AudioOutputI2S audioOut;
AudioConnection patchCord1(playWav, 0, audioOut, 0);
AudioConnection patchCord2(playWav, 1, audioOut, 1);

void setup() {
  pinMode(TTL_PIN, OUTPUT);
  digitalWrite(TTL_PIN, LOW);

  Serial.begin(115200);
  AudioMemory(12);

  if (!SD.begin(SD_CS)) {
    Serial.println("SD init failed");
    while (1) delay(1000);
  }

  // Serial.println("READY");
  // Serial.println("Type LIST or PLAY filename.wav");
}

// list all WAV files in /stimuli folder
void listFiles() {
  File dir = SD.open("stimuli");
  if (!dir) {
    Serial.println("stimuli folder not found");
    return;
  }
  while (true) {
    File entry = dir.openNextFile();
    if (!entry) break;
    if (!entry.isDirectory()) {
      const char *name = entry.name();
      if (strstr(name, ".wav") || strstr(name, ".WAV")) {
        Serial.print("FILE ");
        Serial.println(name);
      }
    }
    entry.close();
  }
  Serial.println("END");
}

void playFile(const char *fname) {
  char fullpath[64];
  snprintf(fullpath, sizeof(fullpath), "stimuli/%s", fname);

  if (!SD.exists(fullpath)) {
    Serial.print("Missing: ");
    Serial.println(fullpath);
    return;
  }

  digitalWrite(TTL_PIN, HIGH);
  playWav.play(fullpath);
  delay(1); // let the library start
  while (playWav.isPlaying()) {
    delay(1);
  }
  digitalWrite(TTL_PIN, LOW);

  Serial.print("DONE ");
  Serial.println(fname);
}

void loop() {
  static char cmd[80];
  static size_t idx = 0;

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (idx > 0) {
        cmd[idx] = '\0';
        idx = 0;

        // parse command
        if (strcasecmp(cmd, "LIST") == 0) {
          listFiles();
        } else if (strncasecmp(cmd, "PLAY ", 5) == 0) {
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
