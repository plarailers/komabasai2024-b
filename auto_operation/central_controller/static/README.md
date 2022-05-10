# online
オンライン運転体験用のソースコードを置いたフォルダ。

## なかみ
### controller.html
(式部)ユーザーが操作するサイト。
ハンドルに見立てたスライダをユーザーが動かすと、<input type="range" id="speed" ...> のValueが、0-255の間で変化します。

### style.css
(式部)controller.htmlのスタイルシート。

### loaders.min.css
(式部)ローディング中にチカチカするやつのCSS。https://connoratherton.com/loaders より。

### viewer.js
(三浦)WebRTCで動画をストリーミング再生する処理をまとめたもの。詳細は /live-streaming 以下。