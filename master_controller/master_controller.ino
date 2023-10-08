//LEDを点灯する際はコモン(ディジット)がLOW、セグメントはHIGHになる必要がある
#define DIGIT_ON LOW
#define DIGIT_OFF HIGH
#define SEGMENT_ON HIGH
#define SEGMENT_OFF LOW

#include <BluetoothSerial.h>

BluetoothSerial SerialBT;//BluetoothSerialオブジェクトを作成

const int digitPins[4] = {13,14,15,16}; //コモン(ディジット)のピン番号を配列で指定
const int segmentPins[8] = {17,18,19,21,22,23,25,26}; //セグメントのピン番号を配列で指定

const int digitPinA = 13;
const int digitPinB = 14;
const int digitPinC = 15;
const int digitPinD = 16;

const int segmentPinA = 17;
const int segmentPinB = 18;
const int segmentPinC = 19;
const int segmentPinD = 21;
const int segmentPinE = 22;
const int segmentPinF = 23;
const int segmentPinG = 25;
const int segmentPinDP = 26;

const int digits[] = {
  0b01111110, //0
  0b00110000, //1
  0b01101101, //2
  0b01111001, //3
  0b00110011, //4
  0b01011011, //5
  0b01011111, //6
  0b01110010, //7
  0b01111111, //8
  0b01111011  //9
};

void displayOneNumber(int n){
  //引数を入力したい数字としてそれを表示する関数を設定
  digitalWrite(segmentPinA,digits[n] & 0b01000000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinB,digits[n] & 0b00100000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinC,digits[n] & 0b00010000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinD,digits[n] & 0b00001000 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinE,digits[n] & 0b00000100 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinF,digits[n] & 0b00000010 ? SEGMENT_ON :SEGMENT_OFF);
  digitalWrite(segmentPinG,digits[n] & 0b00000001 ? SEGMENT_ON :SEGMENT_OFF);
}

void clearSegments(){
  for (int k = 0; k < 8; k = k + 1){
    digitalWrite(segmentPins[k],SEGMENT_OFF);
  }
}

void displayNumber(int n){
  for (int j = 3; j >= 0; j = j - 1){
    digitalWrite(digitPins[j],DIGIT_ON); //右の桁から順に表示する桁(ディジット)を選択してONにする
    displayOneNumber(n % 10);
    if (j == 2){
      digitalWrite(segmentPinDP,SEGMENT_ON);
    }
    delay(1);
    clearSegments();
    digitalWrite(digitPins[j],DIGIT_OFF);
    n /= 10;
    
  }
}

int velocity = 0;
int acceleration = 0;
int lasttime = 0;
int velocitydisplay = 0;

void setup() {
  for (int i = 0; i <= 3; i = i + 1){
    pinMode(digitPins[i],OUTPUT);
    digitalWrite(digitPins[i],DIGIT_OFF);
  }

  for (int i = 0; i < 8; i = i + 1){
    pinMode(segmentPins[i],OUTPUT);
    digitalWrite(segmentPins[i],SEGMENT_OFF);
  }

  Serial.begin(115200);
  pinMode(27,INPUT);

  SerialBT.begin(device_name);
  Serial.printf("The device with name \"%s\" is started.\n Now you can pair it with Bluetooth!\n", device_name.c_str());

}



void loop() {

  

  if (millis() - lasttime > 100) { //100ミリ秒に1回加速度から速度の計算を行う
    

    int val = analogReadMilliVolts(27);
    Serial.println(val);

    acceleration = ((val-128)*14/(3127-128))-8; //可変抵抗の読み取り値を-8～+5の加速度に変換
    Serial.println(acceleration);

    velocity = velocity + acceleration; //指定された加速度から速度を計算
  
      if (velocity <= 0){
        velocity = 0; //速度の計算値が0以下の時は0を指定
      }
      if (velocity >= 255){
        velocity = 255; //速度の計算値が255以上の時は255を指定
      }
      else{
        velocity = velocity; //速度の計算値が0～255に収まっていればそのまま
      }


    Serial.println(velocity);
    SerialBT.println(velocity);
    lasttime = millis();
  }

  velocitydisplay = velocity*4;
  displayNumber(velocitydisplay);

}
