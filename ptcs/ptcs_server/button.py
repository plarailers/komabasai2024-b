import json
import logging
import threading
from typing import Any, Callable, Optional

import serial.tools.list_ports

ButtonCallback = Callable[[Any], None]


class Button:
    callback: ButtonCallback
    recv_thread: Optional[threading.Thread]

    def __init__(self, port: str, callback: ButtonCallback) -> None:
        baudrate = 115200
        self.serial = serial.Serial(port, baudrate, timeout=3.0)
        self.callback = callback
        self.recv_thread = None

    def print_ports(self) -> None:
        print("ports:")
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"  {p}")

    def start(self) -> None:
        """
        受信スレッドを開始する。
        """
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        self.recv_thread = thread

    def close(self) -> None:
        self.serial.close()

    def _run(self) -> None:
        """
        受信スレッドの中身。
        ボタンから受信したデータがあれば、コールバックを呼び出す。
        """

        while True:
            if self.serial.in_waiting:
                message = self.receive()  # ブロッキング処理
                try:
                    data = json.loads(message)
                    logging.info(f"RECV {data}")
                    self.callback(data)
                except json.decoder.JSONDecodeError:
                    pass

    def receive(self) -> str:
        message = self.serial.readline()
        message_string = message.decode("utf-8")
        return message_string
