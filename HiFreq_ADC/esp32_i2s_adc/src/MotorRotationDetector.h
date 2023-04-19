/**
 * @file MotorRotationDetector.h
 * @author @thgc_Mtd_h
 * @brief ブラシモータの電流ノイズを用いた回転量推定コード
 * 実験的に設定した定数は、MotorRotationDetector.cpp に記載
 * @version 0.1
 * @date 2023-04-17
 * 
 * @copyright Copyright (c) 2023
 * 
 */

#pragma once

#include <Arduino.h>
#include "Filter.h"

class MotorRotationDetector {
public:
  /**
   * @brief Construct a new Motor Rotation Detector object
   */
  MotorRotationDetector();

  /**
   * @brief 電流のサンプリング結果から、回転量を更新する
   * @param current_A 電流測定値[A]
   * @param time_us 電流をサンプリングした時刻[us]
   */
  void update(float current_A, unsigned long time_us);

  /**
   * @brief マイコン起動から現在までの総回転量[回]を取得する。
   * マイコンをリセットするまでずっと積算される
   * @return unsigned int 回転量[回]
   */
  unsigned int getTotalRotation();

  /**
   * @brief 前回この関数を呼び出してから何回転したかを取得する。
   * 関数を呼ぶたびに0にリセットされる
   * @return unsigned int 回転量[回]
   */
  unsigned int getRotation();

  /**
   * @brief モータが1秒あたり何回転しているかを取得する
   * @return float モータ回転速度[rps]
   */
  float getRps();

  float getNoise();

private:
  const unsigned int PULSE_PER_ROTATION_;  // モータ1回転あたり何個のパルスが出るか
  const unsigned long PULSE_IGNORE_DURATION_US_;  // パルス検出からある時間[us]だけは次のパルスを無視する
  const float THRESHOLD_A_;  // ノイズと判定する電流閾値

  FirstHPF current_hpf_;  // 電流波形からノイズを抽出するためのハイパスフィルタ
  bool reach_threshold_flag_;  // 閾値に達したことを示すフラグ
  unsigned int pulse_count_;  // パルスを検出するたびに1増えて、PULSE_PER_ROTATION_で0に戻る
  unsigned long last_pulse_time_us_;  // パルスを検出した直近の時刻[us]
  unsigned long last_rotate_time_us_;  // モータが1周した直近の時刻[us]
  unsigned int total_rotation_;  // マイコン起動時から積算した総回転数
  unsigned int last_rotation_;  // 直前にgetRotationを呼び出した時の総回転数
  float rps_;  // モータ回転数(1秒に何回転したか)[rps]
  float noise;
};
