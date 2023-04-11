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

        Train(char* serialBTPortName);
        int     getMotorInput();
        void    moveMotor(int motorInput);
        double  getMovingDistance(double wheelSpeed, bool isStopping);
        void    sendMovingDistance(double movingDistance);
        void    sendPositionID(int positionID);
};

Train::Train(char* serialBTPortName) {
    this->serialSpeed       = 115200;
    this->serialBTPortName  = serialBTPortName;
    this->MOTOR_INPUT_PIN   = A18;
}

int Train::getMotorInput() {

    int MOTOR_INPUT_MAX = 255;  // inputの上限
    int MOTOR_INPUT_MIN = 0;    // inputの下限
    int motorInput;

    while (SerialBT.available() > 0) {
        motorInput = SerialBT.read();
    }
    motorInput = constrain(motorInput, MOTOR_INPUT_MIN, MOTOR_INPUT_MAX);
    return motorInput;
}

void Train::moveMotor(int motorInput) {
    ledcWrite(0, motorInput);
}

double Train::getMovingDistance(double wheelSpeed, bool isStopping) {

    double movingDistance;

    if (isStopping) {
        return 0;
    }
    else {
        /* wheelSpeedを時間積分 */
        return movingDistance;
    }
}

void Train::sendMovingDistance(double movingDistance) {
    SerialBT.print(movingDistance);
}

void Train::sendPositionID(int positionID) {
    SerialBT.print(positionID);
}