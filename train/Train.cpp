#include "Train.h"

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