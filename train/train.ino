/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <driver/adc.h>
#include <esp_int_wdt.h>
#include "MFRC522Uart.h"

/*
■■■     ■    ■■■      ■    ■     ■   ■■■■ ■■■■■■ ■■■■  ■■■     ■■■ 
■  ■■  ■■    ■  ■■   ■■    ■■    ■■  ■      ■■   ■     ■  ■■  ■    
■   ■  ■ ■   ■   ■   ■ ■   ■■   ■■■  ■      ■■   ■     ■   ■  ■    
■   ■  ■ ■   ■  ■■   ■ ■   ■ ■  ■ ■  ■      ■■   ■     ■  ■■  ■■   
■■■■  ■■ ■■  ■■■■   ■■ ■■  ■ ■  ■ ■  ■■■■   ■■   ■■■■  ■■■■     ■■ 
■     ■■■■■  ■  ■   ■■■■■  ■ ■ ■  ■  ■      ■■   ■     ■  ■      ■ 
■     ■   ■  ■  ■■  ■   ■  ■  ■■  ■  ■      ■■   ■     ■  ■■     ■ 
■    ■     ■ ■   ■ ■     ■ ■  ■   ■  ■■■■   ■■   ■■■■  ■   ■  ■■■■
*/

/* BLE パラメーラ */
static const char SERVICE_UUID[] = "63cb613b-6562-4aa5-b602-030f103834a4";
static const char CHARACTERISTIC_MOTORINPUT_UUID[] = "88c9d9ae-bd53-4ab3-9f42-b3547575a743";
static const char CHARACTERISTIC_POSITIONID_UUID[] = "8bcd68d5-78ca-c1c3-d1ba-96d527ce8968";
static const char CHARACTERISTIC_ROTATION_UUID[] = "aab17457-2755-8b50-caa1-432ff553d533";
static const char CHARACTERISTIC_VOLTAGE_UUID[] = "7ecc0ed2-5ef9-c9e6-5d16-582f86035ecf";

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristicMotorInput = NULL;
BLECharacteristic *pCharacteristicPositionId = NULL;
BLECharacteristic *pCharacteristicRotation = NULL;
BLECharacteristic *pCharacteristicVoltage = NULL;
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
const int ENCODER_1A_PIN  = 16; // 進行方向右
const int ENCODER_1B_PIN  = 17; // 進行方向右
const int ENCODER_2A_PIN  = 36; // 進行方向左
const int ENCODER_2B_PIN  = 39; // 進行方向左
volatile unsigned long preRightStepTime = 0, nowRightStepTime;
volatile unsigned long preLeftStepTime = 0, nowLeftStepTime;
unsigned long rightChattaringTime = 10;
unsigned long leftChattaringTime = 10;
byte rotation = 1; //CharacteristicRotationには1を代入してnotifyする
volatile int rightCount = 0;  // 進行方向右パルス検出回数
volatile int leftCount = 0;   // 進行方向左パルス検出回数

/* 電源電圧読み取り パラーメータ */
const int VMONITOR_PIN    = 34;
volatile unsigned long preVoltageCheckTime = 0, nowVoltageCheckTime;

/*
■■■■  ■    ■  ■    ■    ■■■ ■■■■■■ ■■    ■■■   ■    ■   ■■■ 
■     ■    ■  ■■   ■  ■■      ■■   ■   ■■  ■■  ■■   ■  ■    
■     ■    ■  ■■■  ■  ■       ■■   ■   ■    ■  ■■■  ■  ■    
■     ■    ■  ■ ■  ■  ■       ■■   ■   ■     ■ ■ ■  ■  ■■   
■■■■  ■    ■  ■  ■ ■  ■       ■■   ■   ■     ■ ■  ■ ■    ■■ 
■     ■    ■  ■  ■■■  ■       ■■   ■   ■    ■■ ■  ■■■     ■ 
■     ■   ■■  ■   ■■  ■■      ■■   ■   ■    ■  ■   ■■     ■ 
■      ■■■■   ■    ■   ■■■■   ■■   ■■   ■■■■   ■    ■  ■■■■ 
*/

/*---------------- BLE 関数 ここから --------------------*/
std::string getTrainName() {
  //////// TODO: ここのchipIdを正しく設定してください ////////
  uint64_t chipId = ESP.getEfuseMac();
  switch (chipId) {
    case 0xf07ae21b5ae0:
      return "T0";
    case 0x40158455B594:
      return "T1";
    case 0x1C7BE21B5AE0:
      return "T2";
    case 0x308466C29D1C:
      return "T3";
    case 0x3CC6F5AB4C24:
      return "T4";
    default:
      return "unknown";
  }
}

