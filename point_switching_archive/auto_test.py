import serial
from time import sleep

# 2秒おきにarduino nanoに繋いだ全てのサーボの向きを変更する検証用プログラム

# arduinoと繋いでいるportの名前に変更すること
PORT = "/dev/cu.usbserial-130"
arduino = serial.Serial(PORT, 9600)

while True:
    servo_ids = [0, 1, 2, 3]
    servo_states = [1, 1, 1, 1]
    for i in range(4):
        servo_id = servo_ids[i]
        servo_state = servo_states[i]
        arduino.write(servo_id.to_bytes(1, 'little'))
        arduino.write(servo_state.to_bytes(1, 'little'))

    sleep(2)

    servo_states = [0, 0, 0, 0]
    for i in range(4):
        servo_id = servo_ids[i]
        servo_state = servo_states[i]
        arduino.write(servo_id.to_bytes(1, 'little'))
        arduino.write(servo_state.to_bytes(1, 'little'))

    sleep(2)