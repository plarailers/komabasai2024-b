//受信用
#include "BluetoothSerial.h"
#include <ArduinoJson.h>

BluetoothSerial SerialBT;

const int BUFFER_SIZE = 32;
char buf[BUFFER_SIZE];
StaticJsonDocument<BUFFER_SIZE> doc_r;
StaticJsonDocument<BUFFER_SIZE> doc_s;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32_receiver"); //Bluetoothのdevice name
  Serial.println("The device started, now you can pair it with bluetooth!");
}

void loop() {
  //ESP32から受信
  int index=0;
  while(SerialBT.available()>0) {
    buf[index] = SerialBT.read();
    delay(2);
    if(buf[index]=='}'){
      Serial.println("find");//特に意味はあんまりない改行
      break;
    }
    if (index+1 >= BUFFER_SIZE) {
      break;
    }
    index++;
  }
  //EPS32に送信
  String send_data="";
  doc_s.clear();
  doc_s["pID"]=14;
  doc_s["wR"]=200;
  serializeJson(doc_s,send_data);
  SerialBT.println(send_data);
  delay(100);
  //test用にprint
  //kokokara
  for(int i = 0; i <= index; i++){
        Serial.print(buf[i]);
  }
  deserializeJson(doc_r, buf); 
  //kokomade
  index=0;
  memset(buf, '\0', BUFFER_SIZE);
  doc_r.clear();
  delay(300);
}