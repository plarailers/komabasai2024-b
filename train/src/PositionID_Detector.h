/* 
	MFRC522 to ESP32 Connections
	===========
	RST 		to 27
	SS(SDA) 	to 5
	MISO		to 19
	MOSI		to 23
	SCK			to 18
	3.3V 		to 3.3V DC
	GND 		to common ground
	=======
	2023-04-16
*/

#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 	27
#define SS_PIN 		5
#define MISO_PIN 	19
#define MOSI_PIN 	23
#define SCK_PIN 	18

class PositionID_Detector
{
	private:
		int 		positionID;  
		MFRC522 	mfrc522{SS_PIN, RST_PIN};  // Create MFRC522 instance
		MFRC522::MIFARE_Key key;
		
    public:
		PositionID_Detector();
        void    MFRC522Setup(); //RFIDリーダ(MFRC522)
        int     getPositionID();
};

