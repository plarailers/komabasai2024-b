/*
 * ファイル>スケッチ例>ESP32>I2S>HiFreq_ADCを参考に作成した。
 * I2Sを用いて高速かつ等間隔にAD変換を行い、データをシリアルに出力する。
 */

#include <BluetoothSerial.h>
#include <driver/i2s.h>
#include <soc/syscon_reg.h>
#include "src/HighSpeedAnalogRead.h"
#include "src/arduinoFFT/arduinoFFT.h"

#define SAMPLING_RATE 10000  // AD変換のサンプリングレート[Hz]
#define ADC_N_CHANNEL 2      // AD変換したい信号の数。電圧と電流なので2つ
#define ADC_CH_CURRENT ADC1_CHANNEL_4 //pin 32
#define ADC_CH_VOLTAGE ADC1_CHANNEL_5 //pin 33
#define FFT_VEC_LEN 1024  // FFTに使うサンプル数
#define AVE_LEN 32   // 平滑化後の電流・電圧・周波数を記録しておくサンプル数
#define N_MEDIAN 5   // モータ周波数は平均ではなく中央値で平滑化する。平滑化サンプル数

#define SERIAL_LEN 16

arduinoFFT FFT;
BluetoothSerial SerialBT;
HighSpeedAnalogRead adc;

const int PWM_PIN = 25;
const int PWM_CHANNEL = 0;
const uint32_t PWM_FREQ = 20000;

int pwm_duty = 0;

portMUX_TYPE ringbuf_mutex = portMUX_INITIALIZER_UNLOCKED;

float ringbuf_current_A[FFT_VEC_LEN];
float ringbuf_voltage_V[FFT_VEC_LEN];
int i_ringbuf = 0;  // いま書き込むリングバッファのインデックス

float vec_current_real[FFT_VEC_LEN];  // Real part of Current Vector
float vec_current_imag[FFT_VEC_LEN];  // Imaginal part of Current Vector
  
float buf_freq_median[N_MEDIAN];  // 周波数の中央値を取るための配列
int i_median = 0;

unsigned long ave_time_us[AVE_LEN];  // フーリエ変換で周波数を計算した時刻
float ave_freq_Hz[AVE_LEN];          // 中央値を取った後の周波数
float ave_current_A[AVE_LEN];        // フーリエ変換期間の平均を取った電流
float ave_voltage_V[AVE_LEN];        // フーリエ変換期間の平均を取った電圧
int i_ave = 0;  // いま書き込んでいるバッファのインデックス

float average(float* vec, size_t len) {
  float sum = 0.0f;
  for (int i=0; i<len; i++) {
    sum += vec[i];
  }
  return sum / len;
}

float median(float* vec) {
  // 渡された配列vecをコピー
  float data[N_MEDIAN];
  for (int i=0; i<N_MEDIAN; i++) {
    data[i] = vec[i];
  }

  // データを大きさの順に並べ替え
  float tmp;
  for(int i=1; i<N_MEDIAN; i++) {
    for(int j=0; j<N_MEDIAN - i; j++) {
      if(data[j] > data[j + 1]) {
        tmp = data[j];
        data[j] = data[j + 1];
        data[j + 1] = tmp;
      }
    }
  }

  // メジアンを求める
  if(N_MEDIAN % 2 == 1) { // データ数が奇数個の場合
    return data[(N_MEDIAN - 1) / 2];
  } else { // データ数が偶数の場合
    return (data[(N_MEDIAN / 2) - 1] + data[N_MEDIAN / 2]) / 2.0;
  }
}

/**
 * @brief ADCによる1サンプリングが完了したときに実行される関数。
 * サンプリング結果をringbufに転記する
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
  // リングバッファへサンプリング結果を転記
  portENTER_CRITICAL(&ringbuf_mutex);
  for (size_t i = 0; i < chNum; i++) {
    uint16_t value = data[i] & 0xFFF;         // ADCの読み値(0-4095)
    uint8_t channel = (data[i] >> 12) & 0xF;  // CH番号
    if (channel == ADC_CH_CURRENT) {
      ringbuf_current_A[i_ringbuf] = (float)value;
    } else if (channel == ADC_CH_VOLTAGE) {
      ringbuf_voltage_V[i_ringbuf] = (float)value;
    }
  }
  portEXIT_CRITICAL(&ringbuf_mutex);
  // リングバッファのインデックスを進める
  i_ringbuf = (i_ringbuf + 1) % FFT_VEC_LEN;
}

void setup() {
  Serial.begin(115200);
  ledcSetup(PWM_CHANNEL, PWM_FREQ, 8);
  ledcAttachPin(PWM_PIN, PWM_CHANNEL);
  ledcWrite(PWM_CHANNEL, pwm_duty);
  
  SerialBT.begin("Bluetooth-Oscillo");
  
  adc.addChannel(ADC_CH_CURRENT, ADC_WIDTH_12Bit, ADC_ATTEN_0db);
  adc.addChannel(ADC_CH_VOLTAGE, ADC_WIDTH_12Bit, ADC_ATTEN_0db);
  adc.setSampleRateHz(SAMPLING_RATE);
  adc.attachInterrupt(adcReadDone);
  adc.start();

  Serial.println("setup end");
}

void loop() {

  // print value through Serial
  // (serial speed should be 1Mbps or more)
  /*
  for (int i=0; i<FFT_VEC_LEN; i++) {
    Serial.print(vec_current_real[i]);
    Serial.print(",");
    Serial.println(vec_voltage[i]);
  }
  */
  // フーリエ変換を行った時刻を記録しておく
  ave_time_us[i_ave] = micros();

  // フーリエ変換用にデータをvec_currentに転記
  portENTER_CRITICAL(&ringbuf_mutex);
  for (size_t i = 0; i < FFT_VEC_LEN; i++) {
    vec_current_real[i] = ringbuf_current_A[(i_ringbuf + 1 + i) / FFT_VEC_LEN];
    vec_current_imag[i] = 0.0f;
  }
  
  // 電流・電圧の平均を取る
  ave_current_A[i_ave] = average(ringbuf_current_A, FFT_VEC_LEN);
  ave_voltage_V[i_ave] = average(ringbuf_voltage_V, FFT_VEC_LEN);
  portEXIT_CRITICAL(&ringbuf_mutex);

  // Fourier transform (apply Hamming windowing)
  FFT = arduinoFFT(vec_current_real, vec_current_imag, FFT_VEC_LEN, SAMPLING_RATE);
  FFT.Windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  FFT.Compute(FFT_FORWARD);  // calculate FFT
  FFT.ComplexToMagnitude();  // mag. to vR 1st half
  float peak = FFT.MajorPeak();  // get peak freq

  buf_freq_median[i_median] = peak;
  i_median = (i_median + 1) % N_MEDIAN;

  // 周波数を中央値を取ることで平滑化して記録
  ave_freq_Hz[i_ave] = median(buf_freq_median);

  // Serial.print(ave_freq_Hz[i_ave]);
  Serial.print(ave_time_us[i_ave]);
  Serial.print(", ");
  Serial.print(peak);
  Serial.print(", ");
  Serial.print(ave_current_A[i_ave]);
  Serial.print(", ");
  Serial.println(ave_voltage_V[i_ave]);

  // 電圧・電流・周波数の平均を取り終わったのでインデックスを進める
  i_ave = (i_ave + 1) % AVE_LEN;

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
  
  delay(1);
}
