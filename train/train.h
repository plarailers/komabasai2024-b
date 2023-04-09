/* train.inoで使用する関数を定義する */

#include <SPI.h>
#include <MFRC522.h>

#include "getStopping.h"
#include "getWheelSpeed.h"

#define RST_PIN         27         // Configurable, see typical pin layout above
#define SS_PIN          5         // Configurable, see typical pin layout above
#define MISO_PIN  19 
#define MOSI_PIN  23 
#define SCK_PIN   18 

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance


class Train {
    private:
        int     serialSpeed;
        String  serialPortName;
        int     MOTOR_INPUT_PIN;
        int     MOTOR_CURRENT_SENSOR_PIN;
    public:
        void    BNO055Setup();  //加速度センサ(BNP055)
        void    MFRC522Setup(); //RFIDリーダ(MFRC522)
        int     getMotorInput();
        void    moveMotor(int motorInput);
        double  getWheelSpeed(int MOTOR_CURRENT_SENSOR_PIN);
        void    getStopping(void);
        double  getMovingDistance(double wheelSpeed, bool isStopping);
        void    sendMovingDistance(double movingDistance);
        int     getPositionID();
        void    sendPositionID(int positionID);
};

void Train::MFRC522Setup() {
    SPI.begin();			// Init SPI bus
	mfrc522.PCD_Init();		// Init MFRC522
	delay(4);				// Optional delay. Some board do need more time after init to be ready, see Readme
	mfrc522.PCD_DumpVersionToSerial();	// Show details of PCD - MFRC522 Card Reader details
	Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
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

double Train::getMovingDistance(double wheelSpeed, bool isStopping) {
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

int Train::getPositionID() {
    // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
	if ( ! mfrc522.PICC_IsNewCardPresent()) {
		return -1;
	}

	// Select one of the cards
	if ( ! mfrc522.PICC_ReadCardSerial()) {
		return -1;
	}

	// Dump debug info about the card; PICC_HaltA() is automatically called
	mfrc522.PICC_DumpToSerial(&(mfrc522.uid));

    return positionID;
}

void Train::sendPositionID(int positionID) {
    SerialBT.print(positionID);
}

