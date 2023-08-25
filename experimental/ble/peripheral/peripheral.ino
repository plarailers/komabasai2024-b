#include <BLEDevice.h>

static const char SERVICE_UUID[] = "63cb613b-6562-4aa5-b602-030f103834a4";
static const char CHARACTERISTIC_UUID[] = "88c9d9ae-bd53-4ab3-9f42-b3547575a743";

BLEServer *pServer = NULL;
BLEService *pService = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLEAdvertising *pAdvertising = NULL;

std::string getTrainName() {
  uint64_t chipId = ESP.getEfuseMac();
  switch (chipId) {
    case 0xf0d9cb1f9c9c:
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

class MyCharacteristicCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    std::string value = pCharacteristic->getValue();

    if (value.length() > 0) {
      Serial.print("Written: ");
      for (int i = 0; i < value.length(); i++) {
        Serial.print(value[i]);
      }
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

  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
  );
  pCharacteristic->setCallbacks(new MyCharacteristicCallbacks());
  pCharacteristic->setValue("Initial value");

  pService->start();

  pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("Advertising started");
}

void loop() {
  delay(1000);
}
