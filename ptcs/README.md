# Plarailers Train Control System (仮)

列車制御システム (作成中)

## フォルダ構造

各要素を分離しつつもフォルダ構造を深くしすぎないために、このディレクトリは Poetry プロジェクトと npm プロジェクトのヘテロになっています。

- `ptcs_server` (Poetry)
- `ptcs_ui` (npm)

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
