/* train.inoで使用する変数・関数を定義する */

#include <BluetoothSerial.h>
#include <ArduinoJson.h>
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
        PositionID_Detector         positionID_Detector;

        Train(char* serialBTPortName);

        int     getMotorInput();
        void    moveMotor(int motorInput);
        void    sendData(String key, int value);
};