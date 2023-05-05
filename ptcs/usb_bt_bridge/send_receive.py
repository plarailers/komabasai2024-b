import serial
import time

def send(message,ser):
    # messageをArduinoに送信する
    ser.write(bytes(message,'ascii'))
    #ser.flush()
def receive(ser):
    message=ser.readline()
    message_string=message.decode('utf-8')
    return message_string

if __name__ == "__main__": 
    i=0
    port = '/dev/cu.usbserial-5' # ポート名は環境に合わせて変更する
    baudrate = 115200
    ser = serial.Serial(port, baudrate,timeout=3.0,write_timeout=3.0)
    ser.read_until(b'}')
    time.sleep(3)
    while(True):
        time.sleep(0.3)
        i+=1
        json_data=f'{{"key": 51, "value": {i} }}'
        print(json_data)
        send(json_data,ser)
        print(receive(ser))
    ser.close()
    
    #message=receive(ser)