const int pin = 25;
int counter = 0, preCounter = 0;
volatile unsigned long preTime = 0, nowTime;
unsigned long chattaringTime = 10;

void setup() {
  Serial.begin(115200);
  pinMode(pin, INPUT);
  attachInterrupt(pin, count, CHANGE);
}

void loop() {
  Serial.println(counter);
}

void count() {
  nowTime = millis();
  if(nowTime - preTime > chattaringTime){
    counter += 1;
    preTime = nowTime;
  }
}
