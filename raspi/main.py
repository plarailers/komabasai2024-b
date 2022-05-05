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

MOTOR_PIN = 19
SENSOR_PIN = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR_PIN, GPIO.OUT)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

motor = GPIO.PWM(MOTOR_PIN, 50)

MOMO_BIN = os.path.expanduser('~/momo-2020.8.1_raspberry-pi-os_armv6/momo')

process_socat = None
process_momo = None
port = None

def setup():
    global process_socat, process_momo, port, handle_speed, controlled_speed_queue
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
    handle_speed = 0
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

async def receive_controlled_speed(websocket, path):
    # wsで受信したスピードをqueueに入れる
    # raspiがサーバ側
    async for speed in websocket:
        controlled_speed_queue.append(int(speed))
        print(f"controlled speed received: {speed}")
        # print(f"typeof speed: {type(speed)}")

async def ws_receive():
    async with websockets.serve(receive_controlled_speed, "raspberrypi.local", 8765):
        await asyncio.Future()

def loop():
    speed = None
    controlled_speed = None
    global handle_speed

    if port.in_waiting <= 0 and not len(controlled_speed_queue):
        return

    if port.in_waiting > 0:
        while port.in_waiting > 0:
            data = port.read()
        handle_speed = data[0]

    if len(controlled_speed_queue):
        while len(controlled_speed_queue):
            controlled_speed = controlled_speed_queue.popleft()

    if controlled_speed is None:
        speed = handle_speed
    else:
        speed = min(handle_speed, controlled_speed)

    dc = speed * 100 / 255
    motor.ChangeDutyCycle(dc)
    print(datetime.datetime.now(), 'receive speed', speed)

async def async_loop():
    while True:
        loop()
        await asyncio.sleep(0.01)

if __name__ == '__main__':
    try:
        setup()
        event_loop = asyncio.get_event_loop()
        gather = asyncio.gather(
            async_loop(),
            ws_receive()
        )
        event_loop.run_until_complete(gather)
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
