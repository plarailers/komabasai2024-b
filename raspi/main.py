#!/usr/bin/env python3

import subprocess
import re
import os.path
import time
import datetime
import RPi.GPIO as GPIO
import serial
import asyncio
import websockets
from collections import deque

MOTOR_PIN = 10
SENSOR_PIN = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN, GPIO.OUT)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

motor = GPIO.PWM(MOTOR_PIN, 50)

MOMO_BIN = os.path.expanduser('~/momo-2020.8.1_raspberry-pi-os_armv6/momo')

process_socat = None
process_momo = None
port = None

def setup():
    global process_socat, process_momo, port, controlled_speed_queue
    print('starting...')
    process_socat = subprocess.Popen(['socat', '-d', '-d', 'pty,raw,echo=0', 'pty,raw,echo=0'], stderr=subprocess.PIPE)
    port1_name = re.search(r'N PTY is (\S+)', process_socat.stderr.readline().decode()).group(1)
    port2_name = re.search(r'N PTY is (\S+)', process_socat.stderr.readline().decode()).group(1)
    process_socat.stderr.readline()
    print('using ports', port1_name, 'and', port2_name)
    process_momo = subprocess.Popen([MOMO_BIN, '--no-audio-device', '--use-native', '--force-i420', '--serial', f'{port1_name},9600', 'test'])
    port = serial.Serial(port2_name, 9600)
    controlled_speed_queue = deque()
    motor.start(0)
    GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=on_sensor, bouncetime=10)
    print('started')
    print('motor:', MOTOR_PIN)
    print('sensor:', SENSOR_PIN)
    print('running at http://raspberrypi.local:8080/')
    print('Ctrl+C to quit')

def on_sensor(channel):
    data = b'o\n'
    port.write(data)
    port.flush()
    print(datetime.datetime.now(), 'send sensor', data)

async def receive_controlled_speed():
    # wsで受信したスピードをqueueに入れる
    ws_uri = 'ws:' #URIを埋める必要あり
    async with websockets.connect(ws_uri) as websocket:
        speed = await websocket.recv()
        controlled_speed_queue.append(speed)

def loop():
    while port.in_waiting > 0:
        data = port.read()
        speed = data[0]
        # 制御システムからスピードを受信していれば、運転体験と比較して遅い方を採用
        if len(controlled_speed_queue):
            controlled_speed = controlled_speed_queue.popleft()
            speed = min(speed, controlled_speed)
        dc = speed * 100 / 255
        motor.ChangeDutyCycle(dc)
        print(datetime.datetime.now(), 'receive speed', speed)

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print('interrupted')
    except Exception as e:
        print(e)
    finally:
        motor.stop()
        GPIO.cleanup()
        if port:
            port.close()
        if process_momo:
            process_momo.terminate()
        if process_socat:
            process_socat.terminate()
