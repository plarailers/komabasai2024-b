/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include <BluetoothSerial.h>
BluetoothSerial SerialBT;
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>


#include "train.h"

Train train(115200, "ESP32-Dr.", A18, 4);


void setup() {
    /* Serial */
    Serial.begin(train.serialSpeed);
    while (!Serial);

    /* SerialBT */
    SerialBT.begin(train.serialPortName);

    /* ledc */
    ledcSetup(0, 700, 8);
    ledcAttachPin(train.MOTOR_INPUT_PIN, 0);

    /* BNO055 */
    train.BNO055Setup();

    /* MFRC522 */
    train.MFRC522Setup();

}

void loop(){

    /* モータ駆動 */
    int     motorInput      = getMotorInput();
    moveMotor(motorInput);

    /* 積算位置検知(IPS) */
    double  wheelDistance   = getWheelSpeed();
    bool    isStopping      = getStopping();
    double  movingDistance  = getMovingDistance(wheelDistance, isStopping);
    sendMovingDistance(movingDistance);

    /* 絶対位置検知(APS) */
    int     positionID      = getPositionID();
    if (positionID > 0) sendPositionID(positionID);
    
}