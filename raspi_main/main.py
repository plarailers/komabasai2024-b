#!/usr/bin/env python3

import subprocess
import re
import os.path
import time
from queue import Queue
import serial

MOMO_BIN = os.path.expanduser('~/momo-2020.8.1_raspberry-pi-os_armv6/momo')

process_socat = None
process_momo = None
port = None

recv_queue = Queue()
send_queue = Queue()

def setup():
    global process_socat, process_momo, port
    print('starting...')
    process_socat = subprocess.Popen(['socat', '-d', '-d', 'pty,raw,echo=0', 'pty,raw,echo=0'], stderr=subprocess.PIPE)
    port1_name = re.search(r'N PTY is (\S+)', process_socat.stderr.readline().decode()).group(1)
    port2_name = re.search(r'N PTY is (\S+)', process_socat.stderr.readline().decode()).group(1)
    process_socat.stderr.readline()
    print('using ports', port1_name, 'and', port2_name)
    process_momo = subprocess.Popen([MOMO_BIN, '--no-audio-device', '--use-native', '--force-i420', '--serial', f'{port1_name},9600', 'test'])
    port = serial.Serial(port2_name, 9600)
    print('started')
    print('running at http://raspberrypi.local:8080/')
    print('ctrl+c to quit')

def loop():
    while port.in_waiting > 0:
        data = port.read()
        print(data)

    while not send_queue.empty():
        data = send_queue.get()
        port.write(data)
        port.flush()

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
        if port:
            port.close()
        if process_momo:
            process_momo.terminate()
        if process_socat:
            process_socat.terminate()
