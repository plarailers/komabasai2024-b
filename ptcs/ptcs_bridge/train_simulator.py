import asyncio
import logging
import math

from .train_base import NotifyPositionIdCallback, NotifyRotationCallback, TrainBase

logger = logging.getLogger(__name__)

_background_tasks: set[asyncio.Task] = set()


class TrainSimulator(TrainBase):
    """
    BLE 通信を行わず、列車への速度指令とモーター回転通知をシミュレーションする。
    """

    id: str
    _current_speed_cm_s: float
    _target_speed_cm_s: float
    _total_rotation: float
    _task: asyncio.Task | None
    _notify_rotation_callback: NotifyRotationCallback | None

    INTERVAL_SECONDS = 0.1
    INPUT_TO_CENTIMETERS_PER_SECOND = 30.0 / 255
    WHEEL_PERIMETER_CENTIMETERS = 2.4 * math.pi
    GEAR_RATIO = 175 / 8448

    def __init__(self, id: str) -> None:
        self.id = id
        self._current_speed_cm_s = 0.0
        self._target_speed_cm_s = 0.0
        self._total_rotation = 0.0
        self._task = None
        self._notify_rotation_callback = None

    def __str__(self) -> str:
        return f"TrainSimulator({self.id})"

    async def _loop(self):
        while True:
            await asyncio.sleep(self.INTERVAL_SECONDS)

            # とりあえず簡単に、即座に指令速度に変わるものとする
            prev_speed_cm_s = self._current_speed_cm_s
            self._current_speed_cm_s = self._target_speed_cm_s

            delta_cm = (prev_speed_cm_s + self._current_speed_cm_s) / 2 * self.INTERVAL_SECONDS

            prev_total_rotation = self._total_rotation
            self._total_rotation += delta_cm / self.WHEEL_PERIMETER_CENTIMETERS / self.GEAR_RATIO

            rotation = math.floor(self._total_rotation) - math.floor(prev_total_rotation)

            if self._notify_rotation_callback is not None:
                for _ in range(rotation):
                    # logger.info("%s notify rotation %s", self, 1)
                    self._notify_rotation_callback(self, 1)

    async def connect(self) -> None:
        assert self._task is None
        task = asyncio.create_task(self._loop())
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
        self._task = task
        logger.info("%s connected", self)

    async def disconnect(self) -> None:
        assert self._task is not None
        self._task.cancel()
        self._task = None
        logger.info("%s disconnected", self)

    async def send_speed(self, speed: float) -> None:
        self._target_speed_cm_s = speed * self.INPUT_TO_CENTIMETERS_PER_SECOND
        logger.info("%s send speed %s", self, speed)

    async def start_notify_position_id(self, callback: NotifyPositionIdCallback) -> None:
        raise NotImplementedError()

    async def start_notify_rotation(self, callback: NotifyRotationCallback) -> None:
        self._notify_rotation_callback = callback


async def main():
    t0 = TrainSimulator("t0")
    t1 = TrainSimulator("t1")
    await t0.connect()
    await t1.connect()

    def handle_rotation(train: TrainSimulator, _rotation: int):
        print(f"{train} rotated!")

    await t0.start_notify_rotation(handle_rotation)
    await t1.start_notify_rotation(handle_rotation)

    await asyncio.sleep(1.0)
    await t0.send_speed(40)
    await asyncio.sleep(1.0)
    await t0.send_speed(80)
    await asyncio.sleep(1.0)
    await t0.send_speed(120)
    await asyncio.sleep(1.0)
    await t0.send_speed(160)
    await asyncio.sleep(1.0)
    await t0.send_speed(200)
    await asyncio.sleep(10.0)
    await t0.send_speed(0)
    await asyncio.sleep(5.0)

    await t0.disconnect()
    await t1.disconnect()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)-8s]  %(message)s"))
    logger.addHandler(handler)

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
