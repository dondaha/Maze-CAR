#include <WiFi.h>
#include <Arduino.h>
#include <AsyncUDP.h>
#include "MecanumDriver.h"

const int id = 25;
MecanumDriver mecanum(9, 8, 12, 13, 11, 10, 46, 21);

const char *ssid = "LAPTOP-DDH";
const char *passwd = "ywtywtywt";
const int port = 12345;

const IPAddress ip_address(192, 168, 1, 200 + id);
const IPAddress gateway(192, 168, 1, 1);
const IPAddress subnet(255, 255, 255, 0);

AsyncUDP udp;
SemaphoreHandle_t mutex;

String message;
int duty_cycle1 = 0;
int duty_cycle2 = 0;
int duty_cycle3 = 0;
int duty_cycle4 = 0;

void onPacketCallback(AsyncUDPPacket packet)
{
  xSemaphoreTake(mutex, portMAX_DELAY);
  message = "";
  for (int i = 0; i < packet.length(); i++)
  {
    message += (char)packet.data()[i];
  }
  Serial.println(message);
  xSemaphoreGive(mutex);
}

void setup()
{
  Serial.begin(115200);
  mecanum.begin();

  WiFi.mode(WIFI_MODE_STA);
  if (WiFi.config(ip_address, gateway, subnet) == false)
  {
    Serial.println("Wi-Fi configuration failed");
  }
  Serial.printf("Connecting to Wi-Fi: %s", ssid);
  WiFi.begin(ssid, passwd);
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(100);
  }
  Serial.printf("\r\nConnected to Wi-Fi: %s\r\n", ssid);
  Serial.printf("IP Address: %s\r\n", WiFi.localIP().toString());

  while (!udp.listen(port))
  {
  }
  Serial.printf("UDP is listening on port %d\r\n", port);
  mutex = xSemaphoreCreateMutex();
  udp.onPacket(onPacketCallback);
}

void loop()
{
  xSemaphoreTake(mutex, portMAX_DELAY);
  if (message.length())
  {
    int begin = message.indexOf('<');
    int end = message.indexOf('>');
    if (begin != -1 && end != -1 && begin < end)
    {
      sscanf(message.substring(begin, end + 1).c_str(), "<%d,%d,%d,%d>", &duty_cycle1, &duty_cycle2, &duty_cycle3, &duty_cycle4);
    }
  }
  message = "";
  xSemaphoreGive(mutex);

  mecanum.setDutyCycle(duty_cycle1, duty_cycle2, duty_cycle3, duty_cycle4);

  delay(50);
}