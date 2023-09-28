/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "MFRC522Uart.h"

/* BLE パラメーラ・関数 ここから */
static const char SERVICE_UUID[] = "63cb613b-6562-4aa5-b602-030f103834a4";
static const char CHARACTERISTIC_MOTORINPUT_UUID[] = "88c9d9ae-bd53-4ab3-9f42-b3547575a743";
static const char CHARACTERISTIC_POSITIONID_UUID[] = "8bcd68d5-78ca-c1c3-d1ba-96d527ce8968";
static const char CHARACTERISTIC_ROTATION_UUID[] = "aab17457-2755-8b50-caa1-432ff553d533";

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristicMotorInput = NULL;
BLECharacteristic *pCharacteristicPositionId = NULL;
BLECharacteristic *pCharacteristicRotation = NULL;
BLEAdvertising *pAdvertising = NULL;

std::string getTrainName() {
  uint64_t chipId = ESP.getEfuseMac();
  switch (chipId) {
    case 0x702e93bd9e7c:
      return "E5";
    case 0x9867e3ab6224:
      return "E6";
    case 0xdceacf1f9c9c:
      return "Dr.";
    default:
      return "unknown";
  }
}

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    Serial.println("Connected");
  }

  void onDisconnect(BLEServer *pServer) {
    Serial.println("Disconnected");
    pServer->startAdvertising();
    ledcWrite(0, 0); //モータを停止
  }
};

class CharacteristicMotorInputCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristicMotorInput) {
    std::string value = pCharacteristicMotorInput->getValue();

    if (value.length() > 0) {
      Serial.print("motorInput: ");
      int motorInput = std::stoi(value);
      Serial.print(motorInput);
      ledcWrite(0, motorInput);
      Serial.println();
    }
  }
};
/* BLE パラメーラ・関数 ここまで */


/* PWM(ledc) パラメータ */ 
const int FORWARD_PWM_CH = 0;
const int REVERSE_PWM_CH = 1;
const float PWM_FREQ_HZ = 20000;


/* RFID(MFRC522) パラメーラ */
#define MFRC522_RX_PIN 5
#define MFRC522_TX_PIN 19
#define MFRC522_RST_PIN 27
MFRC522Uart mfrc522(&Serial2, MFRC522_RX_PIN, MFRC522_TX_PIN, MFRC522_RST_PIN);


/* ロータリエンコーダ パラメータ・関数 */
byte rotation = 1;
const int ENCODER_1A_PIN  = 16; // 進行方向右
const int ENCODER_2A_PIN  = 36; // 進行方向左
volatile unsigned long preTime = 0, nowTime;
unsigned long chattaringTime = 10;

void notifyRotation() {
    nowTime = millis();
    if(nowTime - preTime > chattaringTime){
        pCharacteristicRotation->setValue((uint8_t*)&rotation, 1);
        pCharacteristicRotation->notify();
        Serial.println("Rotation Notified");
        preTime = nowTime;
    }
}


/*
  ■■■■  ■■■■■■■■■■■■■    ■     ■   ■■■■■  
 ■      ■■       ■       ■     ■   ■■  ■■ 
 ■      ■■       ■       ■     ■   ■■   ■ 
 ■■     ■■       ■       ■     ■   ■■  ■■ 
  ■■■   ■■■■■    ■       ■     ■   ■■■■■  
     ■  ■■       ■       ■     ■   ■■     
     ■■ ■■       ■       ■■    ■   ■■     
     ■  ■■       ■        ■   ■■   ■■     
 ■■■■   ■■■■■■   ■         ■■■■    ■■    
*/

