# 自動運転プログラム
## 中身
### com_to_arduino/com_to_arduino.ino (谷口)
  - Arduinoによるサーボとセンサの制御プログラム
  - junctionId を受け取り、ポイントを切り替える。
  - CdSが車両の通過を検知したとき、通過したCdSの sensorId を送る。

### gui_web
列車の位置表示や指令を行うGUI

### system_on_raspi
自動運転システム

- Communication.py (三浦)
  - ESP32およびArduinoとの通信プログラム。
  - ESP32へinputを送り、ESP32からホールセンサの信号を受け取る。
  - Arduinoとの通信。切り替えるポイントの junctionId を送り、検知された sensorId を受け取る。
  - simulationMode = true にすると、実機が無くてもシミュレーションできる。
  - **環境によってCOMポート番号の書き換えなどが必要**
- main.py (松田)
  - コマンドラインから実行する。自動運転システム(Operation)の稼働と、WEBサーバとしてGUIへの情報配信(Server)を行う
- Server.py (松田)
  - GUIに情報を送る
- Operation.py (松田)
  - 自動運転システムの最上位プログラム
  - Communication から受け取ったホールセンサ信号とセンサ信号(sensorId)を基にシミュレーションを更新。
  - 各車両の速度指令と、切り替えるポイントを計算し、内部モジュールのCommunicationを通してハードウェアに送信。
- その他の.pyファイル
  - 自動運転に用いられるモジュール。詳細は[五月祭2022列車制御システム構成図](https://docs.google.com/presentation/d/1fT75t7o4gi9V8cbwn1BwtUComzHEs0q3-pRfCk-om7c/edit?usp=sharing)を参照。
  - **State.pyは、線路形状に応じて書き換える**
  - **DiaPlanner.pyは、最初に列車を置いた場所に応じて書き換える**
