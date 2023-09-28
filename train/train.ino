/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "MFRC522Uart.h"

/* BLE パラメーラ */
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

/* PWM(ledc) パラメータ */ 
const int PWM_FORWARD_PIN = 25;
const int PWM_REVERSE_PIN = 4;
const int PWM_ENABLE_PIN  = 2;
const int FORWARD_PWM_CH = 0;
const int REVERSE_PWM_CH = 1;
const float PWM_FREQ_HZ = 20000;

/* RFID(MFRC522) パラメーラ */
const int MFRC522_RX_PIN = 5;
const int MFRC522_TX_PIN = 19;
const int MFRC522_RST_PIN = 27;
MFRC522Uart mfrc522(&Serial2, MFRC522_RX_PIN, MFRC522_TX_PIN, MFRC522_RST_PIN);

/* ロータリエンコーダ パラメータ */
byte rotation = 1; //CharacteristicRotationには1を代入してnotifyする
const int ENCODER_1A_PIN  = 16; // 進行方向右
const int ENCODER_2A_PIN  = 36; // 進行方向左
volatile unsigned long preTime = 0, nowTime;
unsigned long chattaringTime = 10;

/* 電源電圧読み取り */
const int VMONITOR_PIN    = 34;

/* BLE 関数 ここから */
std::string getTrainName() {
  //////// TODO: ここのchipIdを正しく設定してください ////////
  uint64_t chipId = ESP.getEfuseMac();
  switch (chipId) {
    case 0x702e93bd9e7c:
      return "E5";
    case 0x9867e3ab6224:
      return "E6";
    case 0xdceacf1f9c9c:
      return "Dr.";
    case 0x2068d11f9c9c:
      return "JT";
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
    ledcWrite(FORWARD_PWM_CH, 0); //モータを停止
  }
};

class CharacteristicMotorInputCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristicMotorInput) {
    std::string value = pCharacteristicMotorInput->getValue();

    if (value.length() > 0) {
      Serial.print("motorInput: ");
      int motorInput = std::stoi(value);
      Serial.print(motorInput);
      ledcWrite(FORWARD_PWM_CH, motorInput);
      Serial.println();
    }
  }
};
/* BLE 関数 ここまで */

/* ロータリエンコーダ 関数 */
void notifyRotation() {
    nowTime = millis();
    if(nowTime - preTime > chattaringTime){
        pCharacteristicRotation->setValue((uint8_t*)&rotation, 1); //rotationはbyte型なので1バイト
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
      BLECharacteristic::PROPERTY_WRITE
  );
  pCharacteristicMotorInput->setCallbacks(new CharacteristicMotorInputCallbacks());
  pCharacteristicMotorInput->setValue("Initial value");
  pCharacteristicMotorInput->addDescriptor(new BLE2902());

  pCharacteristicPositionId = pService->createCharacteristic(
      CHARACTERISTIC_POSITIONID_UUID,
      BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristicPositionId->setValue("Initial value");
  pCharacteristicPositionId->addDescriptor(new BLE2902());

  pCharacteristicRotation = pService->createCharacteristic(
      CHARACTERISTIC_ROTATION_UUID,
      BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristicRotation->setValue("Initial value");
  pCharacteristicRotation->addDescriptor(new BLE2902());

  pService->start();

  pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("Advertising started");
  /* BLE セットアップ ここまで */


  /* PWM(ledc) セットアップ */
  pinMode(PWM_ENABLE_PIN, OUTPUT);
  digitalWrite(PWM_ENABLE_PIN, HIGH);  // ENABLE = HIGHでPWM有効化
  ledcSetup(FORWARD_PWM_CH, PWM_FREQ_HZ, 8);
  ledcAttachPin(PWM_FORWARD_PIN, FORWARD_PWM_CH);  // 正転側をPWMする
  pinMode(PWM_REVERSE_PIN, OUTPUT);
  digitalWrite(PWM_REVERSE_PIN, LOW);  // 逆転側はLOW固定
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