#include <Arduino.h>
#include "MFRC522Uart.h"

/////////////////////////////////////////////////////////////////////////////////////
// Functions for setting up the Arduino
/////////////////////////////////////////////////////////////////////////////////////
/**
 * @brief Constructor. Prepares the output pins.
 */
MFRC522Uart::MFRC522Uart(HardwareSerial* serial,
                         byte mfrc522RxPin,
                         byte mfrc522TxPin,
                         byte resetPowerDownPin) {
    _Serial = serial;
    _Serial->begin(9600, SERIAL_8N1, mfrc522TxPin, mfrc522RxPin);
    _Serial->setTimeout(1000);
    _resetPowerDownPin = resetPowerDownPin;
}

/////////////////////////////////////////////////////////////////////////////////////
// Basic interface functions for communicating with the MFRC522
/////////////////////////////////////////////////////////////////////////////////////

/**
 * @brief Writes a byte to the specified register in the MFRC522 chip.
 * The interface is described in the datasheet section 8.1.3.
 * @param reg   The register to write to. One of the PCD_Register enums.
 * @param value	The value to write.
 */
void MFRC522Uart::PCD_WriteRegister(PCD_Register reg, byte value) {
    _Serial->write(reg & 0x3f);  // Send A0-A5. Datasheet section 8.1.3.3.
    _Serial->write(value);
    _Serial->flush();
    int a;
    while ((a = _Serial->read()) != (reg & 0x3f)) {  // confirm response
        delay(1);
    }
    // byte returnedAddr = 255;
    // _Serial->readBytes(&returnedAddr, 1);  // confirm response
    // Serial.print("[PCD_WriteRegister] wrote ");
    // Serial.println(returnedAddr);
}

/**
 * @brief Writes a number of bytes to the specified register in the MFRC522 chip.
 * The interface is described in the datasheet section 8.1.2.
 * @param reg    The register to write to. One of the PCD_Register enums.
 * @param count  The number of bytes to write to the register
 * @param values The values to write. Byte array.
 */
void MFRC522Uart::PCD_WriteRegister(PCD_Register reg, byte count, byte *values) {
    for (byte index = 0; index < count; index++) {
        _Serial->write(reg & 0x3f);  // Send A0-A5. Datasheet section 8.1.3.3.
        _Serial->write(values[index]);
        _Serial->flush();
        int a;
        while ((a = _Serial->read()) != (reg & 0x3f)) {  // confirm response
            delay(1);
        }
        // byte returnedAddr = 255;
        // _Serial->readBytes(&returnedAddr, 1);  // confirm response
        // Serial.print("[PCD_WriteRegister] wrote ");
        // Serial.print(returnedAddr);
        // Serial.print(" ");
        // Serial.print(index);
        // Serial.print(" of ");
        // Serial.println(count);
    }
}

/**
 * @brief Reads a byte from the specified register in the MFRC522 chip.
 * The interface is described in the datasheet section 8.1.3.
 * @param reg The register to read from. One of the PCD_Register enums.
 * 
 * @return The data read from MFRC522 chip.
 */
byte MFRC522Uart::PCD_ReadRegister(PCD_Register reg) {
    _Serial->write(reg | 0x80);  // MSB == 1 is for reading. Datasheet section 8.1.3.3.
    _Serial->flush();            // Wait until all bits are transmitted.
    byte value = 255;
    _Serial->readBytes(&value, 1);
    return value;
}

/**
 * @brief Reads a number of bytes from the specified register in the MFRC522 chip.
 * The interface is described in the datasheet section 8.1.2.
 * @param reg     The register to read from. One of the PCD_Register enums.
 * @param count   The number of bytes to read
 * @param values  Byte array to store the values in.
 * @param rxAlign Only bit positions rxAlign..7 in values[0] are updated.
 */
void MFRC522Uart::PCD_ReadRegister(PCD_Register reg, byte count, byte *values, byte rxAlign) {
    if (count == 0) {
        return;
    }
    //Serial.print(F("Reading ")); 	Serial.print(count); Serial.println(F(" bytes from register."));
    byte address = 0x80 | reg;  // MSB == 1 is for reading. LSB is not used in address. Datasheet section 8.1.2.3.
    byte index = 0;             // Index in values array.
    count--;                    // One read is performed outside of the loop
    _Serial->write(address);    // Tell MFRC522 which address we want to read
    _Serial->flush();           // Wait until all bits are transmitted.
    if (rxAlign) {		// Only update bit positions rxAlign..7 in values[0]
        // Create bit mask for bit positions rxAlign..7
        byte mask = (0xFF << rxAlign) & 0xFF;
        // Read value and tell that we want to read the same address again.
        byte value = 255;
        _Serial->readBytes(&value, 1);
        _Serial->write(address);
        _Serial->flush();           // Wait until all bits are transmitted.
        // Apply mask to both current value of values[0] and the new data in value.
        values[0] = (values[0] & ~mask) | (value & mask);
        index++;
    }
    while (index < count) {
        _Serial->readBytes(&values[index], 1);
        _Serial->write(address);
        _Serial->flush();           // Wait until all bits are transmitted.
        index++;
    }
    values[index] = _Serial->readBytes(&values[index], 1);  // Read the final byte. Not send address to quit
}

