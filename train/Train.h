/* train.inoで使用する変数・関数を定義する */

#include <BluetoothSerial.h>
BluetoothSerial SerialBT;

#include "GetStopping.h"
#include "GetWheelSpeed.h"
#include "GetPositionID.h"


class Train : public GetStopping, public GetWheelSpeed, public GetPositionID
{
    public:
        int     serialSpeed;
        char*   serialBTPortName;
        int     MOTOR_INPUT_PIN;
        int     motorInput;

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

    int MOTOR_INPUT_MAX = 255;  // inputの上限
    int MOTOR_INPUT_MIN = 0;    // inputの下限

    while (SerialBT.available() > 0) {
        motorInput = SerialBT.read();
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
    SerialBT.print("\"wheelRotation\":");
    SerialBT.print(wheelRotation);
    SerialBT.println("}");
}

void Train::sendPositionID(int positionID) {
    SerialBT.print("{\"positionID\":");
    SerialBT.print(positionID);
    SerialBT.println("}");
}