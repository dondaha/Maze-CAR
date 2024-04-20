#include <WiFi.h>
#include <AsyncUDP.h>
#include "MecanumDriver.h"

// 创建麦克纳姆轮驱动器对象
MecanumDriver mecanum(9, 8, 12, 13, 11, 10, 46, 21);

const char *ssid = "esp32-s3-1";
const int localUdpPort = 12345;

AsyncUDP udp;
SemaphoreHandle_t mutex;

String message;
int speed1 = 0;
int speed2 = 0;
int speed3 = 0;
int speed4 = 0;

void onPacketCallback(AsyncUDPPacket packet) {
  xSemaphoreTake(mutex, portMAX_DELAY);
  message = "";
  for (int i = 0; i < packet.length(); i++) {
    message += (char)packet.data()[i];
  }
  xSemaphoreGive(mutex);
}

void setup() {
  Serial.begin(115200);  // 打开与电脑调试的串口
  mecanum.begin();       // 启动麦克纳姆轮驱动器

  WiFi.mode(WIFI_MODE_AP);  // 设置工作在STA模式

  Serial.print("Setting up Wi-Fi ");
  Serial.println(ssid);
  while (!WiFi.softAP(ssid))  // 等待网络连接成功
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Done!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());

  while (!udp.listen(localUdpPort)) {
  }
  Serial.println("UDP is listening on port " + String(localUdpPort));
  mutex = xSemaphoreCreateMutex();
  udp.onPacket(onPacketCallback);
}

void loop() {
  xSemaphoreTake(mutex, portMAX_DELAY);
  if (message.length()) {
    int begin = message.indexOf('<');
    int end = message.indexOf('>');
    if (begin != -1 && end != -1 && begin < end) {
      Serial.print("message: ");
      Serial.println(message.substring(begin, end + 1));
      sscanf(message.substring(begin, end + 1).c_str(), "<%d,%d,%d,%d>", &speed1, &speed2, &speed3, &speed4);
    }
  }
  message = "";
  xSemaphoreGive(mutex);

  speed1 = constrain(speed1, -255, 255);
  speed2 = constrain(speed2, -255, 255);
  speed3 = constrain(speed3, -255, 255);
  speed4 = constrain(speed4, -255, 255);
  
  mecanum.driveAllMotor(speed1, speed2, speed3, speed4);
  delay(50);
}
