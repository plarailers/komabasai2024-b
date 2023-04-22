/*
 * ファイル>スケッチ例>ESP32>I2S>HiFreq_ADCを参考に作成した。
 * I2Sを用いて高速かつ等間隔にAD変換を行い、データをシリアルに出力する。
 */

#include <BluetoothSerial.h>
#include <driver/i2s.h>
#include <esp_adc_cal.h>
#include <soc/syscon_reg.h>
#include "src/Filter.h"
#include "src/HighSpeedAnalogRead.h"
#include "src/MotorRotationDetector.h"

#define SERIAL_LEN 16

// ピン番号
const int PIN_PWM = 25;
const int PIN_SENSE_I = 32;
const int PIN_SENSE_V = 33;
const int PIN_PHOTO_CLK = 34;
const int PIN_PHOTO_DAT = 35;

// ADC関係(ユーザが指定する定数)
const int ADC_SAMPLING_RATE = 20000;  // AD変換のサンプリングレート[Hz]
const int ADC_N_CHANNEL = 4;      // AD変換したい信号の数。電圧、電流、clk、datの4つ
const adc1_channel_t ADC_CH_CURRENT = (adc1_channel_t)(digitalPinToAnalogChannel(PIN_SENSE_I));
const adc1_channel_t ADC_CH_VOLTAGE= (adc1_channel_t)(digitalPinToAnalogChannel(PIN_SENSE_V));
const adc1_channel_t ADC_CH_CLK = (adc1_channel_t)(digitalPinToAnalogChannel(PIN_PHOTO_CLK));
const adc1_channel_t ADC_CH_DAT = (adc1_channel_t)(digitalPinToAnalogChannel(PIN_PHOTO_DAT));
const float R1_I = 1.0f;       // 電流検出用シャント抵抗
const float R2_I = 470.0f;     // 電流検出信号の入力抵抗
const float R3_I = 10000.0f;   // 電流検出信号のプルアップ抵抗
const float R1_V = 47000.0f;   // 電圧計の分圧抵抗(上)
const float R2_V = 10000.0f;   // 電圧計の分圧抵抗(下)
const float R3_V = 220000.0f;  // 電圧検出信号のプルアップ抵抗
const float GAIN_I = (R2_I + R3_I) / R3_I / R1_I;  // ADCで読んだ電圧[V]を電流[A]に換算する係数
const float GAIN_V = (R1_V*R2_V + R2_V*R3_V + R3_V*R1_V) / (R2_V*R3_V);  // ADCで読んだ電圧からモータ電圧を計算する係数

// モータPWM関係
const int PWM_CHANNEL = 0;
const float PWM_FREQ = ADC_SAMPLING_RATE;  // モータのPWM周波数[Hz]。ADCと同一にすること

// setupで代入される値
esp_adc_cal_characteristics_t adc_chars_1;
uint32_t current_offset_mV = 0;  // 0AのときのADC測定値[mV]
uint32_t voltage_offset_mV = 0;  // 0VのときのADC測定値[mV]

// 指令などなど
int pwm_duty = 0;
int photoreflector_clk = 0;  // フォトリフレクタのクロック線読み値(0～4096)  
int photoreflector_dat = 0;  // フォトリフレクタのデータ線読み値(0～4096)
unsigned int motor_total_rotation = 0;  // マイコン起動から現在までの、モータの総回転数

// for debug
uint32_t value_mV_debug = 0;
float current_A_debug = 0.0f;

BluetoothSerial SerialBT;
HighSpeedAnalogRead adc;
MotorRotationDetector motorRotationDetector;
FirstHPF current_hpf;

float ringbuf[10000];
float ringbuf_for_print[10000];
int i_ringbuf = 0;
portMUX_TYPE mutex = portMUX_INITIALIZER_UNLOCKED;

/**
 * @brief ADCによる1サンプリングが完了したときに実行される関数。
 * @param data サンプリングしたデータが記録されている配列へのポインタ。
 *             たとえばaddChannelで2つの入力チャンネルを登録した場合は、
 *               - data[0]: 1つ目に登録したCHのサンプリング結果
 *               - data[1]: 2つ目に登録したCHのサンプリング結果
 *             を取得できる。各「サンプリング結果」の中身は
 *               - bit 0-11 : サンプリング結果 (0-4096)
 *               - bit 12-15 : チャンネル番号 (0-7)
 *             である
 * @param chNum サンプリングした入力ピンの数
 */
