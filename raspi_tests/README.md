# raspi_tests

ラズパイの動作確認用

- led.py
  - Lチカ（点滅）
  - GPIO 14番ピンで出力
- pwm.py
  - Lチカ（PWM）
  - GPIO 14番ピンで出力
- hall.py
  - センサ読み取り
  - GPIO 17番ピンで入力

## PC から Raspberry Pi へのファイル転送

```
scp -r ./raspi_tests pi@raspberrypi.local:~/
```
