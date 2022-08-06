# experimental/esp_eye_viewer

[experimental/esp_eye_camera](../esp_eye_camera//README.md) の映像のみを抜き出す。

## 使い方

- [experimental/esp_eye_camera](../esp_eye_camera//README.md) を読んで、ESP-EYE でカメラサーバを立ち上げる
- PC でローカルサーバを立てる
  - VS Code なら Live Server プラグインを入れて Go Live を押す
  - Node.js なら `npx http-server`
  - Python なら `python3 -m http.server`
- index.html にアクセスし、入力欄に ESP-EYE の URL (http://～.～.～.～/) を入れる
- Start を押す

## 開発する人向けの情報

- `<img />` 要素の `src` に `http://{ESP-EYE の IP アドレス}:81/stream` を指定するだけでストリーミング配信されるらしい
