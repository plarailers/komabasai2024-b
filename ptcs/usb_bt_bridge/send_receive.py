import serial
import time

def send(message,ser):
    # messageを基地局に送信する
    ser.write(bytes(message,'ascii'))
    
def receive(ser):
    # 基地局からmessageを受信する
    message=ser.readline()
    message_string=message.decode('utf-8')
    return message_string

if __name__ == "__main__": 
    i=0
    port = '/dev/tty.usbserial-1440' # ポート名は環境に合わせて変更する
    baudrate = 115200
    ser = serial.Serial(port, baudrate,timeout=3.0,write_timeout=3.0)
    ser.read_until(b'}')
    time.sleep(3)
    while(True):
        time.sleep(0.3)
        print("motorInput: ", end='')
        motorInput = input()
        json_data=f'{{"motorInput": {motorInput}}}'
        print(json_data)
        send(json_data,ser)
        print(receive(ser))
    ser.close()