#include <stdint.h> //uintの定義
#include <Wire.h>
#include <ESP32Servo.h>

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define MODULE_SELECT_PIN 17 //自分の環境に合わせてRXDピン(4ピン)と接続するesp32のピン番号を指定
#define ADDRESS 0x52 //ToFモジュールのI2Cのaddress

#define PWM_PIN 25 //自分の環境に合わせてPWMピンと接続するesp32のピン番号を指定
#define DISTANCE_APPROACHING 120 //車両が接近したと判断する距離
#define DEGREE_NORMAL 90 //通常時の架線柱の角度
#define DEGREE_COLLAPSE 180 //倒壊時の架線柱の角度

#define TIME_OF_NORMAL 60000 //架線柱が倒れるまでの通常運行の最小時間
#define TIME_OF_COLLAPSE 60000 //架線柱が倒れている時間

Servo myservo;
uint32_t nowtime, changetime, timedelta;
bool iscollapsed;

static const char SERVICE_UUID[] = "62dd9b52-2995-7978-82e2-6abf1ae56555";
static const char CHARACTERISTIC_ISCOLLAPSED_UUID[] = "79fe0b5c-754c-3fe0-941f-3dc191cf09bf";

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristicIsCollapsed = NULL;
BLEAdvertising *pAdvertising = NULL;

class MyServerCallbacks : public BLEServerCallbacks { 
    void onConnect(BLEServer* pServer){
        Serial.println("BLE Connected");
    }
    
    void onDisconnect(BLEServer *pServer){
        Serial.println("BLE Disconnected");
        pServer->startAdvertising();
    }
};

void bleSetup() {
    Serial.println("Starting BLE");
    BLEDevice::init("Wire Pole");
    
    Serial.print("Address: ");
    Serial.println(BLEDevice::getAddress().toString().c_str());
    
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());
    
    pService = pServer->createService(SERVICE_UUID);
    
    pCharacteristicIsCollapsed = pService->createCharacteristic(
        CHARACTERISTIC_ISCOLLAPSED_UUID,
        BLECharacteristic::PROPERTY_WRITE |
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pCharacteristicIsCollapsed->setValue("Initial value");
    pCharacteristicIsCollapsed->addDescriptor(new BLE2902());

    pService->start();
    
    pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->start();
    Serial.println("Advertising started");
}

void sendIsCollapsed(bool iscollapsed){
    pCharacteristicIsCollapsed->setValue((uint8_t*)&iscollapsed, 1);
    pCharacteristicIsCollapsed->notify();
    Serial.printf("positionID: %d Notified\n", iscollapsed);
}

uint16_t readDistance(){
    Wire.beginTransmission(ADDRESS);
    Wire.write(0xD3);
    Wire.endTransmission(0);
    Wire.requestFrom(ADDRESS, 2);

    uint16_t distance = 0;
    uint16_t distance_tmp = 0;
    uint8_t data_count = 0;

    while(Wire.available()){
        distance_tmp = Wire.read();
        distance = (distance << (data_count * 8)) | distance_tmp;
        data_count++;
    }

    return distance;
}

void setup(){
    Serial.begin(115200);
    Wire.begin();
    pinMode(MODULE_SELECT_PIN, OUTPUT);

    myservo.attach(PWM_PIN);
    myservo.write(DEGREE_NORMAL);

    nowtime = 0;
    changetime = 0;
    timedelta = 0;

    iscollapsed = 0;

    bleSetup();

    delay(1000);
}

void loop(){
    digitalWrite(MODULE_SELECT_PIN, LOW);
    delay(5);
    
    uint16_t distance = readDistance();

    Serial.print(distance);
    Serial.println("mm");
    
    digitalWrite(MODULE_SELECT_PIN, HIGH);
    delay(45);

    nowtime = (uint32_t)millis();
    timedelta = nowtime - changetime;

    if(iscollapsed == 0){
        if(timedelta > TIME_OF_NORMAL && distance > DISTANCE_APPROACHING){
            myservo.write(DEGREE_COLLAPSE);
            changetime = nowtime;
            iscollapsed = 1;
            sendIsCollapsed(iscollapsed);
            delay(300);
        }
        else{
            myservo.write(DEGREE_NORMAL);
        }
    }

    else if(iscollapsed == 1){
        if(timedelta > TIME_OF_COLLAPSE){
            myservo.write(DEGREE_NORMAL);
            changetime = nowtime;
            iscollapsed = 0;
            sendIsCollapsed(iscollapsed);
            delay(300);
        }
        else{
            myservo.write(DEGREE_COLLAPSE);
        }
    }
}