/**
 * @brief Sets the bits given in mask in register reg.
 * @param ref The register to update. One of the PCD_Register enums.
 * @param mask The bits to set.
 */
void MFRC522Uart::PCD_SetRegisterBitMask(PCD_Register reg, byte mask) { 
    byte tmp;
    tmp = PCD_ReadRegister(reg);
    PCD_WriteRegister(reg, tmp | mask);  // set bit mask
}

/**
 * @brief Clears the bits given in mask from register reg.
 * @param ref The register to update. One of the PCD_Register enums.
 * @param mask The bits to clear.
 */
void MFRC522Uart::PCD_ClearRegisterBitMask(PCD_Register reg, byte mask) {
    byte tmp;
    tmp = PCD_ReadRegister(reg);
    PCD_WriteRegister(reg, tmp & (~mask));  // clear bit mask
}

/**
 * @brief Use the CRC coprocessor in the MFRC522 to calculate a CRC_A.
 * @param[in]  data   Pointer to the data to transfer to the FIFO for CRC calculation.
 * @param[in]  length The number of bytes to transfer.
 * @param[out] result Pointer to result buffer. Result is written to result[0..1], low byte first.
 * 
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */
MFRC522Uart::StatusCode MFRC522Uart::PCD_CalculateCRC(byte *data, byte length, byte *result) {
    PCD_WriteRegister(CommandReg, PCD_Idle);		// Stop any active command.
    PCD_WriteRegister(DivIrqReg, 0x04);				// Clear the CRCIRq interrupt request bit
    PCD_WriteRegister(FIFOLevelReg, 0x80);			// FlushBuffer = 1, FIFO initialization
    PCD_WriteRegister(FIFODataReg, length, data);	// Write data to the FIFO
    PCD_WriteRegister(CommandReg, PCD_CalcCRC);		// Start the calculation
    
    // Wait for the CRC calculation to complete. Check for the register to
    // indicate that the CRC calculation is complete in a loop. If the
    // calculation is not indicated as complete in ~90ms, then time out
    // the operation.
    const uint32_t deadline = millis() + 89;

    do {
        // DivIrqReg[7..0] bits are: Set2 reserved reserved MfinActIRq reserved CRCIRq reserved reserved
        byte n = PCD_ReadRegister(DivIrqReg);
        if (n & 0x04) {									// CRCIRq bit set - calculation done
            PCD_WriteRegister(CommandReg, PCD_Idle);	// Stop calculating CRC for new content in the FIFO.
            // Transfer the result from the registers to the result buffer
            result[0] = PCD_ReadRegister(CRCResultRegL);
            result[1] = PCD_ReadRegister(CRCResultRegH);
            return STATUS_OK;
        }
        yield();
    }
    while (static_cast<uint32_t> (millis()) < deadline);

    // 89ms passed and nothing happened. Communication with the MFRC522 might be down.
    return STATUS_TIMEOUT;
}


/////////////////////////////////////////////////////////////////////////////////////
// Functions for manipulating the MFRC522
/////////////////////////////////////////////////////////////////////////////////////

/**
 * @brief Initializes the MFRC522 chip.
 */
void MFRC522Uart::PCD_Init() {
    pinMode(_resetPowerDownPin, OUTPUT);     // Now set the resetPowerDownPin as digital output.
    digitalWrite(_resetPowerDownPin, LOW);   // Make sure we have a clean LOW state.
    delayMicroseconds(2);				     // 8.8.1 Reset timing requirements says about 100ns. Let us be generous: 2μsl
    digitalWrite(_resetPowerDownPin, HIGH);  // Exit power down mode. This triggers a hard reset.
    // Section 8.8.2 in the datasheet says the oscillator start-up time is the start up time of the crystal + 37,74μs. Let us be generous: 50ms.
    delay(50);
    
    // Reset baud rates
    PCD_WriteRegister(TxModeReg, 0x00);
    PCD_WriteRegister(RxModeReg, 0x00);
    // Reset ModWidthReg
    PCD_WriteRegister(ModWidthReg, 0x26);

    // When communicating with a PICC we need a timeout if something goes wrong.
    // f_timer = 13.56 MHz / (2*TPreScaler+1) where TPreScaler = [TPrescaler_Hi:TPrescaler_Lo].
    // TPrescaler_Hi are the four low bits in TModeReg. TPrescaler_Lo is TPrescalerReg.
    PCD_WriteRegister(TModeReg, 0x80);			// TAuto=1; timer starts automatically at the end of the transmission in all communication modes at all speeds
    PCD_WriteRegister(TPrescalerReg, 0xA9);		// TPreScaler = TModeReg[3..0]:TPrescalerReg, ie 0x0A9 = 169 => f_timer=40kHz, ie a timer period of 25μs.
    PCD_WriteRegister(TReloadRegH, 0x03);		// Reload timer with 0x3E8 = 1000, ie 25ms before timeout.
    PCD_WriteRegister(TReloadRegL, 0xE8);
    
    PCD_WriteRegister(TxASKReg, 0x40);		// Default 0x00. Force a 100 % ASK modulation independent of the ModGsPReg register setting
    PCD_WriteRegister(ModeReg, 0x3D);		// Default 0x3F. Set the preset value for the CRC coprocessor for the CalcCRC command to 0x6363 (ISO 14443-3 part 6.2.4)
    PCD_AntennaOn();						// Enable the antenna driver pins TX1 and TX2 (they were disabled by the reset)
}

