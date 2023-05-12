import serial
import time
import json

old_time = 0
new_time = 0
mileage_cm_ = 0.0

GEAR_RATIO = 175/8448
WHEEL_DIAMETER_cm_ = 2.4
PI = 3.14159265358979


def send(message,ser):
    # messageを基地局に送信する
    ser.write(bytes(message,'ascii'))
    
def receive(ser):
    # 基地局からmessageを受信する
    message=ser.readline()
    message_string=message.decode('utf-8')
    return message

if __name__ == "__main__": 
    try:
        port = '/dev/tty.usbserial-144130' # ポート名は環境に合わせて変更する
        baudrate = 115200
        ser = serial.Serial(port, baudrate,timeout=3.0,write_timeout=3.0)
        ser.read_until(b'}')
        time.sleep(3)
        while(True):
            new_time = time.time()
            dt = new_time - old_time

            if dt > 1:
                motorInput = 100
                json_data=f'{{"mI":{motorInput}}}'
                # print(json_data)
                send(json_data,ser)
                old_time = new_time

            recv_message = receive(ser)
            if (recv_message):
                try:
                    recv_data = json.loads(recv_message)
                    print(recv_data)
                    keys = recv_data.keys()
                    if 'mR' in keys:
                        motorRotation = recv_data['mR']
                        mileage_cm_ += motorRotation * GEAR_RATIO * WHEEL_DIAMETER_cm_ * PI
                    if 'pID' in keys:
                        print(mileage_cm_)
                        mileage_cm_ = 0
                except json.decoder.JSONDecodeError:
                    print("[main] json decode failed. recv_message is: ")
                    print(recv_message)
                    pass  # デコードできなかった場合は何もしない

    except:
        motorInput = 0
        json_data=f'{{"mI":{motorInput}}}'
        print(json_data)
        send(json_data,ser)
        ser.close()