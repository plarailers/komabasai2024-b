#define OFF 0
#define ON 1
#define LEDC_CHANNEL_1 1 //サーボモーター用のチャンネルを1に設定
#define LEDC_SERVO_FREQ 50 //チャネル1の通信速度を設定
#define LEDC_RESOLUTIONBIT_SERVO 8 //256段階で制御
#define LEDC_CHANNEL_2 2 //ブザーを鳴らすためのチャンネルを2に設定
#define LEDC_BUZZER_FREQ 5000 //チャネル2の通信速度を設定
#define LEDC_RESOLUTIONBIT_BUZZER 13
//#include <Servo.h>
//#include <BluetoothSerial.h>

//Servo myservo; //Servoオブジェクトを生成

// String device_name = "ESP32-BT-Slave";//デバイスに名前を設定
// BluetoothSerial SerialBT; //BluetoothSerialオブジェクトを作成

int switchpin = 25;
int servopin = 33;
int buzzerpin = 27;
int melo = 200;
//bool block = true;
volatile int counter = 0;
volatile int lasttime = 0;

bool move_state = false;

void IRAM_ATTR button_pushed(){
  if(millis() - lasttime >1000){
    // if(move_state = false){
    //   block = !block;  
    // }
    // else{
    //   block = block;
    // }
    move_state = !move_state;
    counter = counter + 1;
  }
  else{
    move_state = move_state;
  }
  lasttime = millis();

}


void setup() {
  Serial.begin(115200);

  
  pinMode (switchpin,INPUT); //switchpin(25)を入力に設定

  ledcSetup(LEDC_CHANNEL_1,LEDC_SERVO_FREQ,LEDC_RESOLUTIONBIT_SERVO);
  ledcAttachPin(servopin,LEDC_CHANNEL_1);
  //myservo.write(20);
  ledcSetup(LEDC_CHANNEL_2,LEDC_BUZZER_FREQ,LEDC_RESOLUTIONBIT_BUZZER);
  ledcAttachPin(buzzerpin,LEDC_CHANNEL_2);

  ledcWrite(LEDC_CHANNEL_1,13); //制御パルス1ms

  //myservo.attach(servopin); //servopin(33)にサーボモータの信号線を接続

  // SerialBT.begin(device_name);
  // Serial.printf("The device with name \"%s\" is started. \n Now you can pair it with Bluetooth!\n", device_name.c_str());

  attachInterrupt(switchpin, button_pushed, RISING);//割り込みを登録　オンになった時に関数button_pushedを実行
}


void loop() {//メインCPU(core1)で実行するプログラム


  if (move_state == HIGH) {

     
    // SerialBT.print("{\"button\":");
    // SerialBT.print(move_state);
    // SerialBT.println("}");

    Serial.print("{\"blocked\":");
    Serial.print(move_state);
    Serial.println("}");
    
    // Serial.print(move_state);
    // Serial.print(digitalRead(25));
    // Serial.print(digitalRead(33));
    // Serial.println(digitalRead(14));

    ledcWrite(LEDC_CHANNEL_1,23); //制御パルス2ms
    // myservo.write(40);
    // myservo.write(60);
    // myservo.write(80);
    // myservo.write(100);
    // myservo.write(120);//120度へ回転
    delay(100);
    //Serial.println(counter);

    // Serial.print(move_state);
    // Serial.print(digitalRead(25));
    // Serial.print(digitalRead(33));
    // Serial.println(digitalRead(14));

    ledcWriteTone(LEDC_CHANNEL_2,587);//レ
    delay(500);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(150);
    ledcWriteTone(LEDC_CHANNEL_2,440);//ラ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,494);//シ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,523);//ド
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,587);//レ
    delay(500);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,0);
    delay(50);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,0);
    delay(300);
    ledcWriteTone(LEDC_CHANNEL_2,659);//ミ
    delay(500);
    ledcWriteTone(LEDC_CHANNEL_2,523);//ド
    delay(150);
    ledcWriteTone(LEDC_CHANNEL_2,587);//レ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,659);//ミ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,740);//ファ＃
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,784);//ソ高い
    delay(500);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,0);
    delay(50);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,0);
    delay(400);
    ledcWriteTone(LEDC_CHANNEL_2,523);//ド
    delay(500);
    ledcWriteTone(LEDC_CHANNEL_2,587);//レ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,523);//ド
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,494);//シ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,440);//ラ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,0);
    delay(100);
    ledcWriteTone(LEDC_CHANNEL_2,494);//シ
    delay(500);
    ledcWriteTone(LEDC_CHANNEL_2,523);//ド
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,494);//シ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,440);//ラ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,370);//ファ＃
    delay(500);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,440);//ラ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,494);//シ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,392);//ソ
    delay(200);
    ledcWriteTone(LEDC_CHANNEL_2,494);//シ
    delay(400);
    ledcWriteTone(LEDC_CHANNEL_2,440);//ラ
    delay(400);
    ledcWriteTone(LEDC_CHANNEL_2,0);
    delay(400);

    // if (move_state = 0){
    //   block = !block;
    //   Serial.print("{\"button\":");
    //   Serial.print(block);
    //   Serial.println("}"); 
    // }
    // else{
    //   block = block;
    // }



    // Serial.print(move_state);
    // Serial.print(digitalRead(25));
    // Serial.print(digitalRead(33));
    // Serial.println(digitalRead(14));

  }
  else{
    // SerialBT.print("{\"button\":");
    // SerialBT.print(move_state);
    // SerialBT.println("}");

    Serial.print("{\"blocked\":");
    Serial.print(move_state);
    Serial.println("}");

    // Serial.print(move_state);
    // Serial.print(digitalRead(25));
    // Serial.print(digitalRead(33));
    // Serial.println(digitalRead(14));

    //myservo.write(20);//もとに戻る
    ledcWrite(LEDC_CHANNEL_1,13); //制御パルス1ms
    // Serial.print(move_state);
    // Serial.print(digitalRead(25));
    // Serial.print(digitalRead(33));
    // Serial.println(digitalRead(14));
    //Serial.println(counter);
  
    ledcWriteTone(LEDC_CHANNEL_2,0);
    delay(500);

    

  }



}