void setup() {

    /* Serial セットアップ */
    Serial.begin(115200);
    while (!Serial);

    /* BLE セットアップ ここから*/
    Serial.println("Starting BLE");

    Serial.print("Chip ID: ");
    Serial.println(ESP.getEfuseMac());

    BLEDevice::init("ESPlarail (" + getTrainName() + ")");

    Serial.print("Address: ");
    Serial.println(BLEDevice::getAddress().toString().c_str());

    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    pService = pServer->createService(SERVICE_UUID);

    pCharacteristicMotorInput = pService->createCharacteristic(
        CHARACTERISTIC_MOTORINPUT_UUID,
        BLECharacteristic::PROPERTY_READ | 
        BLECharacteristic::PROPERTY_WRITE | 
        BLECharacteristic::PROPERTY_NOTIFY |
        BLECharacteristic::PROPERTY_INDICATE
    );
    pCharacteristicMotorInput->setCallbacks(new CharacteristicMotorInputCallbacks());
    pCharacteristicMotorInput->setValue("Initial value");
    pCharacteristicMotorInput->addDescriptor(new BLE2902());

    pCharacteristicPositionId = pService->createCharacteristic(
        CHARACTERISTIC_POSITIONID_UUID,
        BLECharacteristic::PROPERTY_READ | 
        BLECharacteristic::PROPERTY_WRITE | 
        BLECharacteristic::PROPERTY_NOTIFY |
        BLECharacteristic::PROPERTY_INDICATE
    );
    pCharacteristicPositionId->setValue("Initial value");
    pCharacteristicPositionId->addDescriptor(new BLE2902());

    pCharacteristicRotation = pService->createCharacteristic(
        CHARACTERISTIC_ROTATION_UUID,
        BLECharacteristic::PROPERTY_READ | 
        BLECharacteristic::PROPERTY_WRITE | 
        BLECharacteristic::PROPERTY_NOTIFY |
        BLECharacteristic::PROPERTY_INDICATE
    );
    pCharacteristicPositionId->setValue("Initial value");
    pCharacteristicPositionId->addDescriptor(new BLE2902());

    pService->start();

    pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->start();
    Serial.println("Advertising started");
    /* BLE セットアップ ここまで */


    /* PWM(ledc) セットアップ */
    ledcSetup(0, 20000, 8);
    ledcAttachPin(25, 0);
    ledcWrite(0, 0);
    Serial.println("PWM Setup done");


    /* RFID(MFRC522) セットアップ */
    mfrc522.PCD_Init();
    delay(4);
    mfrc522.PCD_DumpVersionToSerial();
    Serial.println("RFID Setup done");


    /* ロータリエンコーダ セットアップ*/
    pinMode(ENCODER_1A_PIN, INPUT);
    pinMode(ENCODER_2A_PIN, INPUT);
    attachInterrupt(ENCODER_1A_PIN, notifyRotation, CHANGE);
    attachInterrupt(ENCODER_2A_PIN, notifyRotation, CHANGE);
    Serial.println("ロータリエンコーダ Setup done");

}
    
/*
■■       ■■■■      ■■■■    ■■■■■  
■■      ■■   ■■   ■■   ■■  ■■  ■■ 
■■     ■■     ■  ■■     ■  ■■   ■ 
■■     ■      ■  ■      ■  ■■  ■■ 
■■     ■      ■  ■      ■  ■■■■■  
■■     ■      ■  ■      ■  ■■     
■■     ■■     ■  ■■     ■  ■■     
■■      ■■   ■■   ■■   ■■  ■■     
■■■■■■   ■■■■      ■■■■    ■■ 
*/

void loop(){

    /* RFIDの読み取り */

    // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
	if ( ! mfrc522.PICC_IsNewCardPresent()) return;

	// Select one of the cards
	if ( ! mfrc522.PICC_ReadCardSerial()) return;
	
	byte positionID = mfrc522.uid.uidByte[0]; //UIDの最初の1バイトをpositionIDとする
	Serial.print("positionID: ");
	Serial.print(positionID);
    pCharacteristicPositionId->setValue((uint8_t*)&positionID, 1);
    pCharacteristicPositionId->notify();
    Serial.println(" Notified");

	mfrc522.PICC_HaltA(); // 卡片進入停止模式

}