/**
 * @brief Performs a soft reset on the MFRC522 chip and waits for it to be ready again.
 */
void MFRC522Uart::PCD_Reset() {
    PCD_WriteRegister(CommandReg, PCD_SoftReset);	// Issue the SoftReset command.
    // The datasheet does not mention how long the SoftRest command takes to complete.
    // But the MFRC522 might have been in soft power-down mode (triggered by bit 4 of CommandReg) 
    // Section 8.8.2 in the datasheet says the oscillator start-up time is the start up time of the crystal + 37,74μs. Let us be generous: 50ms.
    uint8_t count = 0;
    do {
        // Wait for the PowerDown bit in CommandReg to be cleared (max 3x50ms)
        delay(50);
    } while ((PCD_ReadRegister(CommandReg) & (1 << 4)) && (++count) < 3);
}

/**
 * @brief Turns the antenna on by enabling pins TX1 and TX2.
 * After a reset these pins are disabled.
 */
void MFRC522Uart::PCD_AntennaOn() {
    byte value = PCD_ReadRegister(TxControlReg);
    if ((value & 0x03) != 0x03) {
        PCD_WriteRegister(TxControlReg, value | 0x03);
    }
}

/**
 * @brief Turns the antenna off by disabling pins TX1 and TX2.
 */
void MFRC522Uart::PCD_AntennaOff() {
    PCD_ClearRegisterBitMask(TxControlReg, 0x03);
}


/////////////////////////////////////////////////////////////////////////////////////
// Functions for communicating with PICCs
/////////////////////////////////////////////////////////////////////////////////////

/**
 * @brief Executes the Transceive command.
 * CRC validation can only be done if backData and backLen are specified.
 * @param sendData Pointer to the data to transfer to the FIFO.
 * @param sendLen  Number of bytes to transfer to the FIFO.
 * @param backData nullptr or pointer to buffer if data should be read back after executing the command.
 * @param backLen  In: Max number of bytes to write to *backData. Out: The number of bytes returned.
 * @param validBit In/Out: The number of valid bits in the last byte. 0 for 8 valid bits. Default nullptr.
 * @param rxAlign  In: Defines the bit position in backData[0] for the first bit received. Default 0.
 * @param checkCRC In: True => The last two bytes of the response is assumed to be a CRC_A that must be validated.
 *							 
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */
MFRC522Uart::StatusCode MFRC522Uart::PCD_TransceiveData(byte *sendData,
                                                        byte sendLen,
                                                        byte *backData,
                                                        byte *backLen,
                                                        byte *validBits,
                                                        byte rxAlign,
                                                        bool checkCRC) {
    byte waitIRq = 0x30;		// RxIRq and IdleIRq
    return PCD_CommunicateWithPICC(PCD_Transceive, waitIRq, sendData, sendLen, backData, backLen, validBits, rxAlign, checkCRC);
} // End PCD_TransceiveData()

