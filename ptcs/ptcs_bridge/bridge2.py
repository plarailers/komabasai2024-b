import asyncio

from .train_base import TrainBase
from .wire_pole_client import WirePoleClient


class Bridge2:
    trains: dict[str, TrainBase]
    obstacles: dict[str, WirePoleClient]

    def __init__(self) -> None:
        self.trains = {}
        self.obstacles = {}

    def add_train(self, train: TrainBase) -> None:
        assert train.id not in self.trains
        self.trains[train.id] = train

    def add_obstacle(self, obstacle: WirePoleClient) -> None:
        assert obstacle.id not in self.obstacles
        self.obstacles[obstacle.id] = obstacle

    async def connect_all(self) -> None:
        await asyncio.gather(
            *(train.connect() for train in self.trains.values()),
            *(obstacle.connect() for obstacle in self.obstacles.values()),
        )

    async def disconnect_all(self) -> None:
        await asyncio.gather(
            *(train.disconnect() for train in self.trains.values()),
            *(obstacle.disconnect() for obstacle in self.obstacles.values()),
        )
