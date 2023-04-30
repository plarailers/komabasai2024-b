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

#define RST_PIN         27
#define SS_PIN          5
#define MISO_PIN  		19 
#define MOSI_PIN  		23 
#define SCK_PIN   		18 

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
MFRC522::MIFARE_Key key;

class GetPositionID
{
	private:
		int 	positionID;
    public:
		GetPositionID();
        void    MFRC522Setup(); //RFIDリーダ(MFRC522)
        int     getPositionID();
		void 	dump_byte_array(byte *buffer, byte bufferSize);
};

GetPositionID::GetPositionID() {
	this->positionID = 0;
}

void GetPositionID::MFRC522Setup() {
    SPI.begin();			// Init SPI bus
	mfrc522.PCD_Init();		// Init MFRC522
	delay(4);				// Optional delay. Some board do need more time after init to be ready, see Readme
	mfrc522.PCD_DumpVersionToSerial();	// Show details of PCD - MFRC522 Card Reader details
	Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
}

int GetPositionID::getPositionID() {
    // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
	if ( ! mfrc522.PICC_IsNewCardPresent()) {
		return -1;
	}

	// Select one of the cards
	if ( ! mfrc522.PICC_ReadCardSerial()) {
		return -1;
	}

	// Dump debug info about the card; PICC_HaltA() is automatically called
	// mfrc522.PICC_DumpToSerial(&(mfrc522.uid));

	// 顯示卡片內容
	// Serial.print(F("Card UID:"));
	// dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size); // 顯示卡片的UID
	// Serial.println();
	
	positionID = mfrc522.uid.uidByte[0]; //UIDの最初の1バイトをPositionIDとする
	Serial.print("PositionID: ");
	Serial.println(positionID);

	mfrc522.PICC_HaltA(); // 卡片進入停止模式

    return positionID;
}

void GetPositionID::dump_byte_array(byte *buffer, byte bufferSize) {
	for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], DEC);
    }
}