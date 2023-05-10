#include <VarSpeedServo.h>

// サーボの数。
const int NUM_SERVO = 4;

// 各サーボを入れる配列。
VarSpeedServo servo[NUM_SERVO];

// サーボを回転させる速さ。1~255。
const int SERVO_SPEED = 100;

// サーボを直進にする際の角度。適宜いじってください。
const int SERVO_ANGLE_STRAIGHT[NUM_SERVO] = {25, 25, 25, 25};
// サーボを曲げる際の角度。適宜いじってください。
const int SERVO_ANGLE_CURVE[NUM_SERVO] = {75, 75, 75, 75};
// サーボをアタッチするピンの指定。適宜いじってください。
const int SERVO_ATTACH_PIN[NUM_SERVO] = {3, 5, 9, 10};
const byte STRAIGHT = 0;
const byte CURVE = 1;
// 各サーボの状態を格納。初期値は適宜いじってください。
byte servo_status[NUM_SERVO] = {STRAIGHT, STRAIGHT, STRAIGHT, STRAIGHT};

void servo_change(byte servo_id, byte servo_state) {
    //servoの向きを切り替える関数。
    if (servo_state == STRAIGHT) {
        servo[servo_id].write(SERVO_ANGLE_STRAIGHT[servo_id], SERVO_SPEED, true);
        servo_status[servo_id] = STRAIGHT;
    }
    else {
        servo[servo_id].write(SERVO_ANGLE_CURVE[servo_id], SERVO_SPEED, true);
        servo_status[servo_id] = CURVE;
    }
}

void setup() {
    Serial.begin(9600);
    for (int servo_id = 0; servo_id < NUM_SERVO; servo_id++) {
        // attachする。
        servo[servo_id].attach(SERVO_ATTACH_PIN[servo_id]);
        // サーボの向きの初期化。
        if (servo_status[servo_id] == STRAIGHT) {
            servo[servo_id].write(SERVO_ANGLE_STRAIGHT[servo_id], SERVO_SPEED, true);
        }
        else {
            servo[servo_id].write(SERVO_ANGLE_CURVE[servo_id], SERVO_SPEED, true);
        }
    }
}

void loop() {
    while (Serial.available() >= 2) { 
        // シリアルで受け取った信号をもとにサーボを動かす
        byte servo_id = Serial.read();
        byte servo_state = Serial.read();
        servo_change(servo_id, servo_state);
    }
}
