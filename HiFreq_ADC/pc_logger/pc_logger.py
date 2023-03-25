# シリアル通信で受け取った値を、ファイルに記録するためのスクリプト

import keyboard
import serial

ser = serial.Serial('COM3', 1000000)
ser.rtscts=False
ser.dsrdtr=False
ser.rts=False
ser.dtr=False

n = 0
file_path = 'HiFreq_ADC/pc_logger/log.txt'

with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
    while n < 50000:
        val = ser.readline().decode('utf-8')
        f.write(val)
        n = n + 1
        if keyboard.is_pressed("c"):
            break

ser.close()
