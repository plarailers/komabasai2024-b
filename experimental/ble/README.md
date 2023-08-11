# experimental/ble

Bluetooth Low Energy に関する実験。

## フォルダ構造
- peripheral
  - Arduino IDE を使って ESP32 DevKitC に書き込むプログラム
- central
  - PC 側で動かすプログラム

## 使い方

peripheral/peripheral.ino を ESP32 に書き込むと、サーバーが立ち、advertising が始まる。

PC 側で

```bash
cd central
pip install -r requirements.txt
python main.py
```

を実行すると、scan した後、クライアントとして ESP32 に接続する。

接続後、1秒に1回、セントラルからペリフェラルにメッセージが送られる。

## 開発する人向け情報

- ESP32 のアドレス
  - E5: `9c:9c:1f:cb:d9:f2`

- Service ID と Characteristic ID (勝手に決めてよい)
  - Service ID: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
  - Characteristic ID: `beb5483e-36e1-4688-b7f5-ea07361b26a8`

- ペリフェラル側ライブラリ
  - https://github.com/espressif/arduino-esp32/tree/master/libraries/BLE
- セントラル側ライブラリ
  - https://bleak.readthedocs.io/
