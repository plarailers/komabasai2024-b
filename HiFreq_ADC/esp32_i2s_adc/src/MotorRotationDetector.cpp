#include "MotorRotationDetector.h"

MotorRotationDetector::MotorRotationDetector()
: PULSE_PER_ROTATION_(6),
  PULSE_IGNORE_DURATION_US_(500),
  THRESHOLD_A_(-0.03f),
  reach_threshold_flag_(false),
  pulse_count_(0),
  time_from_pulse_us_(0),
  time_from_rotate_us_(0),
  total_rotation_(0),
  last_rotation_(0),
  rps_(0.0f)
{
  current_hpf_.setFc(3000.0f);
  for (int i = 0; i < AVERAGE_NUM_; i++) {
    rotate_time_us_list_[i] = UINT32_MAX;
  }
}

void MotorRotationDetector::update(float current_A, unsigned long period_us) {
  // 時間を積算
  time_from_pulse_us_ += period_us;
  time_from_rotate_us_ += period_us;
  // パルス間隔が100ms以上空いた場合は停止とみなす
  if (time_from_pulse_us_ > 100000) {
    rps_ = 0.0f;
  }
  // ハイパスフィルタでノイズ分を抽出
  float noise = current_hpf_.update(current_A, (float)period_us / 1e6);
  // ノイズ分が閾値を下回ったとき、フラグを立てる
  if (noise < THRESHOLD_A_) {
    // 誤検出防止のため、直前のパルス検出から一定時間経過後のみフラグを立てる
    if (time_from_pulse_us_ > PULSE_IGNORE_DURATION_US_) {
      reach_threshold_flag_ = true;
    }
  }
  // フラグが立った状態でノイズ分が0に戻ったら、1パルス検出
  if (reach_threshold_flag_ && noise > 0.0f) {
    pulse_count_ += 1;
    reach_threshold_flag_ = false;
    time_from_pulse_us_ = 0;  // パルス検出からの経過時間をリセット
    // パルス検出回数が、モータ1回転分に達したら、回転数を積算する
    if (pulse_count_ == PULSE_PER_ROTATION_) {
      total_rotation_ += 1;  // 回転数の積算
      pulse_count_ = 0;

      // 1回転にかかった時間を記録する。AVERAGE_NUM_個の平均を取りたいので、リストの
      // 1番目を2番目にずらし、0番目を1番目にずらし、0番目に最新の時間を記録する
      for (int i = AVERAGE_NUM_ - 1; i >= 1; i--) {
        rotate_time_us_list_[i] = rotate_time_us_list_[i - 1];
      }
      rotate_time_us_list_[0] = time_from_rotate_us_;
      // 1回転にかかった時間をリセット
      time_from_rotate_us_ = 0;

      // AVERAGE_NUM_回だけ回転するのにかかった時間を求め、平均速度を計算
      unsigned long rotate_time_sum = 0;  
      for (int i = 0; i < AVERAGE_NUM_; i++) {
        rotate_time_sum += rotate_time_us_list_[i];
      }
      rps_ = 1000000.0f / rotate_time_sum * AVERAGE_NUM_;
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