class MyServerCallbacks : public BLEServerCallbacks {
  /// @brief BLEサーバーとの接続．切れたときにモータ停止
  /// @param pServer 
  void onConnect(BLEServer* pServer) {
    Serial.println("BLE Connected");
  }

  void onDisconnect(BLEServer *pServer) {
    Serial.println("BLE Disconnected");
    pServer->startAdvertising();
    ledcWrite(FORWARD_PWM_CH, 0); //モータを停止
  }
};

class CharacteristicMotorInputCallbacks : public BLECharacteristicCallbacks {
  /// @brief モータ入力が書き込まれたらPWM出力を変更する
  /// @param pCharacteristicMotorInput 
  void onWrite(BLECharacteristic *pCharacteristicMotorInput) {
    std::string value = pCharacteristicMotorInput->getValue();
    String valueStr = value.c_str();

    if (value.length() > 0) {
      int motorInput = valueStr.toInt();
      ledcWrite(FORWARD_PWM_CH, motorInput);
      Serial.printf("motorInput: %d\n", motorInput);
    }
  }
};

void bleSetup() {
  /// @brief BLEのセットアップ．
  /// 1. サーバー，サービスを設定モータ入力，
  /// 2. 位置ID，ロータリエンコーダの3つのキャラクタリスティックを作る．
  /// 3. BLE通信を開始

  Serial.println("Starting BLE");

  uint64_t chipid;
	chipid=ESP.getEfuseMac();//The chip ID is essentially its MAC address(length: 6 bytes).
  Serial.print("ChipId: ");
  Serial.println(chipid, HEX);

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

  pCharacteristicVoltage = pService->createCharacteristic(
      CHARACTERISTIC_VOLTAGE_UUID,
      BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristicVoltage->setValue("Initial value");
  pCharacteristicVoltage->addDescriptor(new BLE2902());

  pService->start();

  pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("Advertising started");
}
/*----------- BLE 関数 ここまで --------------------------*/

/*------------ PWM(ledc) 関数 ここから -------------------*/
void pwmSetup() {
  pinMode(PWM_ENABLE_PIN, OUTPUT);
  digitalWrite(PWM_ENABLE_PIN, HIGH);  // ENABLE = HIGHでPWM有効化
  ledcSetup(FORWARD_PWM_CH, PWM_FREQ_HZ, 8);
  ledcAttachPin(PWM_FORWARD_PIN, FORWARD_PWM_CH);  // 正転側をPWMする
  pinMode(PWM_REVERSE_PIN, OUTPUT);
  digitalWrite(PWM_REVERSE_PIN, LOW);  // 逆転側はLOW固定
  Serial.println("PWM Setup done");
}
/*------------ PWM(ledc) 関数 ここまで -------------------*/

/*------------- RFID(MFRC522) 関数 ここから --------------*/
void getPositionId() {
  /// @brief 位置IDを取得
  /// カードがなくシリアル通信ができなければ抜け出す
  /// 通信できたら，UIDを読み出し，キャラクタリスティックにセットしたのち通知する．

  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if ( ! mfrc522.PICC_IsNewCardPresent()) return;

  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) return;
  
  byte positionID = mfrc522.uid.uidByte[0]; //UIDの最初の1バイトをpositionIDとする
  pCharacteristicPositionId->setValue((uint8_t*)&positionID, 1);
  pCharacteristicPositionId->notify();
  Serial.printf("positionID: %d Notified\n", positionID);

  mfrc522.PICC_HaltA(); // 卡片進入停止模式
}

void rfidSetup() {
  mfrc522.PCD_Init();
  delay(4);
  mfrc522.PCD_DumpVersionToSerial();
  Serial.println("RFID Setup done");
}
/*---------- RFID(MFRC522) 関数 ここまで ----------------*/

/*--------- ロータリエンコーダ 関数 ここから ---------------*/
/// @brief 進行方向右側のロータリエンコーダの割り込み処理
void IRAM_ATTR countRotationRight() {
  nowRightStepTime = millis();
  if(nowRightStepTime - preRightStepTime > rightChattaringTime){
    rightCount++;
    preRightStepTime = nowRightStepTime;
  }
}

