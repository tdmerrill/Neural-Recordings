#include <Arduino.h>
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

// adjust as needed:
const int TTL_PIN = 2;            // pin that goes HIGH during playback
const int SD_CS   = BUILTIN_SDCARD; // chip select for Teensy 4.1 built-in SD

AudioPlaySdWav playWav1;
AudioOutputI2S audioOutput;
AudioConnection patchCord1(playWav1, 0, audioOutput, 0);
AudioConnection patchCord2(playWav1, 1, audioOutput, 1);
AudioControlSGTL5000     sgtl5000_1;

// Use these with the Teensy Audio Shield
#define SDCARD_CS_PIN    10
#define SDCARD_MOSI_PIN  7   // Teensy 4 ignores this, uses pin 11
#define SDCARD_SCK_PIN   14  // Teensy 4 ignores this, uses pin 13

void setup() {
  pinMode(TTL_PIN, OUTPUT);
  digitalWrite(TTL_PIN, LOW);

  Serial.begin(115200);
  AudioMemory(8);

  sgtl5000_1.enable();
  sgtl5000_1.volume(0.5);

  SPI.setMOSI(SDCARD_MOSI_PIN);
  SPI.setSCK(SDCARD_SCK_PIN);
  if (!(SD.begin(SDCARD_CS_PIN))) {
    // stop here, but print a message repetitively
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }

}

void playSound(const char *filename)
{
  Serial.print("Playing file: ");
  Serial.println(filename);

  // Start playing the file.  This sketch continues to
  // run while the file plays.
  playWav1.play(filename);

  // A brief delay for the library read WAV info
  delay(10);

  // Simply wait for the file to finish playing.
  while (playWav1.isPlaying()) {
    // uncomment these lines if you audio shield
    // has the optional volume pot soldered
    //float vol = analogRead(15);
    //vol = vol / 1024;
    // sgtl5000_1.volume(vol);
  }
}

// list all WAV files in /stimuli folder
void listFiles() {
  File dir = SD.open("/");   // open root instead of "stimuli"
  if (!dir) {
    Serial.println("SD root not found");
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
  // no folder path now — just use fname directly
  if (!SD.exists(fname)) {
    Serial.print("Missing: ");
    Serial.println(fname);
    return;
  }

  digitalWrite(TTL_PIN, HIGH);

  // play the sound file
  playSound(fname);      // or playWav.play(fname) if you use the Audio library
  // delay(1);            // let the library start
  // while (playWav.isPlaying()) {
  //   delay(1);
  // }

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