/**
 * @brief Transfers data to the MFRC522 FIFO, executes a command, waits for completion and transfers data back from the FIFO.
 * CRC validation can only be done if backData and backLen are specified.
 * @param command  The command to execute. One of the PCD_Command enums.
 * @param waitIRq  The bits in the ComIrqReg register that signals successful completion of the command.
 * @param sendData Pointer to the data to transfer to the FIFO.
 * @param sendLen  Number of bytes to transfer to the FIFO.
 * @param backData nullptr or pointer to buffer if data should be read back after executing the command.
 * @param backLen  In: Max number of bytes to write to *backData. Out: The number of bytes returned.
 * @param validBit In/Out: The number of valid bits in the last byte. 0 for 8 valid bits.
 * @param rxAlign  In: Defines the bit position in backData[0] for the first bit received. Default 0.
 * @param checkCRC In: True => The last two bytes of the response is assumed to be a CRC_A that must be validated.					 
 *
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */
MFRC522Uart::StatusCode MFRC522Uart::PCD_CommunicateWithPICC(byte command,
                                                             byte waitIRq,
                                                             byte *sendData,
                                                             byte sendLen,
                                                             byte *backData,
                                                             byte *backLen,
                                                             byte *validBits,
                                                             byte rxAlign,
                                                             bool checkCRC) {
    // Prepare values for BitFramingReg
    byte txLastBits = validBits ? *validBits : 0;
    byte bitFraming = (rxAlign << 4) + txLastBits;		// RxAlign = BitFramingReg[6..4]. TxLastBits = BitFramingReg[2..0]
    
    PCD_WriteRegister(CommandReg, PCD_Idle);			// Stop any active command.
    PCD_WriteRegister(ComIrqReg, 0x7F);					// Clear all seven interrupt request bits
    PCD_WriteRegister(FIFOLevelReg, 0x80);				// FlushBuffer = 1, FIFO initialization
    PCD_WriteRegister(FIFODataReg, sendLen, sendData);	// Write sendData to the FIFO
    PCD_WriteRegister(BitFramingReg, bitFraming);		// Bit adjustments
    PCD_WriteRegister(CommandReg, command);				// Execute the command
    if (command == PCD_Transceive) {
        PCD_SetRegisterBitMask(BitFramingReg, 0x80);	// StartSend=1, transmission of data starts
    }
    
    // In PCD_Init() we set the TAuto flag in TModeReg. This means the timer
    // automatically starts when the PCD stops transmitting.
    //
    // Wait here for the command to complete. The bits specified in the
    // `waitIRq` parameter define what bits constitute a completed command.
    // When they are set in the ComIrqReg register, then the command is
    // considered complete. If the command is not indicated as complete in
    // ~36ms, then consider the command as timed out.
    const uint32_t deadline = millis() + 36;
    bool completed = false;

    do {
        byte n = PCD_ReadRegister(ComIrqReg);	// ComIrqReg[7..0] bits are: Set1 TxIRq RxIRq IdleIRq HiAlertIRq LoAlertIRq ErrIRq TimerIRq
        if (n & waitIRq) {					// One of the interrupts that signal success has been set.
            completed = true;
            break;
        }
        if (n & 0x01) {						// Timer interrupt - nothing received in 25ms
            return STATUS_TIMEOUT;
        }
        yield();
    }
    while (static_cast<uint32_t> (millis()) < deadline);

    // 36ms and nothing happened. Communication with the MFRC522 might be down.
    if (!completed) {
        return STATUS_TIMEOUT;
    }
    
    // Stop now if any errors except collisions were detected.
    byte errorRegValue = PCD_ReadRegister(ErrorReg); // ErrorReg[7..0] bits are: WrErr TempErr reserved BufferOvfl CollErr CRCErr ParityErr ProtocolErr
    if (errorRegValue & 0x13) {	 // BufferOvfl ParityErr ProtocolErr
        return STATUS_ERROR;
    }
  
    byte _validBits = 0;
    
    // If the caller wants data back, get it from the MFRC522.
    if (backData && backLen) {
        byte n = PCD_ReadRegister(FIFOLevelReg);	// Number of bytes in the FIFO
        if (n > *backLen) {
            return STATUS_NO_ROOM;
        }
        *backLen = n;											// Number of bytes returned
        PCD_ReadRegister(FIFODataReg, n, backData, rxAlign);	// Get received data from FIFO
        _validBits = PCD_ReadRegister(ControlReg) & 0x07;		// RxLastBits[2:0] indicates the number of valid bits in the last received byte. If this value is 000b, the whole byte is valid.
        if (validBits) {
            *validBits = _validBits;
        }
    }
    
    // Tell about collisions
    if (errorRegValue & 0x08) {		// CollErr
        return STATUS_COLLISION;
    }
    
    // Perform CRC_A validation if requested.
    if (backData && backLen && checkCRC) {
        // In this case a MIFARE Classic NAK is not OK.
        if (*backLen == 1 && _validBits == 4) {
            return STATUS_MIFARE_NACK;
        }
        // We need at least the CRC_A value and all 8 bits of the last byte must be received.
        if (*backLen < 2 || _validBits != 0) {
            return STATUS_CRC_WRONG;
        }
        // Verify CRC_A - do our own calculation and store the control in controlBuffer.
        byte controlBuffer[2];
        MFRC522Uart::StatusCode status = PCD_CalculateCRC(&backData[0], *backLen - 2, &controlBuffer[0]);
        if (status != STATUS_OK) {
            return status;
        }
        if ((backData[*backLen - 2] != controlBuffer[0]) || (backData[*backLen - 1] != controlBuffer[1])) {
            return STATUS_CRC_WRONG;
        }
    }
    
    return STATUS_OK;
} // End PCD_CommunicateWithPICC()


