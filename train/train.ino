/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include "Train.h"

Train train("ESP32-Dr.");

void setup() {
    /* Serial */
    Serial.begin(train.serialSpeed);
    while (!Serial);
    Serial.println("Serial Start!!");

    /* SerialBT */
    SerialBT.begin(train.serialBTPortName);
    Serial.println("SerialBT Start!!");

    // /* ledc */
    ledcSetup(0, 700, 8);
    ledcAttachPin(train.MOTOR_INPUT_PIN, 0);
    train.moveMotor(0);
    Serial.println("LEDC Setup done!!");

    /* BNO055 */
    train.BNO055Setup();
    Serial.println("BNO055 Setup done!!");

    // /* MFRC522 */
    // train.MFRC522Setup();
    // Serial.println("MFRC522 Setup done!!");

}

void loop(){

    // /* モータ駆動 */
    int     motorInput      = train.getMotorInput();
    train.moveMotor(motorInput);

    // /* 積算位置検知(IPS) */
    float   wheelSpeed      = train.getWheelSpeed(train.MOTOR_CURRENT_PIN);
    bool    isStopping      = train.getStopping();
    float   wheelRotation   = train.calcWheelRotation(wheelSpeed, isStopping);
    train.sendWheelRotation(wheelRotation);

    // /* 絶対位置検知(APS) */
    int     positionID      = train.getPositionID();
    if (positionID > 0) train.sendPositionID(positionID);

}