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

class PositionID_Detector
{
	private:
		int 				positionID;
		MFRC522 			mfrc522;  // Create MFRC522 instance
		MFRC522::MIFARE_Key key;
		const int 			RST_PIN;
		const int 			SS_PIN;
		const int 			MISO_PIN;  		 
		const int 			MOSI_PIN;  		 
		const int 			SCK_PIN;   		 
		
    public:
		PositionID_Detector();
        void    MFRC522Setup(); //RFIDリーダ(MFRC522)
        int     getPositionID();
		void 	dump_byte_array(byte *buffer, byte bufferSize);
};

