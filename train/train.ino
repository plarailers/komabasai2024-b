/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include "train.h"

Train train(115200, "ESP32-Dr.");

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
    int     motorInput      = train.getMotorInput();
    train.moveMotor(motorInput);

    /* 積算位置検知(IPS) */
    double  wheelDistance   = train.getWheelSpeed(train.MOTOR_CURRENT_SENSOR_PIN);
    bool    isStopping      = train.getStopping();
    double  movingDistance  = train.getMovingDistance(wheelDistance, isStopping);
    train.sendMovingDistance(movingDistance);

    /* 絶対位置検知(APS) */
    int     positionID      = train.getPositionID();
    if (positionID > 0) train.sendPositionID(positionID);
    
}