//LEDを点灯する際はコモン(ディジット)がLOW、セグメントはHIGHになる必要がある
#define DIGIT_ON LOW
#define DIGIT_OFF HIGH
#define SEGMENT_ON HIGH
#define SEGMENT_OFF LOW

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <driver/adc.h>


static const char SERVICE_UUID[] = "cea8c671-fb2c-5f3c-87ea-7ddea950b9a5";
static const char CHARACTERISTIC_VELOCITYINSTRUCTION_UUID[] = "4bb36d3a-dace-c0e6-e70c-81e0e77930cb";

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristicVelocityInstruction = NULL;
BLEAdvertising *pAdvertising = NULL;

/*---------------- BLE 関数 ここから --------------------*/

class MyServerCallbacks : public BLEServerCallbacks {
  /// @brief BLEサーバーとの接続．切れたときにモータ停止
  /// @param pServer 
  void onConnect(BLEServer* pServer) {
    Serial.println("BLE Connected");
  }

  void onDisconnect(BLEServer *pServer) {
    Serial.println("BLE Disconnected");
    pServer->startAdvertising();
  }
};

void bleSetup() {
  /// @brief BLEのセットアップ．
  /// 1. サーバー，サービスを設定モータ入力，
  /// 2. 位置ID，ロータリエンコーダの3つのキャラクタリスティックを作る．
  /// 3. BLE通信を開始

  Serial.println("Starting BLE");

  Serial.print("Chip ID: ");
  Serial.println(ESP.getEfuseMac());

  BLEDevice::init("master controller");

  Serial.print("Address: ");
  Serial.println(BLEDevice::getAddress().toString().c_str());

  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  pService = pServer->createService(SERVICE_UUID);

  pCharacteristicVelocityInstruction = pService->createCharacteristic(
      CHARACTERISTIC_VELOCITYINSTRUCTION_UUID,
      BLECharacteristic::PROPERTY_NOTIFY
  );
  pCharacteristicVelocityInstruction->setValue("Initial value");
  pCharacteristicVelocityInstruction->addDescriptor(new BLE2902());

  pService->start();

  pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("Advertising started");
}

/*----------- BLE 関数 ここまで --------------------------*/

int velocity = 0;
int acceleration = 0;
int lasttime = 0;
int velocitydisplay = 0;
const int INPUT_MIN = 210;
const int INPUT_MAX = 3080;

void sendVelocity(){

  pCharacteristicVelocityInstruction->setValue((uint8_t*)&velocity, 4);
  pCharacteristicVelocityInstruction->notify();
  Serial.printf("velocity: %d Notified\n", velocity);
}

const int digitPins[4] = {13,14,15,16}; //コモン(ディジット)のピン番号を配列で指定
const int segmentPins[8] = {17,18,19,21,22,23,25,26}; //セグメントのピン番号を配列で指定

const int digitPinA = 13;
const int digitPinB = 14;
const int digitPinC = 15;
const int digitPinD = 16;

const int segmentPinA = 17;
const int segmentPinB = 18;
const int segmentPinC = 19;
const int segmentPinD = 21;
const int segmentPinE = 22;
const int segmentPinF = 23;
const int segmentPinG = 25;
const int segmentPinDP = 26;

const int digits[] = {
  0b01111110, //0
  0b00110000, //1
  0b01101101, //2
  0b01111001, //3
  0b00110011, //4
  0b01011011, //5
  0b01011111, //6
  0b01110010, //7
  0b01111111, //8
  0b01111011  //9
};

void displayOneNumber(int n){
  //引数を入力したい数字としてそれを表示する関数を設定
  digitalWrite(segmentPinA,digits[n] & 0b01000000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinB,digits[n] & 0b00100000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinC,digits[n] & 0b00010000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinD,digits[n] & 0b00001000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinE,digits[n] & 0b00000100 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinF,digits[n] & 0b00000010 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinG,digits[n] & 0b00000001 ? SEGMENT_ON :SEGMENT_OFF);
}

void clearSegments(){
  for (int k = 0; k < 8; k = k + 1){
    digitalWrite(segmentPins[k],SEGMENT_OFF);
  }
}

void displayNumber(int n){
  for (int j = 3; j >= 0; j = j - 1){
    digitalWrite(digitPins[j],DIGIT_ON); //右の桁から順に表示する桁(ディジット)を選択してONにする
    displayOneNumber(n % 10);
    if (j == 2){
      digitalWrite(segmentPinDP,SEGMENT_ON);
    }
    delay(1);
    clearSegments();
    digitalWrite(digitPins[j],DIGIT_OFF);
    n /= 10;
    
  }
}


void setup() {

  /* BLE セットアップ */
  bleSetup();

  for (int i = 0; i <= 3; i = i + 1){
    pinMode(digitPins[i],OUTPUT);
    digitalWrite(digitPins[i],DIGIT_OFF);
  }

  for (int i = 0; i < 8; i = i + 1){
    pinMode(segmentPins[i],OUTPUT);
    digitalWrite(segmentPins[i],SEGMENT_OFF);
  }

  Serial.begin(115200);
  pinMode(27,INPUT);

}



void loop() {

  

  if (millis() - lasttime > 100) { //100ミリ秒に1回加速度から速度の計算を行う
    

    int val = analogReadMilliVolts(27);
    Serial.println(val);

    velocity = int(255.0/(INPUT_MAX - INPUT_MIN) * (val - INPUT_MIN));

    // acceleration = ((val-128)*14/(3127-128))-8; //可変抵抗の読み取り値を-8～+5の加速度に変換
    // Serial.println(acceleration);

    // velocity = velocity + acceleration; //指定された加速度から速度を計算
  
      if (velocity <= 0){
        velocity = 0; //速度の計算値が0以下の時は0を指定
      }
      if (velocity >= 255){
        velocity = 255; //速度の計算値が255以上の時は255を指定
      }
      else{
        velocity = velocity; //速度の計算値が0～255に収まっていればそのまま
      }


    Serial.println(velocity);
    sendVelocity();

    lasttime = millis();
  }

  velocitydisplay = velocity*4;
  displayNumber(velocitydisplay);

}
