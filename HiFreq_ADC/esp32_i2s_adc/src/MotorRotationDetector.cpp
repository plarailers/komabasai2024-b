#include "MotorRotationDetector.h"

MotorRotationDetector::MotorRotationDetector()
: PULSE_PER_ROTATION_(6),
  PULSE_IGNORE_DURATION_US_(300),
  THRESHOLD_A_(-0.02f),
  reach_threshold_flag_(false),
  pulse_count_(0),
  last_pulse_time_us_(0),
  last_rotate_time_us_(0),
  total_rotation_(0),
  last_rotation_(0),
  rps_(0.0f),
  noise(0.0f)
{
  current_hpf_.setFc(3000.0f);
}

void MotorRotationDetector::update(float current_A, unsigned long time_us) {
  // ハイパスフィルタでノイズ分を抽出
  noise = current_hpf_.update(current_A, time_us / 1e6);
  // ノイズ分が閾値を下回ったとき、フラグを立てる
  if (noise < THRESHOLD_A_) {
    // 誤検出防止のため、直前のパルス検出から一定時間経過後のみフラグを立てる
    if (time_us - last_pulse_time_us_ > PULSE_IGNORE_DURATION_US_) {
      reach_threshold_flag_ = true;
    }
  }
  // フラグが立った状態でノイズ分が0に戻ったら、1パルス検出
  if (reach_threshold_flag_ && noise > 0.0f) {
    pulse_count_ += 1;
    reach_threshold_flag_ = false;
    last_pulse_time_us_ = time_us;  // パルス検出時刻を記録
    // パルス検出回数が、モータ1回転分に達したら、回転数を積算する
    if (pulse_count_ == PULSE_PER_ROTATION_) {
      pulse_count_ = 0;
      total_rotation_ += 1;
      rps_ = 1.0f / (time_us - last_rotate_time_us_);
      last_rotate_time_us_ = time_us;
    }
  }
}

unsigned int MotorRotationDetector::getTotalRotation() {
  return total_rotation_;
}

unsigned int MotorRotationDetector::getRotation() {
  unsigned int retval = total_rotation_ - last_rotation_;
  last_rotation_ = total_rotation_;
  return retval;
}

float MotorRotationDetector::getRps() {
  return rps_;
}

float MotorRotationDetector::getNoise() {
  return noise;
}