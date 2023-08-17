/* train.inoで使用する変数・関数を定義する */

#include <BluetoothSerial.h>
#include <ArduinoJson.h>
#include "src/StopSensor.h"
#include "src/PositionID_Detector.h"

#define BUFFER_SIZE 32
#define JSON_BUFFER_SIZE 256

class Train
{
    public: 
        int         serialSpeed;
        char*       serialBTPortName;
        int         MOTOR_INPUT_PIN;
        int         motorInput;
        char        buf[BUFFER_SIZE];
        StaticJsonDocument<JSON_BUFFER_SIZE> doc_r;
        StaticJsonDocument<JSON_BUFFER_SIZE> doc_s;

        BluetoothSerial             SerialBT;
        StopSensor                  stopSensor;
        PositionID_Detector         positionID_Detector;

        Train(char* serialBTPortName);

        int     getMotorInput();
        void    moveMotor(int motorInput);
        void    sendData(String key, int value);
};

Train::Train(char* serialBTPortName)
:   serialSpeed(115200),
    serialBTPortName(serialBTPortName),
    MOTOR_INPUT_PIN(25),
    motorInput(0)
{}

int Train::getMotorInput() {

    int     MOTOR_INPUT_MAX =   255;  // inputの上限
    int     MOTOR_INPUT_MIN =   0;    // inputの下限
    int     index           =   0;    // bufのインデックス

    // 基地局から受信
    while(SerialBT.available() > 0 || Serial.available() > 0) {

        if (SerialBT.available() > 0) buf[index] = SerialBT.read();
        if (Serial.available() > 0) buf[index] = Serial.read();
        delay(3);
        // 受信したjsonが終了したらmotorInputを更新
        if(buf[index]=='}'){
            DeserializationError ret = deserializeJson(doc_r, buf);
            motorInput = doc_r["mI"].as<int>();
            Serial.println(motorInput);

            // motorInputをエコーバックする
            sendData("mI", motorInput);

            // doc_r, buf, indexを初期化
            doc_r.clear();
            memset(buf, '\0', BUFFER_SIZE);
            index = 0;
            break;
        }
        if (index > BUFFER_SIZE - 1) {
            // doc_r, buf, indexを初期化
            doc_r.clear();
            memset(buf, '\0', BUFFER_SIZE);
            index = 0;
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

void Train::sendData(String key, int value) {
    String send_data="";
    doc_s.clear();
    doc_s[key]=value;
    serializeJson(doc_s,send_data);
    SerialBT.println(send_data);
    delay(1);
    Serial.println(send_data);
}