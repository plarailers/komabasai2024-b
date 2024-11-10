#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ESP32Servo.h>


/* サーボ パラメータ */
Servo servo;
// サーボを回転させる速さ。1~255。
const int SERVO_SPEED = 100;
// サーボを直進にする際の角度。適宜いじってください。
const int SERVO_ANGLE_STRAIGHT = 80; //POINT0:50, POINT1:80, POINT3:
// サーボを曲げる際の角度。適宜いじってください。
const int SERVO_ANGLE_CURVE = 20; //POINT0:69, POINT1:20, POINT3:
// サーボをアタッチするピンの指定。適宜いじってください。
const int SERVO_ATTACH_PIN = 26;
String STRAIGHT = "STRAIGHT";
String CURVE = "CURVE";

/* サーボ 関数 */
void setServo(String direction) {
    if (direction == STRAIGHT) {
        servo.write(SERVO_ANGLE_STRAIGHT);
    }
    else {
        servo.write(SERVO_ANGLE_CURVE);
    }
}

/* BLE パラメータ */
static const char SERVICE_UUID[] = "2a4023a6-6079-efea-b79f-7c882319b83b";
static const char CHARACTERISTIC_DIRECTION_UUID[] = "737237f4-300e-ca58-1e2f-40ff59fc71f7";
BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristicDirection = NULL;
BLEAdvertising *pAdvertising = NULL;

/* BLE 関数 */
std::string getPointName() {
  //////// TODO: ここのchipIdを正しく設定してください ////////
  uint64_t chipId = ESP.getEfuseMac();
  switch (chipId) {
    case 0x843699bf713c:
      return "POINT0";
    case 0xF0D9CB1F9C9C:
      return "POINT1";
    case 0x64FFA029E748:
      return "POINT3";
    default:
      return "unknown";
  }
}

class MyServerCallbacks : public BLEServerCallbacks {
  /// @brief BLEサーバーとの接続．開始時，終了時に直進にする．
  /// @param pServer 
  void onConnect(BLEServer* pServer) {
    Serial.println("BLE Connected");
  }

  void onDisconnect(BLEServer *pServer) {
    Serial.println("BLE Disconnected");
    pServer->startAdvertising();
  }
};

class CharacteristicDirectionCallbacks : public BLECharacteristicCallbacks {
  /// @brief ポイントの向きが書き込まれたらポイントの向きを変更する
  /// @param pCharacteristicDirection
  void onWrite(BLECharacteristic *pCharacteristicDirection) {
    std::string value = pCharacteristicDirection->getValue();
    String direction = value.c_str();
    setServo(direction);
  }
};

void bleSetup() {
  /// @brief BLEのセットアップ．
  /// 1. サーバー，サービスを設定
  /// 2. キャラクタリスティックを作る．
  /// 3. BLE通信を開始

  Serial.println("Starting BLE");

  uint64_t chipid;
	chipid=ESP.getEfuseMac();//The chip ID is essentially its MAC address(length: 6 bytes).
  Serial.print("ChipId: ");
  Serial.println(chipid, HEX);

  BLEDevice::init("ESPoint (" + getPointName() + ")");

  Serial.print("Address: ");
  Serial.println(BLEDevice::getAddress().toString().c_str());

  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  pService = pServer->createService(SERVICE_UUID);

  pCharacteristicDirection = pService->createCharacteristic(
      CHARACTERISTIC_DIRECTION_UUID,
      BLECharacteristic::PROPERTY_WRITE
  );
  pCharacteristicDirection->setCallbacks(new CharacteristicDirectionCallbacks());
  pCharacteristicDirection->setValue("Initial value");
  pCharacteristicDirection->addDescriptor(new BLE2902());

  pService->start();

  pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("Advertising started");
}


void setup() {
    Serial.begin(115200);
    while (!Serial);
    // attachする。
    servo.attach(SERVO_ATTACH_PIN);
    // サーボの向きの初期化。
    setServo(STRAIGHT);
    /* BLE セットアップ */
    bleSetup();
}

void loop() {
}