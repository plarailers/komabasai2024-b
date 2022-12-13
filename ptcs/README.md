# Plarailers Train Control System (仮)

列車制御システム (作成中)

## フォルダ構造

各要素を分離しつつもフォルダ構造を深くしすぎないために、このディレクトリは Poetry プロジェクトと npm プロジェクトのヘテロになっています。

- `ptcs_control` (Poetry)
  - 列車の制御アルゴリズム
- `ptcs_server` (Poetry)
  - `ptcs_control` から取得したシステムの状態を `ptcs_ui` に配信したり、指示を送ったりする
- `ptcs_ui` (npm)
  - `ptcs_server` から取得したシステムの状態をブラウザに表示したり、指示を送ったりする

## 使用者向け

### 最初にやること

Python と Poetry が必要です。

```bash
pip install poetry
```

### インストール

```bash
poetry install
```

### システム起動

```bash
poetry run server serve
```


## 開発者向け

使用者向けにはあらかじめビルドされた UI が `ptcs_ui/build` に入る (予定) ですが、開発するときには開発サーバーを立てることができます。

### インストール

```bash
poetry install
npm install
```

### 開発サーバー起動

```bash
# ptcs_server を起動
poetry run server serve

# ptcs_ui を起動
npm run ui:dev
```
