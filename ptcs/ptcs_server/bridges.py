import json
import logging
import queue
import threading
from typing import Any, Callable, Optional

import serial.tools.list_ports

from ptcs_bridge.bridge import Bridge
from ptcs_control.components.sensor_position import SensorPosition

BridgeTarget = str
BridgeDict = dict[BridgeTarget, Bridge]
PositionDict = dict[int, SensorPosition]
BridgeCallback = Callable[[BridgeTarget, Any], None]


class BridgeManager:
    bridges: BridgeDict
    positions: PositionDict
    send_queue: queue.Queue[tuple[BridgeTarget, Any]]
    callback: BridgeCallback
    send_thread: Optional[threading.Thread]
    recv_thread: Optional[threading.Thread]

    def __init__(self, callback: BridgeCallback) -> None:
        self.bridges = {}
        self.positions = {}
        self.send_queue = queue.Queue()
        self.callback = callback
        self.send_thread = None
        self.recv_thread = None

    def print_ports(self) -> None:
        print("ports:")
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"  {p}")

    def print_bridges(self) -> None:
        print("bridges:")
        for key, value in self.bridges.items():
            print(f"  {key} = {value}")

    def register(self, target: BridgeTarget, bridge: Bridge) -> None:
        """
        ブリッジを登録する。
        """
        self.bridges[target] = bridge

    def register_position(self, position: SensorPosition, sensor_id: int) -> None:
        """
        サーボと位置の対応を登録する。
        """
        self.positions[sensor_id] = position

    def get_position(self, sensor_id: int) -> SensorPosition | None:
        return self.positions.get(sensor_id)

    def start(self) -> None:
        """
        送信スレッドと受信スレッドを開始する。
        """
        send_thread = threading.Thread(target=self._run_send, daemon=True)
        send_thread.start()
        self.send_thread = send_thread

        recv_thread = threading.Thread(target=self._run_recv, daemon=True)
        recv_thread.start()
        self.recv_thread = recv_thread

    def _run_send(self) -> None:
        """
        送信スレッドの中身。
        送信キューにデータがあれば、ブリッジに送信する。
        """

        while True:
            target, data = self.send_queue.get()  # ブロッキング処理
            logging.info(f"SEND {target} {data}")
            bridge = self.bridges.get(target)
            if bridge is not None:
                message = json.dumps(data)
                bridge.send(message)

    def _run_recv(self) -> None:
        """
        受信スレッドの中身。
        ブリッジから受信したデータがあれば、コールバックを呼び出す。
        """

        while True:
            for target, bridge in self.bridges.items():
                if bridge.serial.in_waiting:
                    message = bridge.receive()  # ブロッキング処理
                    try:
                        data = json.loads(message)
                        logging.info(f"RECV {target} {data}")
                        self.callback(target, data)
                    except json.decoder.JSONDecodeError:
                        pass

    def send(self, target: BridgeTarget, data: Any) -> None:
        """
        `target` に向けて JSON データ `data` を送信する。
        (実際にはすぐに送信せず、送信キューに入れておく。)
        """
        self.send_queue.put((target, data))
