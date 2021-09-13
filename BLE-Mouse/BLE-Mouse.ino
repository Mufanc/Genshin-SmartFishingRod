
#include <BleMouse.h>
#include <WiFi.h>

BleMouse bleMouse("ESP32蓝牙鼠标", "Espressif", 100); //其中“ESP32蓝牙键盘”为键盘名称；"Espressif"为制造商

#define LED_PIN 2

char teststring;
void down() {
  digitalWrite(LED_PIN, HIGH);
}

void up() {
  digitalWrite(LED_PIN, LOW);
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);   //串口和Arduino之间的通信
  bleMouse.begin();
}

void loop() {
  while (Serial.available() > 0) {
    teststring = Serial.read();
    if (teststring == '1') {

      Serial.println("click");
      if (bleMouse.isConnected()) {
        bleMouse.click(MOUSE_LEFT);
      }
      down();
    }
    else {
      up();
    }
    Serial.print(teststring);
    delay(50);
  }
}
