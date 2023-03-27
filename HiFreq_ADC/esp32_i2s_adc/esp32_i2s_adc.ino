/*
 * ファイル>スケッチ例>ESP32>I2S>HiFreq_ADCを参考に作成した。
 * I2Sを用いて高速かつ等間隔にAD変換を行い、データをシリアルに出力する。
 * 
 * 読み取った値を記録しておくメモリであるbufferは2面ある。I2Sがreader内で1面にデータを記録している間、
 * もう1面に記録されたデータをloop内で読み出してシリアルで送信する。
 * シリアルの速度は 1000000bps ないと読み取り速度に追い付けないので注意
 */

#include <arduinoFFT.h>
#include <BluetoothSerial.h>
#include <driver/i2s.h>
#include <soc/syscon_reg.h>

#define SAMPLING_RATE 10000  // AD変換のサンプリングレート[Hz]
#define ADC_N_CHANNEL 2      // AD変換したい信号の数。電圧と電流なので2つ
#define ADC_CH_CURRENT ADC1_CHANNEL_4 //pin 32
#define ADC_CH_VOLTAGE ADC1_CHANNEL_5 //pin 33
#define MEM_SIDE 2
#define MEM_LENGTH 1024
#define N_MEDIAN 5
#define I2S_SAMPLE_RATE (SAMPLING_RATE * ADC_N_CHANNEL)  // I2Sのサンプリングレート[Hz]. 10000以上でないとうまく動かない
#define I2S_BUF_LENGTH (MEM_LENGTH * ADC_N_CHANNEL)

#define SERIAL_BUF_LEN 16

arduinoFFT FFT;
BluetoothSerial SerialBT;

const int PWM_PIN = 25;
const int PWM_CHANNEL = 0;
const uint32_t PWM_FREQ = 20000;

int pwm_duty = 0;

uint8_t flag_read_done = 0;
uint8_t mem_side = 0;
uint16_t buffer[MEM_SIDE][I2S_BUF_LENGTH];
uint32_t sequence_num = 0;

double vec_current_real[MEM_LENGTH];     // Real part of Current Vector
double vec_current_imag[MEM_LENGTH];     // Imaginal part of Current Vector
uint16_t vec_voltage[MEM_LENGTH];   // voltage vector

double vec_current[N_MEDIAN];
double vec_freq[N_MEDIAN];
int i_median = 0;

double median(double* vec) {
  // 渡された配列vecをコピー
  double data[N_MEDIAN];
  for (int i=0; i<N_MEDIAN; i++) {
    data[i] = vec[i];
  }

  // データを大きさの順に並べ替え
  double tmp;
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

void i2sInit()
{
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN),
    .sample_rate =  I2S_SAMPLE_RATE,              // The format of the signal using ADC_BUILT_IN
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT, // is fixed at 12bit, stereo, MSB
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 8,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_adc_mode(ADC_UNIT_1, ADC_CH_CURRENT);
  i2s_set_adc_mode(ADC_UNIT_1, ADC_CH_VOLTAGE);
  i2s_adc_enable(I2S_NUM_0);
  // ADCのチャンネルとアッテネータ設定
  // channel 4 at 12bits with 0db attenuation
  // channel 5 at 12bits with 0db attenuation
  uint32_t patt_tab1 = (((ADC_CH_CURRENT << 4) + 0b1100) << 24) + (((ADC_CH_VOLTAGE << 4) + 0b1100) << 16);
  WRITE_PERI_REG(SYSCON_SARADC_SAR1_PATT_TAB1_REG, patt_tab1);
  // 入力チャンネル数の設定
  *((uint32_t*)SYSCON_SARADC_CTRL_REG) |= ((ADC_N_CHANNEL - 1) << 15);
}

void reader(void *pvParameters) {
  size_t bytes_read;
  while(1){
    i2s_read(I2S_NUM_0, buffer[mem_side], I2S_BUF_LENGTH * sizeof(uint16_t), &bytes_read, portMAX_DELAY);
    mem_side = (mem_side + 1) % MEM_SIDE;
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
    uint8_t idle_mem_side = (mem_side + 1) % MEM_SIDE;  // いま書き込み中でないmem_sideを取得
    for (int i=0; i<I2S_BUF_LENGTH; i++) {  // コピー
      uint16_t data = buffer[idle_mem_side][i] & 0xFFF;
      uint8_t channel = (buffer[idle_mem_side][i] >> 12) & 0xF;
      if (channel == ADC_CH_CURRENT) {
        vec_current_real[i / ADC_N_CHANNEL] = data;
        vec_current_imag[i / ADC_N_CHANNEL] = 0.0f;
      } else if (channel == ADC_CH_VOLTAGE) {
        vec_voltage[i / ADC_N_CHANNEL] = data;
      }
    }

    // print value through Serial
    // (serial speed should be 1Mbps or more)
    /*
    for (int i=0; i<MEM_LENGTH; i++) {
      Serial.print(vec_current_real[i]);
      Serial.print(",");
      Serial.println(vec_voltage[i]);
    }
    */

    // Average current
    double mean = 0.0f;
    for (int i=0; i<MEM_LENGTH; i++) {
      mean += vec_current_real[i];
    }
    mean /= MEM_LENGTH;

    // Fourier transform (apply Hamming windowing)
    FFT = arduinoFFT(vec_current_real, vec_current_imag, MEM_LENGTH, SAMPLING_RATE);
    FFT.Windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.Compute(FFT_FORWARD); // calculate FT
    FFT.ComplexToMagnitude(); // mag. to vR 1st half
    double peak = FFT.MajorPeak(); // get peak freq

    // median
    vec_current[i_median] = mean;
    vec_freq[i_median] = peak;
    i_median = (i_median + 1) % N_MEDIAN;
    
    Serial.print(median(vec_freq));
    Serial.print(",");
    Serial.println(median(vec_current));
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
//    Serial.println(pwm_duty);
    ledcWrite(PWM_CHANNEL, pwm_duty);
  }
  
  delay(1);
}
