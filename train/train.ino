/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include "Train.h"

Train train("ESP32-Dr.");

unsigned int old_time = 0;
unsigned int new_time = 0;

void setup() {

    /* Serial */
    Serial.begin(train.serialSpeed);
    while (!Serial);
    Serial.println("Serial Start!!");

    /* SerialBT */
    SerialBT.begin(train.serialBTPortName);
    Serial.println("SerialBT Start!!");

    /* ledcセットアップ */
    ledcSetup(0, 700, 8);
    ledcAttachPin(train.MOTOR_INPUT_PIN, 0);
    train.moveMotor(0);
    Serial.println("LEDC Setup done!!");

    /* モータ回転数検知セットアップ */
    motorRotationDetectorSetup();
    Serial.println("MotorRotationDetector Setup done!!");

    /* BNO055セットアップ */
    train.stopSensor.BNO055Setup();
    Serial.println("BNO055 Setup done!!");

    /* MFRC522セットアップ */
    train.positionID_Detector.MFRC522Setup();
    Serial.println("MFRC522 Setup done!!");

}

void loop(){

    /* モータ駆動 */
    int     motorInput      = train.getMotorInput();
    train.moveMotor(motorInput);

    // 100ms毎にモータ回転数と停止検知を行う
    new_time = millis();
    if (new_time - old_time > 100) {

        /* モータ回転数 */
        float   motorRotation   = motorRotationDetector.getRotation();
        // if (motorRotation > 0) train.sendMotorRotation(motorRotation);

        /* 停止検知(SS) */
        bool    isStopping      = train.stopSensor.getStopping();
        train.sendIsStopping(isStopping);

        old_time = new_time;
    }

    /* 絶対位置検知(APS) */
    int     positionID      = train.positionID_Detector.getPositionID();
    if (positionID > 0) train.sendPositionID(positionID);

}