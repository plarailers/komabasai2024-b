# experimental/esp_eye_camera

ESP-EYE のカメラで取った映像を Wi-Fi 経由でブラウザにストリーミング配信する。

## フォルダ構造
- CameraWebServer
  - Arduino IDE を使って ESP-EYE に書き込むプログラム
- static
  - CameraWebServer が配信している HTML の中身

## 使い方

- Arduino IDE を入れる
  - ここから：https://www.arduino.cc/en/software
- ESP32 用のボードマネージャを追加
  - 「ファイル > 環境設定」を開き、「追加のボードマネージャ」 の URL に https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json を追加
  - 「ツール > ボード > ボードマネージャ」を開き、「esp32 by Espressif Systems」をインストール
- 書き込み設定
  - ボードは「ESP32 Wrover Module」を選択
  - 正しい COM ポートを選択
  - 「Partition Scheme」には「Huge APP (3MB No OTA)」を選択（今回のサンプルプログラムが非常に大きな ROM を使うため）
- このフォルダの CameraWebServer/CameraWebServer.ino を開く
- Wi-Fi 設定
  - CameraWebServer.ino の 36, 37 行目の以下の部分を、接続したい Wi-Fi の SSID とパスワードに置き換える
```ino
const char* ssid = "**********";
const char* password = "**********";
```
- 書き込む
- シリアルモニタを開く
  - 周波数は 115200 bps
  - 「...」が出ている間は Wi-Fi を探している
  - 表示された URL にアクセス
- ブラウザを確認
  - 「Start Stream」を押す
- 動く

## 開発する人向け情報

- CameraWebServer の中身はこれ
  - https://github.com/espressif/arduino-esp32/tree/2.0.4/libraries/ESP32/examples/Camera/CameraWebServer
  - 「ファイル > スケッチ例 > ESP32 Wrover Module用のスケッチ例 > ESP32 > Camera > CameraWebServer」からも開ける
  - ここにカメラモデルの設定を ESP-EYE 用にする変更を加えた
- CameraWebServer/camera_index.h には gzip 圧縮された HTML が埋め込まれているが、それを展開したものを static/ 以下に置いたので参考にどうぞ
