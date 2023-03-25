#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

String MACadd = "9C:9C:1F:CB:D9:F2";
uint8_t address[6]  = {0x9C, 0x9C, 0x1F, 0xCB, 0xD9, 0xF2};
bool connected;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32test", true); 
  Serial.println("The device started in master mode, make sure remote BT device is on!");
  
  // connect(address) is fast (upto 10 secs max), connect(name) is slow (upto 30 secs max) as it needs
  // to resolve name to address first, but it allows to connect to different devices with the same name.
  // Set CoreDebugLevel to Info to view devices bluetooth address and device names
  connected = SerialBT.connect(address);
  
  if(connected) {
    Serial.println("Connected Succesfully!");
  } else {
    while(!SerialBT.connected(10000)) {
      Serial.println("Failed to connect. Make sure remote device is available and in range, then restart app."); 
    }
  }
  // disconnect() may take upto 10 secs max
  if (SerialBT.disconnect()) {
    Serial.println("Disconnected Succesfully!");
  }
  // this would reconnect to the name(will use address, if resolved) or address used with connect(name/address).
  SerialBT.connect();

  pinMode( 2, OUTPUT);
  pinMode(14, INPUT_PULLUP);

  // Sign for the end of bluetooth setup.
  for (int i=0; i<3; i++) {
    digitalWrite(2, HIGH);
    delay(50);
    digitalWrite(2, LOW);
    delay(50);
  }
}

void loop() {
  String line;    // 受信文字列
  int line_len;   
  long key;
  if ( Serial.available() ) {       // 受信データがあるか？
    line = Serial.readStringUntil('¥n');  
    line_len = line.length();
    key = line.toInt();
    Serial.println(key);        // 1文字だけ読み込む
    SerialBT.write(key);
  }
  delay(20);
}