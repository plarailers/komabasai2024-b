#include "HighSpeedAnalogRead.h"

#include <driver/i2s.h>
#include <soc/syscon_reg.h>

HighSpeedAnalogRead::HighSpeedAnalogRead()
: chNum_(0),
  sampleRateHz_(0),
  patternTable_{0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f,0x0f},
  readBuffer_{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
  taskHandle_(NULL),
  isrFunc_(NULL)
{}

int HighSpeedAnalogRead::addPin(uint8_t pin, adc_bits_width_t resolution, adc_atten_t attenuation) {
  if (chNum_ > 16) {
    return 0;
  }

  // pattern table の書式は、ESP32 Technical Reference Manual の
  // 29.3.5 DIG SAR ADC Controllers を参照。

  switch (pin) {
  case ADC1_CHANNEL_0_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_0 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  case ADC1_CHANNEL_1_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_1 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  case ADC1_CHANNEL_2_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_2 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  case ADC1_CHANNEL_3_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_3 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  case ADC1_CHANNEL_4_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_4 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  case ADC1_CHANNEL_5_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_5 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  case ADC1_CHANNEL_6_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_6 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  case ADC1_CHANNEL_7_GPIO_NUM:
    patternTable_[chNum_ - 1] = (ADC1_CHANNEL_7 << 4) + (resolution << 2) + attenuation;
    chNum_++;
    return 1;

  default:
    return 0;
  }
}

void HighSpeedAnalogRead::attachInterrupt(void (*func)(uint16_t* data, size_t chNum_)) {
  isrFunc_ = func;
}

void HighSpeedAnalogRead::setSampleRateHz(uint32_t sampleRateHz) {
  sampleRateHz_ = sampleRateHz;
}

int HighSpeedAnalogRead::start() {
  if (sampleRateHz_ > 0 && chNum_ >= 1 && chNum_ <= 16) {
    
    // i2sの設定
    i2s_config_t i2s_config;
    i2s_config.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN);
    i2s_config.sample_rate = sampleRateHz_ * chNum_;
    i2s_config.bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT;
    i2s_config.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
    i2s_config.communication_format = I2S_COMM_FORMAT_I2S_MSB;
    i2s_config.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
    i2s_config.dma_buf_count = 4;
    i2s_config.dma_buf_len = 8;
    i2s_config.use_apll = false;
    i2s_config.tx_desc_auto_clear = false;
    i2s_config.fixed_mclk = 0;

    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_adc_mode(ADC_UNIT_1, (adc1_channel_t)((patternTable_[0] & 0xf) >> 4));
    i2s_adc_enable(I2S_NUM_0);

    // 各入力チャンネルの情報を pattern table に設定
    uint32_t pattTab1 = (patternTable_[0] << 24) + (patternTable_[1] << 16) + (patternTable_[2] << 8) + patternTable_[3];
    uint32_t pattTab2 = (patternTable_[4] << 24) + (patternTable_[5] << 16) + (patternTable_[6] << 8) + patternTable_[7];
    uint32_t pattTab3 = (patternTable_[8] << 24) + (patternTable_[9] << 16) + (patternTable_[10] << 8) + patternTable_[11];
    uint32_t pattTab4 = (patternTable_[12] << 24) + (patternTable_[13] << 16) + (patternTable_[14] << 8) + patternTable_[15];
    WRITE_PERI_REG(SYSCON_SARADC_SAR1_PATT_TAB1_REG, pattTab1);
    WRITE_PERI_REG(SYSCON_SARADC_SAR1_PATT_TAB2_REG, pattTab2);
    WRITE_PERI_REG(SYSCON_SARADC_SAR1_PATT_TAB3_REG, pattTab3);
    WRITE_PERI_REG(SYSCON_SARADC_SAR1_PATT_TAB4_REG, pattTab4);

    // 入力チャンネル数の設定
    *((uint32_t*)SYSCON_SARADC_CTRL_REG) |= ((chNum_ - 1) << 15);

    // 読み取りタスクの開始
    xTaskCreatePinnedToCore(reader_, "ADC_reader", 2048, this, 1, &taskHandle_, 1);
  }
}

void HighSpeedAnalogRead::stop() {
  vTaskSuspend(taskHandle_);
  vTaskDelete(taskHandle_);
  i2s_adc_disable(I2S_NUM_0);
  i2s_driver_uninstall(I2S_NUM_0);
  chNum_ = 0;
  sampleRateHz_ = 0;
  memset(patternTable_, 0x0f, sizeof(uint8_t) * 16);
  memset(readBuffer_, 0x00, sizeof(uint16_t) * 16);
  taskHandle_ = NULL;
  isrFunc_ = NULL;
}

void HighSpeedAnalogRead::reader_(void* ptrToThisInstance) {
  HighSpeedAnalogRead* p = reinterpret_cast<HighSpeedAnalogRead*>(ptrToThisInstance);
  size_t bytes_read;
  while(1) {
    // チャンネル数分のデータを読む
    i2s_read(I2S_NUM_0, p->readBuffer_, p->chNum_ * sizeof(uint16_t), &bytes_read, portMAX_DELAY);
    // 割り込み関数にデータを渡して実行する
    if (p->isrFunc_ != NULL) {
      p->isrFunc_(p->readBuffer_, p->chNum_);
    }
  }
}
