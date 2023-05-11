//sender 中継機
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

bool connected;
const int BUFFER_SIZE = 32;
char buf[BUFFER_SIZE];
char buf2[BUFFER_SIZE];

void setup() {

  pinMode( 5, OUTPUT);
  Serial.begin(115200);
  SerialBT.begin("ESP32_sender", true); 
  //上のtrueはmasterであることを示す
  connected = SerialBT.connect("ESP32-Dr");
  //addressはname or Macaddressを引数にとる。前者はmax30ms後者はmax10ms程度の秒数で接続可能
  
    if(connected){
        Serial.println("Connected Succesfully!");
    }
    else {
        while(!SerialBT.connected(10000)) {
        Serial.println("Failed to connect. Make sure remote device is available and in range, then restart app."); 
        }
    }
  
}

void loop() {  
    // pythonから受信し、ESP32に送信
    while(Serial.available()>0){
        char sendData = Serial.read();
        SerialBT.write(sendData);
    }

    // ESP32から受信し、pythonに送信
    while(SerialBT.available()>0) {
        char recvData = SerialBT.read();
        Serial.write(recvData);
    }
}