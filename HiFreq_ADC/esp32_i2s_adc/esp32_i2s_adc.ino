/*
 * ファイル>スケッチ例>ESP32>I2S>HiFreq_ADCを参考に作成した。
 * I2Sを用いて高速かつ等間隔にAD変換を行い、データをシリアルに出力する。
 * 
 * 読み取った値を記録しておくメモリであるbufferは2面ある。I2Sがreader内で1面にデータを記録している間、
 * もう1面に記録されたデータをloop内で読み出してシリアルで送信する。
 * シリアルの速度は 1000000bps ないと読み取り速度に追い付けないので注意
 */

#include <BluetoothSerial.h>
#include <driver/i2s.h>
#include <soc/syscon_reg.h>

#define I2S_SAMPLE_RATE 10000  // サンプリングレート[Hz]/2. 10000以上でないとうまく動かない
#define ADC_INPUT ADC1_CHANNEL_4 //pin 32
#define MEM_SIDE 2
#define MEM_LENGTH 10000

#define SERIAL_BUF_LEN 16
const int PWM_PIN = 25;
const int PWM_CHANNEL = 0;
const uint32_t PWM_FREQ = 20000;

int pwm_duty = 0;

BluetoothSerial SerialBT;

uint8_t flag_read_done = 0;
uint8_t mem_side = 0;
uint16_t buffer[MEM_SIDE][MEM_LENGTH];
uint16_t buffer_for_print[MEM_LENGTH];
uint32_t sequence_num = 0;

void i2sInit()
{
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN),
    .sample_rate =  I2S_SAMPLE_RATE,              // The format of the signal using ADC_BUILT_IN
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT, // is fixed at 12bit, stereo, MSB
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 8,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_adc_mode(ADC_UNIT_1, ADC_INPUT);
  i2s_adc_enable(I2S_NUM_0);
  // ADCのアッテネータ変更。channel 4 at 12bits with 0db attenuation
  WRITE_PERI_REG(SYSCON_SARADC_SAR1_PATT_TAB1_REG, 0x4C000000);
}

void reader(void *pvParameters) {
  uint32_t read_counter = 0;
  uint64_t read_sum = 0;
  size_t bytes_read;
  while(1){
    i2s_read(I2S_NUM_0, buffer[mem_side], MEM_LENGTH * sizeof(uint16_t), &bytes_read, portMAX_DELAY);
    mem_side = (mem_side + 1) & 1;
    flag_read_done = 1;
    sequence_num += 1;
  }
}

void setup() {
  Serial.begin(1000000);
  ledcSetup(PWM_CHANNEL, PWM_FREQ, 8);
  ledcAttachPin(PWM_PIN, PWM_CHANNEL);
  ledcWrite(PWM_CHANNEL, pwm_duty);
  
  SerialBT.begin("Bluetooth-Oscillo");
  
  // Initialize the I2S peripheral
  i2sInit();
  
  // Create a task that reads the data
  xTaskCreatePinnedToCore(reader, "ADC_reader", 2048, NULL, 1, NULL, 1);

  Serial.println("setup end");
}

void loop() {
  
  // -----------
  // ADC reading
  // -----------
  if (flag_read_done == 1) {
    flag_read_done = 0;
    
    // copy data stored in the memory
    uint8_t idle_mem_side = (mem_side + 1) & 1;  // いま書き込み中でないほうのmem_sideを取得
    for (int i=0; i<MEM_LENGTH; i++) {  // コピー
      buffer_for_print[i] = buffer[idle_mem_side][i] & 0xFFF;
    }
    
    // print value through Serial
    // (serial speed should be 1Mbps or more)
    for (int i=0; i<MEM_LENGTH; i++) {
      Serial.println(buffer_for_print[i]);
    }
  }

  // ------------------------------------
  // Motor duty command receive and apply
  // ------------------------------------
  byte buf[SERIAL_BUF_LEN];
  memset(buf, 0, SERIAL_BUF_LEN);
  
  int i = 0;
  if (Serial.available()){
    while(Serial.available()) {
      buf[i] = Serial.read();
      i++;
      if (i >= SERIAL_BUF_LEN) {
        break;
      }
    }
    sscanf((char*)buf, "%d", &pwm_duty);
    Serial.println(pwm_duty);
    ledcWrite(PWM_CHANNEL, pwm_duty);
  }
  
  delay(1);
}
