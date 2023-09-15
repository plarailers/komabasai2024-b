# ptcs_control

## 構造

- `control.py`
  - 列車制御システムの全体
- `mft2023.py`
  - MFT2023 特有の設定
- `constants.py`
  - 定数
- `components/`
  - `components/base.py`
    - 各コンポーネントの基底クラス
  - `components/junction.py`
    - 分岐・合流点
  - `components/section.py`
    - 区間
  - `components/train.py`
    - 列車
  - `components/stop.py`
    - 停止目標
  - `components/station.py`
    - 駅
  - `components/sensor_position.py`
    - センサー位置
  - `components/position.py`
    - 汎用的な位置や方向
