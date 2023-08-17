/* 車載統合ソフトウェア */
/* メインの処理を行う  */

#include "Train.h"

Train train("ESP32-E5");

void setup() {

    /* Serial */
    Serial.begin(train.serialSpeed);
    while (!Serial);
    Serial.print(train.serialBTPortName);
    Serial.print(" ");
    Serial.println("Serial Start!!");

    /* SerialBT */
    train.SerialBT.begin(train.serialBTPortName);
    Serial.println("SerialBT Start!!");

    /* ledcセットアップ */
    ledcSetup(0, 20000, 8);
    ledcAttachPin(train.MOTOR_INPUT_PIN, 0);
    train.moveMotor(0);
    Serial.println("LEDC Setup done!!");

    /* MFRC522セットアップ */
    train.positionID_Detector.MFRC522Setup();
    Serial.println("MFRC522 Setup done!!");

}

void loop(){

    /* モータ駆動 */
    int     motorInput      = train.getMotorInput();
    // 基地局から切断された時はモータ停止
    if (!train.SerialBT.connected()) {
        motorInput = 0;
    }
    train.moveMotor(motorInput);

    /* 積算位置検知(IPS) */
    //TODO: IPSのコードを書く

    /* 絶対位置検知(APS) */
    int     positionID      = train.positionID_Detector.getPositionID();
    if (positionID > 0) train.sendData("pID", positionID);
}