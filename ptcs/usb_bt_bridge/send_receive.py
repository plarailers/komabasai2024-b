import serial


def send(message):
    # Arduinoとのシリアル通信用のポートとボーレートを指定する
    port = '/dev/tty.usbserial-110' # ポート名は環境に合わせて変更する
    baudrate = 115200
    # シリアルポートを開く
    ser = serial.Serial(port, baudrate)
    # messageをArduinoに送信する
    ser.write(bytes(str(message),'ascii'))
if __name__ == "__main__": 
    send('K')
