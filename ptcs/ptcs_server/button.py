import json
import logging
import threading
from typing import Any, Callable, Optional
import serial.tools.list_ports


ButtonCallback = Callable[[Any], None]


class Button:
    callback: ButtonCallback
    thread: Optional[threading.Thread]

    def __init__(self, port: str, callback: ButtonCallback) -> None:
        baudrate = 115200
        self.serial = serial.Serial(port, baudrate, timeout=3.0)
        self.callback = callback
        self.thread = None

    def print_ports(self) -> None:
        print("ports:")
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"  {p}")

    def start(self) -> None:
        """
        送受信スレッドを開始する。
        """
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        self.thread = thread

    def close(self) -> None:
        self.serial.close()

    def _run(self) -> None:
        """
        スレッドの中身。
        ブリッジから受信したデータがあれば、コールバックを呼び出す。
        送信キューにデータがあれば、ブリッジに送信する。
        """

        while True:
            # 受信
            if self.serial.in_waiting:
                message = self.receive()
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