/**
 * @brief Transmits a REQuest command, Type A. Invites PICCs in state IDLE to go to READY and prepare for anticollision or selection. 7 bit frame.
 * Beware: When two PICCs are in the field at the same time I often get STATUS_TIMEOUT - probably due do bad antenna design.
 * @param bufferATQA The buffer to store the ATQA (Answer to request) in
 * @param bufferSize Buffer size, at least two bytes. Also number of bytes returned if STATUS_OK.
 * 
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */
MFRC522Uart::StatusCode MFRC522Uart::PICC_RequestA(byte *bufferATQA, byte *bufferSize) {
    return PICC_REQA_or_WUPA(PICC_CMD_REQA, bufferATQA, bufferSize);
}

/**
 * @brief Transmits a Wake-UP command, Type A. Invites PICCs in state IDLE and HALT to go to READY(*) and prepare for anticollision or selection. 7 bit frame.
 * Beware: When two PICCs are in the field at the same time I often get STATUS_TIMEOUT - probably due do bad antenna design.
 * @param bufferATQA The buffer to store the ATQA (Answer to request) in
 * @param bufferSize Buffer size, at least two bytes. Also number of bytes returned if STATUS_OK.
 * 
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */
MFRC522Uart::StatusCode MFRC522Uart::PICC_WakeupA(byte *bufferATQA, byte *bufferSize) {
    return PICC_REQA_or_WUPA(PICC_CMD_WUPA, bufferATQA, bufferSize);
}

/**
 * @brief Transmits REQA or WUPA commands.
 * Beware: When two PICCs are in the field at the same time I often get STATUS_TIMEOUT - probably due do bad antenna design.
 * @param command The command to send - PICC_CMD_REQA or PICC_CMD_WUPA
 * @param bufferATQA The buffer to store the ATQA (Answer to request) in
 * @param bufferSize Buffer size, at least two bytes. Also number of bytes returned if STATUS_OK.
 * 
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */ 
MFRC522Uart::StatusCode MFRC522Uart::PICC_REQA_or_WUPA(byte command, byte *bufferATQA, byte *bufferSize) {
    byte validBits;
    MFRC522Uart::StatusCode status;
    
    if (bufferATQA == nullptr || *bufferSize < 2) {	// The ATQA response is 2 bytes long.
        return STATUS_NO_ROOM;
    }
    PCD_ClearRegisterBitMask(CollReg, 0x80);		// ValuesAfterColl=1 => Bits received after collision are cleared.
    validBits = 7;									// For REQA and WUPA we need the short frame format - transmit only 7 bits of the last (and only) byte. TxLastBits = BitFramingReg[2..0]
    status = PCD_TransceiveData(&command, 1, bufferATQA, bufferSize, &validBits);
    if (status != STATUS_OK) {
        return status;
    }
    if (*bufferSize != 2 || validBits != 0) {		// ATQA must be exactly 16 bits.
        return STATUS_ERROR;
    }
    return STATUS_OK;
}

