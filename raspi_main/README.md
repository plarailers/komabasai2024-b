# raspi_main

- main.py
  - Raspberry Pi 上で動かすスクリプト。ビデオの送信、メッセージの送受信、GPIO の操作を行う。
- index.html
  - Raspberry Pi で配信し、PC のブラウザ上で動かす。ビデオの受信、メッセージの送受信を行う。

## Raspberry Pi 側で必要なライブラリ

```
sudo apt install socat
pip3 install pyserial
```

## PC から Raspberry Pi へのファイル転送

```
scp -r ./raspi_main pi@raspberrypi.local:~/
```

## 実行

```
cd raspi_main
python3 main.py
```

http://raspberrypi.local:8080/ にアクセスする。
