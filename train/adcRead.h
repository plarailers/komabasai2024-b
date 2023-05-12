/*
 * ファイル>スケッチ例>ESP32>I2S>HiFreq_ADCを参考に作成した。
 * I2Sを用いて高速かつ等間隔にAD変換を行い、データをシリアルに出力する。
 */

#include <esp_adc_cal.h>
#include "src/Filter.h"
#include "src/HighSpeedAnalogRead.h"
#include "src/MotorRotationDetector.h"
#include "src/PhotoPositionID_Detector.h"

#define SERIAL_LEN 16

// ピン番号
const int PIN_PWM = 25;
const int PIN_SENSE_I = 32;
const int PIN_SENSE_V = 33;
const int PIN_PHOTO_SENSOR1 = 34;
const int PIN_PHOTO_SENSOR2 = 35;

// ADC関係(ユーザが指定する定数)
const int ADC_SAMPLING_RATE = 20000;  // AD変換のサンプリングレート[Hz]
const int ADC_N_CHANNEL = 4;      // AD変換したい信号の数。電圧、電流、clk、datの4つ
const adc1_channel_t ADC_CH_CURRENT = (adc1_channel_t)(digitalPinToAnalogChannel(PIN_SENSE_I));
const adc1_channel_t ADC_CH_VOLTAGE= (adc1_channel_t)(digitalPinToAnalogChannel(PIN_SENSE_V));
const adc1_channel_t ADC_CH_SENSOR1 = (adc1_channel_t)(digitalPinToAnalogChannel(PIN_PHOTO_SENSOR1));
const adc1_channel_t ADC_CH_SENSOR2 = (adc1_channel_t)(digitalPinToAnalogChannel(PIN_PHOTO_SENSOR2));
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
int photo_sensor1 = 0;  // フォトリフレクタの読み値1(0～4096)  
int photo_sensor2 = 0;  // フォトリフレクタの読み値2(0～4096)

HighSpeedAnalogRead adc;
MotorRotationDetector motorRotationDetector;
PhotoPositionID_Detector photoPositionID_Detector;

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
    } else if (channel == ADC_CH_VOLTAGE) {
      voltage_V = GAIN_V * (int32_t)(value_mV - voltage_offset_mV) / 1000.0f;
    } else if (channel == ADC_CH_SENSOR1) {
      photo_sensor1 = value_raw;
    } else if (channel == ADC_CH_SENSOR2) {
      photo_sensor2 = value_raw;
    }
  }
  motorRotationDetector.update(current_A, 1000000 / ADC_SAMPLING_RATE);
  photoPositionID_Detector.update(photo_sensor1, photo_sensor2);
}

int getPhoto1() {
  return photo_sensor1;
}

int getPhoto2() {
  return photo_sensor2;
}

void adcSetup() {
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
    adc.addChannel(ADC_CH_SENSOR1, ADC_WIDTH_12Bit, ADC_ATTEN_11db);
    adc.addChannel(ADC_CH_SENSOR2, ADC_WIDTH_12Bit, ADC_ATTEN_11db);
    adc.setSampleRateHz(ADC_SAMPLING_RATE);
    adc.attachInterrupt(adcReadDone);
    adc.start();
}