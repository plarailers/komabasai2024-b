#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         27
#define SS_PIN          5
#define MISO_PIN  		19 
#define MOSI_PIN  		23 
#define SCK_PIN   		18 

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

class GetPositionID
{
	private:
		int 	positionID;
    public:
		GetPositionID();
        void    MFRC522Setup(); //RFIDリーダ(MFRC522)
        int     getPositionID();    
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
	mfrc522.PICC_DumpToSerial(&(mfrc522.uid));

    return positionID;
}

