/* train.inoで使用する変数・関数を定義する */

#include <BluetoothSerial.h>
#include <ArduinoJson.h>
BluetoothSerial SerialBT;

#include "GetStopping.h"
#include "GetWheelSpeed.h"
// #include "GetPositionID.h"
#include "GetPositionID_Photo.h"

#define BUFFER_SIZE 32

class Train : public GetStopping, public GetWheelSpeed, public GetPositionID_Photo
{
    public:
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
        float   calcWheelRotation(float wheelSpeed, bool isStopping);
        void    sendWheelRotation(float wheelRotation);
        void    sendPositionID(int positionID);
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
        delay(2);
        // 受信したjsonが終了したらmotorInputを更新
        if(buf[index]=='}'){
            deserializeJson(doc_r, buf);
            motorInput = doc_r["motorInput"].as<int>();
            Serial.println(motorInput);

            // motorInputをエコーバックする
            String send_data="";
            doc_s.clear();
            doc_s["motorInput"] = motorInput;
            serializeJson(doc_s,send_data);
            SerialBT.println(send_data);
            delay(100);

            // doc_r, buf, indexを初期化
            doc_r.clear();
            memset(buf, '\0', BUFFER_SIZE);
            index = 0;
            delay(300);
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

float Train::calcWheelRotation(float wheelSpeed, bool isStopping) {

    float wheelRotation;

    if (isStopping) {
        return 0;
    }
    else {
        /* wheelSpeedを時間積分 */
        return wheelRotation;
    }
}

void Train::sendWheelRotation(float wheelRotation) {
    SerialBT.print("{\"wheelRotation\":");
    SerialBT.print(wheelRotation);
    SerialBT.println("}");
}

void Train::sendPositionID(int positionID) {
    SerialBT.print("{\"positionID\":");
    SerialBT.print(positionID);
    SerialBT.println("}");
}