#include <Arduino.h>

#define BIT 8
#define THRESHOLD1 1100
#define THRESHOLD2 1750
#define THRESHOLDLEAVE 3950
#define THRESHOLDTIME 250

class PhotoPositionID_Detector
{
	private:
		const int SENSOR1_PIN;
		const int SENSOR2_PIN;
		const int WHITE_THRESHOLD1; //これを下回ったら白
		const int WHITE_THRESHOLD2;
		const int LEAVE_THRESHOLD; //これを上回ったら車両が浮いている
		const int TIME_OUT; //最後のビット検出時刻からTIME_OUT以上経ったらリセット
		int positionID;
		int sensorValue1, sensorValue2;
		typedef enum {
			black,
			white,
		} DetectedColor;
		DetectedColor detectedColor1, detectedColor2;
		DetectedColor preDetectedColor1, preDetectedColor2;
		int bitIndex1, bitIndex2;
		int bitDetectedTime1, bitDetectedTime2, nowTime;
		int gotData1[BIT], gotData2[BIT];
		void reset1();
		void reset2();
		void resetAll();
		void measure1Clock2();
		void measure2Clock1();              
    public:
		PhotoPositionID_Detector();
		void update(int, int);
        void photoRefSetup();
		void setPhotoRefAnalogValue(int, int);
        int getPhotoPositionID();
};
