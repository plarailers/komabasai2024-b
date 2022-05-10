from Operation import *
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import threading

# 自動運転システムの初期化
operation = Operation()
operation.state.communication.setup(simulationMode=True)

# Flaskウェブサーバの初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 自動運転システムが0.1secおきに実行する作業
def operation_loop():
    while True:
        operation.update()
        time.sleep(0.1)

# ブラウザにwebsocketで0.1secおきに信号を送る関数
def send_signal_to_browser():
    while True:
        socketio.sleep(0.1)
        train_taiken = operation.state.getTrainById(1)
        signal = operation.signalSystem.getSignal(train_taiken.currentSection.id, train_taiken.currentSection.targetJunction.getOutSection().id)
        
        # websocketで送信
        socketio.emit('signal_taiken', {
            'signal': signal
        })

@app.route('/')
def index():
    # ブラウザへデータを送信するタスクの開始
    socketio.start_background_task(target=send_signal_to_browser)
    # ブラウザにwebページのデータを返す
    return Response(response='central_controller の Flask ウェブサーバは正常に稼働しています', status=200)

if __name__ == "__main__":
    thread1 = threading.Thread(target=operation_loop, daemon=True)
    thread1.start()  # 自動運転のオペレーションを開始
    socketio.run(app, host='0.0.0.0', port=50050)  # Flaskソケットを起動
