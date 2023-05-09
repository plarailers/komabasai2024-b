/* train.inoで使用する変数・関数を定義する */

#include <BluetoothSerial.h>
#include <ArduinoJson.h>
BluetoothSerial SerialBT;

#include "StopSensor.h"
#include "MotorRotationDetector.h"
#include "PositionID_Detector.h"
// #include "GetPositionID_Photo.h"

#define BUFFER_SIZE 32

class Train
{
    public:
        StopSensor stopSensor;
        PositionID_Detector positionID_Detector;
        int         serialSpeed;
        char*       serialBTPortName;
        int         MOTOR_INPUT_PIN;
        int         motorInput;
        char        buf[BUFFER_SIZE];
        StaticJsonDocument<BUFFER_SIZE> doc_r;
        StaticJsonDocument<BUFFER_SIZE> doc_s;

        Train(char* serialBTPortName);
        int     getMotorInput();
        void    moveMotor(int motorInput);
        void    sendMotorRotation(float motorRotation);
        void    sendPositionID(int positionID);
        void    sendIsStopping(bool isStopping);
};

Train::Train(char* serialBTPortName) {
    this->serialSpeed       = 115200;
    this->serialBTPortName  = serialBTPortName;
    this->MOTOR_INPUT_PIN   = 25;
    this->motorInput        = 0;
}

int Train::getMotorInput() {

    int     MOTOR_INPUT_MAX =   255;  // inputの上限
    int     MOTOR_INPUT_MIN =   0;    // inputの下限
    int     index           =   0;    // bufのインデックス

    // 基地局から受信
    while(SerialBT.available() > 0) {

        buf[index] = SerialBT.read();
        delay(3);
        // 受信したjsonが終了したらmotorInputを更新
        if(buf[index]=='}'){
            deserializeJson(doc_r, buf);
            motorInput = doc_r["mI"].as<int>();
            // Serial.println(motorInput);

            // motorInputをエコーバックする
            // String send_data="";
            // doc_s.clear();
            // doc_s["mI"] = motorInput;
            // serializeJson(doc_s,send_data);
            // SerialBT.println(send_data);

            // doc_r, buf, indexを初期化
            doc_r.clear();
            memset(buf, '\0', BUFFER_SIZE);
            index = 0;
            break;
        }
        if (index > BUFFER_SIZE - 1) {
            break;
        }
        index++;
    }
    motorInput = constrain(motorInput, MOTOR_INPUT_MIN, MOTOR_INPUT_MAX);
    return motorInput;
}

void Train::moveMotor(int motorInput) {
    ledcWrite(0, motorInput);
}

void Train::sendMotorRotation(float motorRotation) {
    String send_data="";
    doc_s.clear();
    doc_s["mR"]=motorRotation;
    serializeJson(doc_s,send_data);
    SerialBT.println(send_data);
}

void Train::sendPositionID(int positionID) {
    String send_data="";
    doc_s.clear();
    doc_s["pID"]=positionID;
    serializeJson(doc_s,send_data);
    SerialBT.println(send_data);
}

void Train::sendIsStopping(bool isStopping) {
    String send_data="";
    doc_s.clear();
    doc_s["iS"]=isStopping;
    serializeJson(doc_s,send_data);
    SerialBT.println(send_data);
}