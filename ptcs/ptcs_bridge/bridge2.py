import asyncio

from .train_base import TrainBase


class Bridge2:
    trains: dict[str, TrainBase]

    def __init__(self) -> None:
        self.trains = {}

    def add_train(self, train: TrainBase) -> None:
        assert train.id not in self.trains
        self.trains[train.id] = train

    async def connect_all(self) -> None:
        await asyncio.gather(*(train.connect() for train in self.trains.values()))

    async def disconnect_all(self) -> None:
        await asyncio.gather(*(train.disconnect() for train in self.trains.values()))
