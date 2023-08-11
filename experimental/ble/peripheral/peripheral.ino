#include <BLEDevice.h>

#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

BLEServer *server = NULL;
BLEService *service = NULL;
BLECharacteristic *characteristic = NULL;
BLEAdvertising *advertising = NULL;

class MyCharacteristicCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *characteristic) {
    std::string value = characteristic->getValue();

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

  BLEDevice::init("Device Hoge");

  Serial.print("Address: ");
  Serial.println(BLEDevice::getAddress().toString().c_str());

  server = BLEDevice::createServer();
  service = server->createService(SERVICE_UUID);
  characteristic = service->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
  );
  characteristic->setCallbacks(new MyCharacteristicCallbacks());
  characteristic->setValue("Characteristic Hoge");

  service->start();

  advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->start();
  Serial.println("Advertising");
}

void loop() {
  delay(1000);
}