/**
 * @brief Transmits SELECT/ANTICOLLISION commands to select a single PICC.
 * Before calling this function the PICCs must be placed in the READY(*) state by calling PICC_RequestA() or PICC_WakeupA().
 * On success:
 * 		- The chosen PICC is in state ACTIVE(*) and all other PICCs have returned to state IDLE/HALT. (Figure 7 of the ISO/IEC 14443-3 draft.)
 * 		- The UID size and value of the chosen PICC is returned in *uid along with the SAK.
 * 
 * A PICC UID consists of 4, 7 or 10 bytes.
 * Only 4 bytes can be specified in a SELECT command, so for the longer UIDs two or three iterations are used:
 * 		UID size	Number of UID bytes		Cascade levels		Example of PICC
 * 		========	===================		==============		===============
 * 		single				 4						1				MIFARE Classic
 * 		double				 7						2				MIFARE Ultralight
 * 		triple				10						3				Not currently in use?
 * @param uid Pointer to Uid struct. Normally output, but can also be used to supply a known UID.
 * @param validBits The number of known UID bits supplied in *uid. Normally 0. If set you must also supply uid->size.
 * 
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */
MFRC522Uart::StatusCode MFRC522Uart::PICC_Select(Uid *uid, byte validBits) {
    bool uidComplete;
    bool selectDone;
    bool useCascadeTag;
    byte cascadeLevel = 1;
    MFRC522Uart::StatusCode result;
    byte count;
    byte checkBit;
    byte index;
    byte uidIndex;					// The first index in uid->uidByte[] that is used in the current Cascade Level.
    int8_t currentLevelKnownBits;		// The number of known UID bits in the current Cascade Level.
    byte buffer[9] = {0,0,0,0,0,0,0,0,0};	// The SELECT/ANTICOLLISION commands uses a 7 byte standard frame + 2 bytes CRC_A
    byte bufferUsed;				// The number of bytes used in the buffer, ie the number of bytes to transfer to the FIFO.
    byte rxAlign;					// Used in BitFramingReg. Defines the bit position for the first bit received.
    byte txLastBits;				// Used in BitFramingReg. The number of valid bits in the last transmitted byte. 
    byte *responseBuffer;
    byte responseLength;
    
    // Description of buffer structure:
    //		Byte 0: SEL 				Indicates the Cascade Level: PICC_CMD_SEL_CL1, PICC_CMD_SEL_CL2 or PICC_CMD_SEL_CL3
    //		Byte 1: NVB					Number of Valid Bits (in complete command, not just the UID): High nibble: complete bytes, Low nibble: Extra bits. 
    //		Byte 2: UID-data or CT		See explanation below. CT means Cascade Tag.
    //		Byte 3: UID-data
    //		Byte 4: UID-data
    //		Byte 5: UID-data
    //		Byte 6: BCC					Block Check Character - XOR of bytes 2-5
    //		Byte 7: CRC_A
    //		Byte 8: CRC_A
    // The BCC and CRC_A are only transmitted if we know all the UID bits of the current Cascade Level.
    //
    // Description of bytes 2-5: (Section 6.5.4 of the ISO/IEC 14443-3 draft: UID contents and cascade levels)
    //		UID size	Cascade level	Byte2	Byte3	Byte4	Byte5
    //		========	=============	=====	=====	=====	=====
    //		 4 bytes		1			uid0	uid1	uid2	uid3
    //		 7 bytes		1			CT		uid0	uid1	uid2
    //						2			uid3	uid4	uid5	uid6
    //		10 bytes		1			CT		uid0	uid1	uid2
    //						2			CT		uid3	uid4	uid5
    //						3			uid6	uid7	uid8	uid9
    
    // Sanity checks
    if (validBits > 80) {
        return STATUS_INVALID;
    }
    
    // Prepare MFRC522
    PCD_ClearRegisterBitMask(CollReg, 0x80);		// ValuesAfterColl=1 => Bits received after collision are cleared.
    
    // Repeat Cascade Level loop until we have a complete UID.
    uidComplete = false;
    while (!uidComplete) {
        // Set the Cascade Level in the SEL byte, find out if we need to use the Cascade Tag in byte 2.
        switch (cascadeLevel) {
            case 1:
                buffer[0] = PICC_CMD_SEL_CL1;
                uidIndex = 0;
                useCascadeTag = validBits && uid->size > 4;	// When we know that the UID has more than 4 bytes
                break;
            
            case 2:
                buffer[0] = PICC_CMD_SEL_CL2;
                uidIndex = 3;
                useCascadeTag = validBits && uid->size > 7;	// When we know that the UID has more than 7 bytes
                break;
            
            case 3:
                buffer[0] = PICC_CMD_SEL_CL3;
                uidIndex = 6;
                useCascadeTag = false;						// Never used in CL3.
                break;
            
            default:
                return STATUS_INTERNAL_ERROR;
                break;
        }
        
        // How many UID bits are known in this Cascade Level?
        currentLevelKnownBits = validBits - (8 * uidIndex);
        if (currentLevelKnownBits < 0) {
            currentLevelKnownBits = 0;
        }
        // Copy the known bits from uid->uidByte[] to buffer[]
        index = 2; // destination index in buffer[]
        if (useCascadeTag) {
            buffer[index++] = PICC_CMD_CT;
        }
        byte bytesToCopy = currentLevelKnownBits / 8 + (currentLevelKnownBits % 8 ? 1 : 0); // The number of bytes needed to represent the known bits for this level.
        if (bytesToCopy) {
            byte maxBytes = useCascadeTag ? 3 : 4; // Max 4 bytes in each Cascade Level. Only 3 left if we use the Cascade Tag
            if (bytesToCopy > maxBytes) {
                bytesToCopy = maxBytes;
            }
            for (count = 0; count < bytesToCopy; count++) {
                buffer[index++] = uid->uidByte[uidIndex + count];
            }
        }
        // Now that the data has been copied we need to include the 8 bits in CT in currentLevelKnownBits
        if (useCascadeTag) {
            currentLevelKnownBits += 8;
        }
        
        // Repeat anti collision loop until we can transmit all UID bits + BCC and receive a SAK - max 32 iterations.
        selectDone = false;
        while (!selectDone) {
            // Find out how many bits and bytes to send and receive.
            if (currentLevelKnownBits >= 32) { // All UID bits in this Cascade Level are known. This is a SELECT.
                //Serial.print(F("SELECT: currentLevelKnownBits=")); Serial.println(currentLevelKnownBits, DEC);
                buffer[1] = 0x70; // NVB - Number of Valid Bits: Seven whole bytes
                // Calculate BCC - Block Check Character
                buffer[6] = buffer[2] ^ buffer[3] ^ buffer[4] ^ buffer[5];
                // Calculate CRC_A
                result = PCD_CalculateCRC(buffer, 7, &buffer[7]);
                if (result != STATUS_OK) {
                    return result;
                }
                txLastBits		= 0; // 0 => All 8 bits are valid.
                bufferUsed		= 9;
                // Store response in the last 3 bytes of buffer (BCC and CRC_A - not needed after tx)
                responseBuffer	= &buffer[6];
                responseLength	= 3;
            }
            else { // This is an ANTICOLLISION.
                //Serial.print(F("ANTICOLLISION: currentLevelKnownBits=")); Serial.println(currentLevelKnownBits, DEC);
                txLastBits		= currentLevelKnownBits % 8;
                count			= currentLevelKnownBits / 8;	// Number of whole bytes in the UID part.
                index			= 2 + count;					// Number of whole bytes: SEL + NVB + UIDs
                buffer[1]		= (index << 4) + txLastBits;	// NVB - Number of Valid Bits
                bufferUsed		= index + (txLastBits ? 1 : 0);
                // Store response in the unused part of buffer
                responseBuffer	= &buffer[index];
                responseLength	= sizeof(buffer) - index;
            }
            
            // Set bit adjustments
            rxAlign = txLastBits;											// Having a separate variable is overkill. But it makes the next line easier to read.
            PCD_WriteRegister(BitFramingReg, (rxAlign << 4) + txLastBits);	// RxAlign = BitFramingReg[6..4]. TxLastBits = BitFramingReg[2..0]
            
            // Transmit the buffer and receive the response.

            // Serial.print("[PICC_Select] buffer (to transmit): ");
			// for (int i = 0; i < 9; i++) {
			// 	Serial.printf("%02x ", buffer[i]);
			// }
			// Serial.println("");

            result = PCD_TransceiveData(buffer, bufferUsed, responseBuffer, &responseLength, &txLastBits, rxAlign);

            // Serial.print("[PICC_Select] buffer (incl response): ");
            // for (int i = 0; i < 9; i++) {
            //     Serial.printf("%02x ", buffer[i]);
            // }
            // Serial.println("");

            if (result == STATUS_COLLISION) { // More than one PICC in the field => collision.
                byte valueOfCollReg = PCD_ReadRegister(CollReg); // CollReg[7..0] bits are: ValuesAfterColl reserved CollPosNotValid CollPos[4:0]
                if (valueOfCollReg & 0x20) { // CollPosNotValid
                    return STATUS_COLLISION; // Without a valid collision position we cannot continue
                }
                byte collisionPos = valueOfCollReg & 0x1F; // Values 0-31, 0 means bit 32.
                if (collisionPos == 0) {
                    collisionPos = 32;
                }
                if (collisionPos <= currentLevelKnownBits) { // No progress - should not happen 
                    return STATUS_INTERNAL_ERROR;
                }
                // Choose the PICC with the bit set.
                currentLevelKnownBits	= collisionPos;
                count			= currentLevelKnownBits % 8; // The bit to modify
                checkBit		= (currentLevelKnownBits - 1) % 8;
                index			= 1 + (currentLevelKnownBits / 8) + (count ? 1 : 0); // First byte is index 0.
                buffer[index]	|= (1 << checkBit);
            }
            else if (result != STATUS_OK) {
                return result;
            }
            else { // STATUS_OK
                if (currentLevelKnownBits >= 32) { // This was a SELECT.
                    selectDone = true; // No more anticollision 
                    // We continue below outside the while.
                }
                else { // This was an ANTICOLLISION.
                    // We now have all 32 bits of the UID in this Cascade Level
                    currentLevelKnownBits = 32;
                    // Run loop again to do the SELECT.
                }
            }
        } // End of while (!selectDone)
        
        // We do not check the CBB - it was constructed by us above.
        
        // Copy the found UID bytes from buffer[] to uid->uidByte[]
        index			= (buffer[2] == PICC_CMD_CT) ? 3 : 2; // source index in buffer[]
        bytesToCopy		= (buffer[2] == PICC_CMD_CT) ? 3 : 4;
        for (count = 0; count < bytesToCopy; count++) {
            uid->uidByte[uidIndex + count] = buffer[index++];
        }
    
        // Check response SAK (Select Acknowledge)
        if (responseLength != 3 || txLastBits != 0) { // SAK must be exactly 24 bits (1 byte + CRC_A).
            return STATUS_ERROR;
        }
        // Verify CRC_A - do our own calculation and store the control in buffer[2..3] - those bytes are not needed anymore.
        result = PCD_CalculateCRC(responseBuffer, 1, &buffer[2]);
        if (result != STATUS_OK) {
            return result;
        }

        // Serial.print("[PICC_Select] buffer (after CalcCRC): ");
        // for (int i = 0; i < bufferUsed; i++) {
        //     Serial.printf("%02x ", buffer[i]);
        // }
        // Serial.println("");

        // FIXME: Somewhat, CRC check failed because we always receive wrong CRC from card.
        //        So we commented out the check.
        //        We aren't sure whether the problem is on the card or receiving protocol or hardware.

        // if ((buffer[2] != responseBuffer[1]) || (buffer[3] != responseBuffer[2])) {
        //     return STATUS_CRC_WRONG;
        // }
        if (responseBuffer[0] & 0x04) { // Cascade bit set - UID not complete yes
            cascadeLevel++;
        }
        else {
            uidComplete = true;
            uid->sak = responseBuffer[0];
        }
    } // End of while (!uidComplete)
    
    // Set correct uid->size
    uid->size = 3 * cascadeLevel + 1;

    return STATUS_OK;
}

