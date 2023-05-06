import json
import serial
import time


class Bridge:
    serial: "serial.Serial"

    def __init__(self, port: str) -> None:
        baudrate = 115200
        self.serial = serial.Serial(port, baudrate, timeout=3.0, write_timeout=3.0)

    def send(self, message: str) -> None:
        self.serial.write(bytes(message, "ascii"))

    def receive(self) -> str:
        message = self.serial.readline()
        message_string = message.decode("utf-8")
        return message_string

    def close(self) -> None:
        self.serial.close()


def main() -> None:
    i = 0
    # port = '/dev/cu.usbserial-5' # ポート名は環境に合わせて変更する
    port = "COM4"  # ポート名は環境に合わせて変更する
    bridge = Bridge(port=port)
    time.sleep(3)
    while True:
        time.sleep(0.3)
        i += 1
        json_data = json.dumps({"key": 51, "value": i})
        print(json_data)
        bridge.send(json_data)
        print(bridge.receive())


if __name__ == "__main__":
    main()
