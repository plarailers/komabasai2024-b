/**
 * @file HighSpeedAnalogRead.h
 * @author Hibiki Matsuda (@thgc_Mtd_h)
 * @brief ESP32のI2S ADCを用いて、高速(>10ksamples/s)かつ等間隔なAD変換を行う
 * AD変換のサンプルごとに、計測値を割り込み関数で受け取れるAPIを提供する
 * @version 0.1
 * @date 2023-04-11
 * 
 * @copyright Copyright (c) 2023
 * 
 */

#include <Arduino.h>
#include <driver/adc.h>
#include <freertos/task.h>

class HighSpeedAnalogRead {

public:
  HighSpeedAnalogRead();

  /**
   * @brief ADC入力ピンを追加する。最大16個まで入力ピンを指定できる
   * @param channel ADC1の入力チャンネル。ADC1_CHANNEL_x
   * @param resolution 分解能。ADC_WIDTH_BIT_9 (9bit), ADC_WIDTH_BIT_10 (10bit), ADC_WIDTH_BIT_11 (11bit),
   * ADC_WIDTH_BIT_12 (12bit) のいずれかを指定する。デフォルトは12bit。
   * @param attenuation アッテネータのゲイン。http://radiopench.blog96.fc2.com/blog-entry-1034.html
   * などが詳しい。デフォルトは-11dB
   * @return 1:success, 0:指定されたピンはADCに非対応などの理由でADC入力ピンを追加できなかった
   */
  int addChannel(adc1_channel_t channel, adc_bits_width_t resolution, adc_atten_t attenuation);

  /**
   * @brief 1サンプルのAD変換が完了した時に呼び出される割り込み関数を登録する（2回以上登録した場合は上書きされる）
   * @param func 割り込み関数として実行したい関数へのポインタ。以下のような、data と chNum を引数に取る関数を想定。
   * void func(uint16_t* data, size_t chNum) {
   *   // do something...
   * }
   * - data: サンプリングしたデータが記録されている配列へのポインタ。たとえばaddPinで2つの入力ピンを登録した場合は、
   *   - data[0]: 1回目に登録したピンのサンプリング結果
   *   - data[1]: 2回目に登録したピンのサンプリング結果
   *   を取得できる。各「サンプリング結果」の中身は
   *   - bit 0-11 : サンプリング結果 (0-4096)
   *   - bit 12-15 : チャンネル番号 (0-7)
   *   であり（詳細はTechnical Reference Manualを参照）、例えば
   *     sampledData = data[0] & 0xfff;
   *     channelNum = (data[0] << 12) & 0xf;
   *   でそれぞれ取得できる
   * - chNum: サンプリングした入力ピンの数
   */
  void attachInterrupt(void (*func)(uint16_t* data, size_t chNum));

  /**
   * @brief サンプリングレート[Hz]を指定する
   * @param sampleRateHz サンプリングレート[Hz]
   */
  void setSampleRateHz(uint32_t sampleRateHz);

  /**
   * @brief AD変換を開始する
   * @return int 1:success, 0:fail
   */
  int start();

  /**
   * @brief AD変換を停止しリソースを解放する
   */
  void stop();

private:
  // ADC入力ピン(チャンネル)数。addPinを実行するごとに1ずつ増える
  uint8_t chNum_;

  // サンプリングレート[Hz]。指定したすべての入力チャンネルについて、ここで指定したサンプリングレートで測定が行われる
  // したがってAD変換は毎秒chNum_*sampleRateHz回実行される
  uint32_t sampleRateHz_;

  // 各入力チャンネルの設定を記録する配列。データシートではpattern tableと呼ばれていて、最大16個まで指定できる
  uint8_t patternTable_[16];

  // i2s_readで読み取ったデータの記録先。最大16チャンネルを設定できるので、16個確保している
  uint16_t readBuffer_[16];

  // i2s_readを実行するタスクのタスクハンドラ
  TaskHandle_t taskHandle_;

  // 1サンプル分の読み取りが完了したときに呼び出される関数で、ユーザがattachInterrupt()を用いて指定できる
  // たとえば制御演算など、毎サンプルごとにデータを処理する関数が渡されることを想定している
  void (*isrFunc_)(uint16_t* data, size_t chNum);

  // i2_readを実行するタスク関数
  static void reader_(void* ptrToThisInstance);
};
