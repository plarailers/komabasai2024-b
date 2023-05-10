import serial

arduino = serial.Serial("/dev/cu.usbmodem11301", 9600)

while True:
    servo_id = int(input(f'servo_id (0~3): '))
    servo_state = int(input(f'sensor_state (straight: 0, curve: 1): '))
    arduino.write(servo_id.to_bytes(1, 'little'))
    arduino.write(servo_state.to_bytes(1, 'little'))