import serial

# arduinoと繋いでいるportの名前に変更すること
PORT = "/dev/cu.usbserial-130"
arduino = serial.Serial(PORT, 9600)

while True:
    servo_id = int(input(f'servo_id (0~3): '))
    servo_state = int(input(f'sensor_state (straight: 0, curve: 1): '))
    arduino.write(servo_id.to_bytes(1, 'little'))
    arduino.write(servo_state.to_bytes(1, 'little'))