//sender 中継機
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;
// Bluetooth受信(Receiver)側のMacアドレスを設定する。
//String MACadd = "9C:9C:1F:CB:D9:F2";
//uint8_t address[6]  = {0x9C, 0x9C, 0x1F, 0xCB, 0xD9, 0xF2};
bool connected;
const int BUFFER_SIZE = 32;
char buf[BUFFER_SIZE];
char buf2[BUFFER_SIZE];

void setup() {

  pinMode( 5, OUTPUT);
  Serial.begin(115200);
  SerialBT.begin("ESP32_sender", true); 
  //上のtrueはmasterであることを示す
  connected = SerialBT.connect("ESP32-Dr.");
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
    int index=0;
    while(Serial.available()>0){
        buf[index] = Serial.read();
        delay(2);
        if(buf[index]=='}'){
            break;
        }
        if (index+1 >= BUFFER_SIZE) {
            break;
        }
        index++;
    }
    for(int i = 0; i <= index; i++){
        SerialBT.write(buf[i]);//データをそのまま送信
    }

    memset(buf, '\0', BUFFER_SIZE);
    index=0;

    // ESP32から受信し、pythonに送信
    while(SerialBT.available()>0) {
        buf2[index] = SerialBT.read();
        delay(2);
        if(buf2[index]=='}'){
        break;
        }
        if (index+1 >= BUFFER_SIZE) {
        break;
        }
        index++;
    }
    for(int i = 0; i <= index; i++) {
        Serial.write(buf2[i]);
    }

    memset(buf2, '\0', BUFFER_SIZE);
    index=0;

    delay(300);
}