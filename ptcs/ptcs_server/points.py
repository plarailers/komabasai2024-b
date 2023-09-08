import logging
import queue
import threading
from typing import Any, Optional

import serial.tools.list_ports

from ptcs_control.components import Direction


class PointSwitcher:
    serial: "serial.Serial"

    def __init__(self, port: str) -> None:
        baudrate = 9600
        self.serial = serial.Serial(port, baudrate, write_timeout=3.0)

    def send(self, message: tuple[int, int]) -> None:
        servo_id, servo_state = message
        self.serial.write(servo_id.to_bytes(1, "little"))
        self.serial.write(servo_state.to_bytes(1, "little"))
        self.serial.flush()

    def close(self) -> None:
        self.serial.close()


PointTarget = str
PointDict = dict[PointTarget, tuple[PointSwitcher, int]]


class PointSwitcherManager:
    points: PointDict
    send_queue: queue.Queue[tuple[PointTarget, Any]]
    send_thread: Optional[threading.Thread]

    def __init__(self) -> None:
        self.points = {}
        self.send_queue = queue.Queue()
        self.send_thread = None

    def print_ports(self) -> None:
        print("ports:")
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"  {p}")

    def print_points(self) -> None:
        print("points:")
        for key, value in self.points.items():
            print(f"  {key} = {value}")

    def register(self, target: PointTarget, point_switcher: PointSwitcher, servo_no: int) -> None:
        """
        ポイントを登録する。
        """
        self.points[target] = (point_switcher, servo_no)

    def start(self) -> None:
        """
        送信スレッドを開始する。
        """
        send_thread = threading.Thread(target=self._run_send, daemon=True)
        send_thread.start()
        self.send_thread = send_thread

    def _run_send(self) -> None:
        """
        送信スレッドの中身。
        送信キューにデータがあれば、arduinoに送信する。
        """

        while True:
            target, direction = self.send_queue.get()  # ブロッキング処理
            logging.info(f"SEND {target} {direction}")
            point_switcher, servo_no = self.points[target]
            servo_state = 0 if direction == Direction.STRAIGHT else 1
            point_switcher.send((servo_no, servo_state))

    def send(self, target: PointTarget, direction: Direction) -> None:
        """
        servoを繋いだarduino nano に向けて データ `direction` を送信する。
        (実際にはすぐに送信せず、送信キューに入れておく。)
        directionはDirection型を想定
        """
        self.send_queue.put((target, direction))
