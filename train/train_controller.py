import serial
import time

old_time = 0
new_time = 0

def send(message,ser):
    # messageを基地局に送信する
    ser.write(bytes(message,'ascii'))
    
def receive(ser):
    # 基地局からmessageを受信する
    message=ser.readline()
    message_string=message.decode('utf-8')
    return message_string

if __name__ == "__main__": 
    try:
        port = '/dev/tty.usbserial-14320' # ポート名は環境に合わせて変更する
        baudrate = 115200
        ser = serial.Serial(port, baudrate,timeout=3.0,write_timeout=3.0)
        ser.read_until(b'}')
        time.sleep(1)
        while(True):
            new_time = time.time()
            if new_time - old_time > 1:
                motorInput = 170
                json_data=f'{{"mI":{motorInput}}}'
                # print(json_data)
                send(json_data,ser)
                old_time = new_time

            if (receive(ser)):
                print(receive(ser), end='')

    except:
        motorInput = 0
        json_data=f'{{"mI":{motorInput}}}'
        print(json_data)
        send(json_data,ser)
        ser.close()