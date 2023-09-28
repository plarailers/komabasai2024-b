#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

static const char SERVICE_UUID[] = "63cb613b-6562-4aa5-b602-030f103834a4";
static const char CHARACTERISTIC_SPEED_UUID[] = "88c9d9ae-bd53-4ab3-9f42-b3547575a743";
static const char CHARACTERISTIC_POSITIONID_UUID[] = "8bcd68d5-78ca-c1c3-d1ba-96d527ce8968";

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristicSpeed = NULL;
BLECharacteristic *pCharacteristicPositionId = NULL;
BLEAdvertising *pAdvertising = NULL;
uint8_t positionID = 70;

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
  }
};

class CharacteristicSpeedCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristicSpeed) {
    std::string value = pCharacteristicSpeed->getValue();

    if (value.length() > 0) {
      Serial.print("Written: ");
      int motorInput = std::stoi(value);
      Serial.print(motorInput);
      ledcWrite(0, motorInput);
      Serial.println();
    }
  }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE");

  Serial.print("Chip ID: ");
  Serial.println(ESP.getEfuseMac());

  BLEDevice::init("ESPlarail (" + getTrainName() + ")");

  Serial.print("Address: ");
  Serial.println(BLEDevice::getAddress().toString().c_str());

  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  pService = pServer->createService(SERVICE_UUID);

  pCharacteristicSpeed = pService->createCharacteristic(
    CHARACTERISTIC_SPEED_UUID,
    BLECharacteristic::PROPERTY_READ | 
    BLECharacteristic::PROPERTY_WRITE | 
    BLECharacteristic::PROPERTY_NOTIFY |
    BLECharacteristic::PROPERTY_INDICATE
  );
  pCharacteristicSpeed->setCallbacks(new CharacteristicSpeedCallbacks());
  pCharacteristicSpeed->setValue("Initial value");
  pCharacteristicSpeed->addDescriptor(new BLE2902());

  pCharacteristicPositionId = pService->createCharacteristic(
    CHARACTERISTIC_POSITIONID_UUID,
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

  /* ledcセットアップ */
  ledcSetup(0, 20000, 8);
  ledcAttachPin(25, 0);
  ledcWrite(0, 0);
  Serial.println("LEDC Setup done!!");
}

void loop() {
  pCharacteristicPositionId->setValue((uint8_t*)&positionID, 1);
  pCharacteristicPositionId->notify();
  Serial.println("Notified PositionId");
  delay(1000);
}
