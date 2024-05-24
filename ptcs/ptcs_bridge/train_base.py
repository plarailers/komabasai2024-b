from typing import Callable

NotifyPositionIdCallback = Callable[["TrainBase", str], None]
NotifyRotationCallback = Callable[["TrainBase", int], None]
NotifyVoltageCallback = Callable[["TrainBase", int], None]


class TrainBase:
    id: str

    async def connect(self) -> None:
        raise NotImplementedError()

    async def disconnect(self) -> None:
        raise NotImplementedError()

    async def send_speed(self, speed: float) -> None:
        raise NotImplementedError()

    async def send_motor_input(self, motor_input: int) -> None:
        raise NotImplementedError()

    async def start_notify_position_uid(self, callback: NotifyPositionIdCallback) -> None:
        raise NotImplementedError()

    async def start_notify_rotation(self, callback: NotifyRotationCallback) -> None:
        raise NotImplementedError()

    async def start_notify_voltage(self, callback: NotifyVoltageCallback) -> None:
        raise NotImplementedError()
