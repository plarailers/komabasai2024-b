import json
import logging
import queue
import threading
from typing import Any, Callable, Optional
import serial.tools.list_ports
from ptcs_control.components import Position, Train
from usb_bt_bridge.bridge import Bridge


BridgeTarget = Train
BridgeDict = dict[BridgeTarget, Bridge]
PositionDict = dict[int, Position]
BridgeCallback = Callable[[BridgeTarget, Any], None]


class BridgeManager:
    bridges: BridgeDict
    positions: PositionDict
    send_queue: queue.Queue[tuple[BridgeTarget, Any]]
    callback: BridgeCallback
    thread: Optional[threading.Thread]

    def __init__(self, callback: BridgeCallback) -> None:
        self.bridges = {}
        self.positions = {}
        self.send_queue = queue.Queue()
        self.callback = callback
        self.thread = None

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

    def register_position(self, position_id: Position, sensor_id: int) -> None:
        """
        サーボと位置の対応を登録する。
        """
        self.positions[sensor_id] = position_id

    def get_position(self, sensor_id: int) -> Position:
        return self.positions[sensor_id]

    def start(self) -> None:
        """
        送受信スレッドを開始する。
        """
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        self.thread = thread

    def _run(self) -> None:
        """
        スレッドの中身。
        ブリッジから受信したデータがあれば、コールバックを呼び出す。
        送信キューにデータがあれば、ブリッジに送信する。
        """

        while True:
            # 受信
            for target, bridge in self.bridges.items():
                while bridge.serial.in_waiting:
                    message = bridge.receive()
                    try:
                        data = json.loads(message)
                        logging.info(f"RECV {target} {data}")
                        self.callback(target, data)
                    except json.decoder.JSONDecodeError:
                        pass

            # 送信
            while not self.send_queue.empty():
                target, data = self.send_queue.get()
                logging.info(f"SEND {target} {data}")
                bridge = self.bridges[target]
                message = json.dumps(data)
                bridge.send(message)

    def send(self, target: BridgeTarget, data: Any) -> None:
        """
        `target` に向けて JSON データ `data` を送信する。
        (実際にはすぐに送信せず、送信キューに入れておく。)
        """
        self.send_queue.put((target, data))
