import serial
import time

def send(message,ser):
    # messageをArduinoに送信する
    ser.write(bytes(message,'ascii'))
    ser.flush()
    print("send")
    
def receive(ser):
    message=ser.readline()
    message_string=message.decode('utf-8')
    return message_string

if __name__ == "__main__": 
    port = '/dev/cu.usbserial-0001' # ポート名は環境に合わせて変更する
    baudrate = 115200
    ser = serial.Serial(port, baudrate,timeout=3.0,write_timeout=3.0)
    time.sleep(5)
    json_data='{ "key": 51, "value": 314 }'
    while(True):
        print("///")
        print(receive(ser))
    ser.close()
    
    #message=receive(ser)