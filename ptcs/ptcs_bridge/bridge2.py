import asyncio

from .master_controller_client import MasterControllerClient
from .point_client import PointClient
from .train_base import TrainBase
from .wire_pole_client import WirePoleClient


class Bridge2:
    trains: dict[str, TrainBase]
    obstacles: dict[str, WirePoleClient]
    controllers: dict[str, MasterControllerClient]
    points: dict[str, PointClient]

    def __init__(self) -> None:
        self.trains = {}
        self.obstacles = {}
        self.controllers = {}
        self.points = {}

    def add_train(self, train: TrainBase) -> None:
        assert train.id not in self.trains
        self.trains[train.id] = train

    def add_obstacle(self, obstacle: WirePoleClient) -> None:
        assert obstacle.id not in self.obstacles
        self.obstacles[obstacle.id] = obstacle

    def add_controller(self, controller: MasterControllerClient) -> None:
        assert controller.id not in self.controllers
        self.controllers[controller.id] = controller

    def add_point(self, point: PointClient) -> None:
        assert point.id not in self.controllers
        self.points[point.id] = point

    async def connect_all(self) -> None:
        await asyncio.gather(
            *(train.connect() for train in self.trains.values()),
            *(obstacle.connect() for obstacle in self.obstacles.values()),
            *(controller.connect() for controller in self.controllers.values()),
            *(point.connect() for point in self.points.values()),
        )

    async def disconnect_all(self) -> None:
        await asyncio.gather(
            *(train.disconnect() for train in self.trains.values()),
            *(obstacle.disconnect() for obstacle in self.obstacles.values()),
            *(controller.disconnect() for controller in self.controllers.values()),
            *(point.disconnect() for point in self.points.values()),
        )
