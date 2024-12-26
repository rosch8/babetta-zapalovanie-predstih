#include <Arduino.h>

#define DATA_SIZE 14
byte data[DATA_SIZE];

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() >= DATA_SIZE) {
    for (int i = 0; i < DATA_SIZE; i++) {
      data[i] = Serial.read();
    }
    Serial.write(data, DATA_SIZE); // Echo the data back
  }
}