/**
 * @brief Instructs a PICC in state ACTIVE(*) to go to state HALT.
 *
 * @return STATUS_OK on success, STATUS_??? otherwise.
 */ 
MFRC522Uart::StatusCode MFRC522Uart::PICC_HaltA() {
    MFRC522Uart::StatusCode result;
    byte buffer[4];
    
    // Build command buffer
    buffer[0] = PICC_CMD_HLTA;
    buffer[1] = 0;
    // Calculate CRC_A
    result = PCD_CalculateCRC(buffer, 2, &buffer[2]);
    if (result != STATUS_OK) {
        return result;
    }
    
    // Send the command.
    // The standard says:
    //		If the PICC responds with any modulation during a period of 1 ms after the end of the frame containing the
    //		HLTA command, this response shall be interpreted as 'not acknowledge'.
    // We interpret that this way: Only STATUS_TIMEOUT is a success.
    result = PCD_TransceiveData(buffer, sizeof(buffer), nullptr, 0);
    if (result == STATUS_TIMEOUT) {
        return STATUS_OK;
    }
    if (result == STATUS_OK) { // That is ironically NOT ok in this case ;-)
        return STATUS_ERROR;
    }
    return result;
}


/////////////////////////////////////////////////////////////////////////////////////
// Support functions
/////////////////////////////////////////////////////////////////////////////////////

