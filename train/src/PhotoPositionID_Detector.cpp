#include "PhotoPositionID_Detector.h"

PhotoPositionID_Detector::PhotoPositionID_Detector() 
: 	SENSOR1_PIN(34),
	SENSOR2_PIN(35),
	WHITE_THRESHOLD1(1300),
	WHITE_THRESHOLD2(1850),
	LEAVE_THRESHOLD(4090),
	TIME_OUT(2500)
{
	this->positionID = 0;
	this->positionID_stored = 0;
	this->sensorValue1 = 0;
	this->sensorValue2 = 0;
	this->sensorValue1_lpf = 0;
	this->sensorValue2_lpf = 0;
	this->detectedColor1 = black;
	this->detectedColor2 = black;
	this->preDetectedColor1 = black;
	this->preDetectedColor2 = black;
	this->bitIndex1 = 0;
	this->bitIndex2 = 0;
	this->bitDetectedTime1 = 0;
	this->bitDetectedTime2 = 0;
	this->nowTime = 0;
}

/* フォトリフクレクタの読み取り値photo_sensor1, photo_sensor2からphotoPositionIDをアップデートする */
void PhotoPositionID_Detector::update(int photo_sensor1, int photo_sensor2, float dt) {

	nowTime = millis();

	positionID = 0;

	setPhotoRefAnalogValue(photo_sensor1, photo_sensor2);

	sensorValue1_lpf = (int)firstLpf1.update((float)sensorValue1, dt);
	sensorValue2_lpf = (int)firstLpf2.update((float)sensorValue2, dt);

	if(sensorValue1 < WHITE_THRESHOLD1){detectedColor1 = white;}
	else{detectedColor1 = black;}

	if(sensorValue2 < WHITE_THRESHOLD2){detectedColor2 = white;}
	else{detectedColor2 = black;}

	// Serial.print("Val1:");
	// Serial.print(sensorValue1);
	// Serial.print(", Val2:");
	// Serial.print(sensorValue2);
	// Serial.print(", Val1_lpf:");
	// Serial.print(sensorValue1_lpf);
	// Serial.print(", Val2_lpf:");
	// Serial.print(sensorValue2_lpf);
	// Serial.print(", Color1:");
	// Serial.print(detectedColor1*1000);
	// Serial.print(", Color2:");
	// Serial.print(detectedColor2*1000);

	// Serial.print(", TOP:");
	// Serial.print("4096");
	// Serial.print(", BOTTOM:");
	// Serial.print("0");
	// Serial.println("");

	measure1Clock2();
	measure2Clock1();

	if (positionID > 0) {
		positionID_stored = positionID;
		
		//Serial.print("PositionID: ");
		//Serial.println(positionID);
	}

	preDetectedColor1 = detectedColor1;
	preDetectedColor2 = detectedColor2;

}

void PhotoPositionID_Detector::photoRefSetup() {
	firstLpf1.setFc(1500.0);  // カットオフ周波数100Hz
	firstLpf2.setFc(1500.0);
	memset(gotData1, '\0', BIT);
	memset(gotData2, '\0', BIT);
	Serial.println("SetupReset");
	resetAll();
}

void PhotoPositionID_Detector::setPhotoRefAnalogValue(int sensorValue1, int sensorValue2) {
	this->sensorValue1 = sensorValue1;
	this->sensorValue2 = sensorValue2;
}

int PhotoPositionID_Detector::getPhotoPositionID() {
    return positionID_stored;
}

void PhotoPositionID_Detector::reset1(){
	bitIndex1 = 0;
	for(int j = 0; j < BIT; j++){
		gotData1[j] = 0;
	}
}

void PhotoPositionID_Detector::reset2(){
	bitIndex2 = 0;
	for(int j = 0; j < BIT; j++){
		gotData2[j] = 0;
	}
}

void PhotoPositionID_Detector::resetAll(){
	reset1();
	reset2();
}

void PhotoPositionID_Detector::measure1Clock2(){
	if(detectedColor2 != preDetectedColor2){
		gotData1[bitIndex1] = detectedColor1;
		//Serial.print(detectedColor1);
		bitIndex1 += 1;
		bitDetectedTime1 = millis();
	}

	if(bitIndex1 >= BIT){
		positionID = 0;
		for(int j = 0; j < BIT; j++){
			positionID += gotData1[BIT - j - 1] * (pow(2, BIT - j - 1) + 0.5);
		}
		Serial.print("PositionID1");
		Serial.println(positionID);
		//Serial.println("GetPositionM1");
		resetAll();
	}

	// if(sensorValue1_lpf > LEAVE_THRESHOLD) {
	// 	//Serial.println("LeaveM1");
	// 	resetAll();
	// }
	if(nowTime - bitDetectedTime1 > TIME_OUT) {
		reset1();
		bitDetectedTime1 = nowTime;
		//Serial.println("TimeoutM1");
	}
}

void PhotoPositionID_Detector::measure2Clock1(){
	if(detectedColor1 != preDetectedColor1){
		gotData2[bitIndex2] = detectedColor2;
		Serial.print(detectedColor2);
		bitIndex2 += 1;
		bitDetectedTime2 = millis();
	}

	if(bitIndex2 >= BIT){
		positionID = 0;
		for(int j = 0; j < BIT; j++){
			positionID += gotData2[j] * (pow(2,j) + 0.5);
		}
		Serial.println("");
		Serial.print("PositionID2:");
		Serial.println(positionID);
		//Serial.println("GetPositionM2");
		resetAll();
	}

	// if(sensorValue2_lpf > LEAVE_THRESHOLD) {
	// 	resetAll();
	// 	Serial.println("");
	// }
	if(nowTime - bitDetectedTime2 > TIME_OUT) {
		reset2();
		bitDetectedTime2 = nowTime;
		Serial.println("");
	}
}