/// @brief 進行方向左側のロータリエンコーダの割り込み処理
void IRAM_ATTR countRotationLeft() {
  nowLeftStepTime = millis();
  if(nowLeftStepTime - preLeftStepTime > leftChattaringTime){
    leftCount++;
    preLeftStepTime = nowLeftStepTime;
  }
}

void rotaryEncoderSetup() {
  pinMode(ENCODER_1A_PIN, INPUT);
  pinMode(ENCODER_1B_PIN, INPUT);
  pinMode(ENCODER_2A_PIN, INPUT);
  pinMode(ENCODER_2B_PIN, INPUT);
  attachInterrupt(ENCODER_1A_PIN, countRotationRight, CHANGE);
  attachInterrupt(ENCODER_2A_PIN, countRotationLeft, CHANGE);
  Serial.println("ロータリエンコーダ Setup done");
}

void rotaryEncoderLoop() {
  while (leftCount > 0) {  // 進行方向左側のパルス検出した数だけnotify
    notifyRotation();
    leftCount--;
  }
  while (rightCount > 0) {  // 進行方向右側のパルス検出した数だけnotify
    notifyRotation();
    rightCount--;
  }
}

void notifyRotation() {
  pCharacteristicRotation->setValue((uint8_t*)&rotation, 1); //rotationはbyte型なので1バイト
  pCharacteristicRotation->notify();
  // Serial.println("Rotation Notified");
}
/*---------- ロータリエンコーダ 関数 ここまで ------------*/

/*---------- 電源電圧読み取り 関数 ここから---------------*/
void checkVoltage() {
  /// @brief 1秒に1回電源電圧を読みとる
  nowVoltageCheckTime = millis();
  if (nowVoltageCheckTime -  preVoltageCheckTime > 1000) {
    uint32_t vin = analogReadMilliVolts(VMONITOR_PIN) * (178.0f/ 68.0f);
    pCharacteristicVoltage->setValue((uint8_t*)&vin, 4);
    pCharacteristicVoltage->notify();
    Serial.printf("Vin = %d mV Notified\n", vin);
    preVoltageCheckTime = nowVoltageCheckTime;
  }
}
/*---------- 電源電圧読み取り 関数 ここまで---------------*/

/*
  ■■■  ■■■■ ■■■■■■    ■    ■  ■■■  
 ■     ■      ■■      ■    ■  ■  ■■
 ■     ■      ■■      ■    ■  ■   ■
 ■■    ■      ■■      ■    ■  ■   ■
   ■■  ■■■■   ■■      ■    ■  ■■■■ 
    ■  ■      ■■      ■    ■  ■    
    ■  ■      ■■      ■   ■■  ■    
 ■■■■  ■■■■   ■■       ■■■■   ■    
*/

void setup() {

  /* Serial セットアップ */
  Serial.begin(115200);
  while (!Serial);

  /*エンコーダ2割り込みバグ回避 */
  /* https://www.mgo-tec.com/blog-entry-trouble-shooting-esp32-wroom.html/7 */
  adc_power_acquire();

  /* BLE セットアップ */
  bleSetup();

  /* PWM(ledc) セットアップ */
  pwmSetup();

  /* RFID(MFRC522) セットアップ */
  rfidSetup();

  /* ロータリエンコーダ セットアップ*/
  rotaryEncoderSetup();

}
    
/*
■       ■■■     ■■■   ■■■  
■     ■■  ■■  ■■  ■■  ■  ■■
■     ■    ■  ■    ■  ■   ■
■     ■     ■ ■     ■ ■   ■
■     ■     ■ ■     ■ ■■■■ 
■     ■    ■■ ■    ■■ ■    
■     ■    ■  ■    ■  ■    
■■■■   ■■■■    ■■■■   ■    
*/

void loop(){

  /* 電源電圧計 */
  checkVoltage();

  /* エンコーダ */
  int enc1A = digitalRead(ENCODER_1A_PIN);
  int enc1B = digitalRead(ENCODER_1B_PIN);
  int enc2A = digitalRead(ENCODER_2A_PIN);
  int enc2B = digitalRead(ENCODER_2B_PIN);
  Serial.printf("encoder = [%d, %d, %d, %d]\n", enc1A, enc1B, enc2A, enc2B);

  /* RFIDの読み取り */
  getPositionId();

  /* ロータリエンコーダがパルス検出していればnotify */
  rotaryEncoderLoop();
}