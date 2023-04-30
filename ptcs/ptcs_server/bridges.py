import json
import queue
import threading
from typing import Any, Callable, Optional
import serial.tools.list_ports
from ptcs_control.components import Train
from usb_bt_bridge.bridge import Bridge


BridgeTarget = Train
BridgeDict = dict[BridgeTarget, Bridge]
BridgeCallback = Callable[[BridgeTarget, Any], None]


class BridgeManager:
    bridges: BridgeDict
    send_queue: queue.Queue[tuple[BridgeTarget, Any]]
    callback: BridgeCallback
    thread: Optional[threading.Thread]

    def __init__(self, callback: BridgeCallback) -> None:
        self.print_ports()

        bridges: BridgeDict = {
            Train("t0"): Bridge("COM4"),
        }

        self.bridges = bridges
        self.print_bridges()

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

    def start(self) -> None:
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        self.thread = thread

    def _run(self) -> None:
        while True:
            # 受信
            for target, bridge in self.bridges.items():
                if bridge.serial.in_waiting:
                    message = bridge.receive()
                    try:
                        data = json.loads(message)
                        print(f"RECV {target} {data}")
                        self.callback(target, data)
                    except json.decoder.JSONDecodeError:
                        pass

            # 送信
            while not self.send_queue.empty():
                target, data = self.send_queue.get()
                print(f"SEND {target} {data}")
                bridge = self.bridges[target]
                message = json.dumps(data)
                bridge.send(message)

    def send(self, target: BridgeTarget, data: Any) -> None:
        self.send_queue.put((target, data))
