// #include "PositionID_Detector.h"

// PositionID_Detector::PositionID_Detector()
// : 	positionID(0)
// {}

// void PositionID_Detector::MFRC522Setup() {
//     SPI.begin();			// Init SPI bus
// 	mfrc522.PCD_Init();		// Init MFRC522
// 	delay(4);				// Optional delay. Some board do need more time after init to be ready, see Readme
// 	mfrc522.PCD_DumpVersionToSerial();	// Show details of PCD - MFRC522 Card Reader details
// 	Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
// }

// int PositionID_Detector::getPositionID() {
//     // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
// 	if ( ! mfrc522.PICC_IsNewCardPresent()) return -1;

// 	// Select one of the cards
// 	if ( ! mfrc522.PICC_ReadCardSerial()) return -1;
	
// 	positionID = mfrc522.uid.uidByte[0]; //UIDの最初の1バイトをPositionIDとする
// 	Serial.print("PositionID: ");
// 	Serial.println(positionID);

// 	mfrc522.PICC_HaltA(); // 卡片進入停止模式

//     return positionID;
// }