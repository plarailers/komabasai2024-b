#define BIT 8
#define THRESHOLD1 380
#define THRESHOLD2 300
#define THRESHOLDLEAVE 750
#define THRESHOLDTIME 250

class GetPositionID_Photo
{
	private:
		int positionID;
		int val1, val2, bool1, bool2, bool1_before, bool2_before;
		int i1, i2, time1, time2, nowTime;
		int getData1[BIT], getData2[BIT];
		void reset1();
		void reset2();
		void resetAll();
		void measure1Clock2();
		void measure2Clock1();              
    public:
		GetPositionID_Photo();
        void photoRefSetup();
        int getPositionID_Photo();
};

GetPositionID_Photo::GetPositionID_Photo() {
	this->positionID = 0;
	this->val1 = 0;
	this->val2 = 0;
	this->bool1 = 0;
	this->bool2 = 0;
	this->bool1_before = 0;
	this->bool2_before = 0;
	this->i1 = 0;
	this->i2 = 0;
	this->time1 = 0;
	this->time2 = 0;
	this->nowTime = 0;
}

void GetPositionID_Photo::photoRefSetup() {
	memset(getData1, '\0', BIT);
	memset(getData2, '\0', BIT);
	resetAll();
}

int GetPositionID_Photo::getPositionID_Photo() {
	val1 = analogRead(34);
	val2 = analogRead(35);
	nowTime = millis();

	positionID = 0;

	if(val1 < THRESHOLD1){bool1 = 1;}
	else{bool1 = 0;}

	if(val2 < THRESHOLD2){bool2 = 1;}
	else{bool2 = 0;}

	measure1Clock2();
	measure2Clock1();

	bool1_before = bool1;
	bool2_before = bool2;

	Serial.print("PositionID: ");
	Serial.println(positionID);

    return positionID;
}

void GetPositionID_Photo::reset1(){
	i1 = 0;
	for(int j = 0; j < BIT; j++){
		getData1[j] = 0;
	}	
}

void GetPositionID_Photo::reset2(){
	i2 = 0;
	for(int j = 0; j < BIT; j++){
		getData2[j] = 0;
	}
}

void GetPositionID_Photo::resetAll(){
	reset1();
	reset2();
}

void GetPositionID_Photo::measure1Clock2(){
	if(bool2 != bool2_before){
		getData1[i1] = bool1;
		i1 += 1;
		time1 = millis();
	}

	if(i1 >= BIT){
		positionID = 0;
		for(int j = 0; j < BIT; j++){
			positionID += getData1[BIT - j - 1] * (pow(2, BIT - j - 1) + 0.5);
		}
		resetAll();
	}

	if(val1 > THRESHOLDLEAVE){resetAll();}
	if(nowTime - time1 > THRESHOLDTIME){reset1();}
}

void GetPositionID_Photo::measure2Clock1(){
	if(bool1 != bool1_before){
		getData2[i2] = bool2;
		i2 += 1;
		time2 = millis();
	}

	if(i2 >= BIT){
		positionID = 0;
		for(int j = 0; j < BIT; j++){
			positionID += getData2[j] * (pow(2,j) + 0.5);
		}
		resetAll();
	}

	if(val2 > THRESHOLDLEAVE){resetAll();}
	if(nowTime - time2 > THRESHOLDTIME){reset2();}
}