void adcReadDone(uint16_t* data, size_t chNum) {
  float current_A = 0.0f;
  float voltage_V = 0.0f;
  for (size_t i = 0; i < chNum; i++) {
    uint16_t value_raw = data[i] & 0xFFF;  // ADCの読み値(0-4095)
    uint32_t value_mV = esp_adc_cal_raw_to_voltage(value_raw, &adc_chars_1);
    uint8_t channel = (data[i] >> 12) & 0xF;  // CH番号
    if (channel == ADC_CH_CURRENT) {
      current_A = GAIN_I * (int32_t)(value_mV - current_offset_mV) / 1000.0f;
      value_mV_debug = value_mV;
      portENTER_CRITICAL_ISR(&mutex);
      ringbuf[i_ringbuf] = current_A;  //current_hpf.update(current_A, 1.0f / ADC_SAMPLING_RATE);
      i_ringbuf = (i_ringbuf + 1) % 10000;
      portEXIT_CRITICAL_ISR(&mutex);
      current_A_debug = current_A;
    } else if (channel == ADC_CH_VOLTAGE) {
      voltage_V = GAIN_V * (int32_t)(value_mV - voltage_offset_mV) / 1000.0f;
    } else if (channel == ADC_CH_CLK) {
      photoreflector_clk = value_raw;
    } else if (channel == ADC_CH_DAT) {
      photoreflector_dat = value_raw;
    }
  }
  motorRotationDetector.update(current_A, 1000000 / ADC_SAMPLING_RATE);
}

void setup() {
  Serial.begin(1000000);
  ledcSetup(PWM_CHANNEL, PWM_FREQ, 8);
  ledcAttachPin(PIN_PWM, PWM_CHANNEL);
  ledcWrite(PWM_CHANNEL, pwm_duty);
  
  SerialBT.begin("Bluetooth-Oscillo");

  current_hpf.setFc(3000.0f);

  // 電流・電圧のオフセット取得(64回analogReadして、平均値を取得)
  analogSetAttenuation(ADC_0db);
  for (int i = 0; i < 64; i++) {
    current_offset_mV += analogReadMilliVolts(PIN_SENSE_I);
    voltage_offset_mV += analogReadMilliVolts(PIN_SENSE_V);
    delay(10);  // 連続でreadすると若干値が小さくなってしまったのでdelayを入れる
  }
  current_offset_mV /= 64;
  voltage_offset_mV /= 64;
  Serial.print("[setup] current_offset_mV: ");
  Serial.println(current_offset_mV);
  Serial.print("[setup] voltage_offset_mV: ");
  Serial.println(voltage_offset_mV);

  // ADCキャリブレーション値の設定
  esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_0db, ADC_WIDTH_12Bit, 1100, &adc_chars_1);
  
  // ADC測定対象チャンネルを追加し、測定開始
  adc.addChannel(ADC_CH_CURRENT, ADC_WIDTH_12Bit, ADC_ATTEN_0db);
  adc.addChannel(ADC_CH_VOLTAGE, ADC_WIDTH_12Bit, ADC_ATTEN_0db);
  adc.addChannel(ADC_CH_CLK, ADC_WIDTH_12Bit, ADC_ATTEN_11db);
  adc.addChannel(ADC_CH_DAT, ADC_WIDTH_12Bit, ADC_ATTEN_11db);
  adc.setSampleRateHz(ADC_SAMPLING_RATE);
  adc.attachInterrupt(adcReadDone);
  adc.start();

  Serial.println("setup end");
}

void loop() {
  Serial.print("rps: ");
  Serial.print(motorRotationDetector.getRps(), 8);
  Serial.print(", rotation: ");
  Serial.println(motorRotationDetector.getRotation());
  // Serial.print(", totalRotation: ");
  // Serial.println(motorRotationDetector.getTotalRotation());

  // Serial.print("value_mV: ");
  // Serial.print(value_mV_debug);
  // Serial.print(", current_A: ");
  // Serial.print(current_A_debug);
  // Serial.print(", noise_A: ");
  // Serial.println(motorRotationDetector.getNoise());
  
  if (i_ringbuf == 0) {
    portENTER_CRITICAL_ISR(&mutex);
    for (int i = 0; i < 10000; i++) {
      ringbuf_for_print[i] = ringbuf[i];
    }
    portEXIT_CRITICAL_ISR(&mutex);
    for (int i = 0; i < 10000; i++) {
      // Serial.println(ringbuf_for_print[i], 3);
    }
  }

  // ------------------------------------
  // Motor duty command receive and apply
  // ------------------------------------
  byte buf[SERIAL_LEN];
  memset(buf, 0, SERIAL_LEN);
  
  int i = 0;
  if (Serial.available()){
    while(Serial.available()) {
      buf[i] = Serial.read();
      i++;
      if (i >= SERIAL_LEN) {
        break;
      }
    }
    sscanf((char*)buf, "%d", &pwm_duty);
    // Serial.println(pwm_duty);
    ledcWrite(PWM_CHANNEL, pwm_duty);
  }
  delay(100);
}