/**
 * @brief Dumps debug info about the connected PCD to Serial.
 * Shows all known firmware versions
 */
void MFRC522Uart::PCD_DumpVersionToSerial() {
    // Get the MFRC522 firmware version
    byte v = PCD_ReadRegister(VersionReg);
    Serial.print(F("Firmware Version: 0x"));
    Serial.print(v, HEX);
    // Lookup which version
    switch(v) {
        case 0x88: Serial.println(F(" = (clone)"));  break;
        case 0x90: Serial.println(F(" = v0.0"));     break;
        case 0x91: Serial.println(F(" = v1.0"));     break;
        case 0x92: Serial.println(F(" = v2.0"));     break;
        case 0x12: Serial.println(F(" = counterfeit chip"));     break;
        default:   Serial.println(F(" = (unknown)"));
    }
    // When 0x00 or 0xFF is returned, communication probably failed
    if ((v == 0x00) || (v == 0xFF)) {
        Serial.println(F("WARNING: Communication failure, is the MFRC522 properly connected?"));
    }
}


/////////////////////////////////////////////////////////////////////////////////////
// Convenience functions - does not add extra functionality
/////////////////////////////////////////////////////////////////////////////////////

/**
 * @briefReturns true if a PICC responds to PICC_CMD_REQA.
 * Only "new" cards in state IDLE are invited. Sleeping cards in state HALT are ignored.
 * 
 * @return bool
 */
bool MFRC522Uart::PICC_IsNewCardPresent() {
    byte bufferATQA[2];
    byte bufferSize = sizeof(bufferATQA);

    // Reset baud rates
    PCD_WriteRegister(TxModeReg, 0x00);
    PCD_WriteRegister(RxModeReg, 0x00);
    // Reset ModWidthReg
    PCD_WriteRegister(ModWidthReg, 0x26);

    MFRC522Uart::StatusCode result = PICC_RequestA(bufferATQA, &bufferSize);

    // FIXME: Somewhat, the ATQA is different between from the one aquired by on-the-market modules.
    // Serial.print("[IsNewCardPresent] buffrATQA: ");
    // Serial.print(bufferATQA[0], HEX);
    // Serial.println(bufferATQA[1], HEX);
    // Serial.print("[IsNewCardPresent] result: ");
    // Serial.println(result);
    return (result == STATUS_OK || result == STATUS_COLLISION);
}

/**
 * @brief Simple wrapper around PICC_Select.
 * Returns true if a UID could be read.
 * Remember to call PICC_IsNewCardPresent(), PICC_RequestA() or PICC_WakeupA() first.
 * The read UID is available in the class variable uid.
 * 
 * @return bool
 */
bool MFRC522Uart::PICC_ReadCardSerial() {
    MFRC522Uart::StatusCode result = PICC_Select(&uid);
    return (result == STATUS_OK);
}
