import logging
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field

from ..components.junction import Junction, JunctionConnection
from ..components.obstacle import Obstacle
from ..components.section import Section, SectionConnection
from ..components.sensor_position import SensorPosition
from ..components.station import Station
from ..components.stop import Stop
from ..components.train import Train
from .events import Event


def create_empty_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    return logger


@dataclass
class BaseControl(ABC):
    """
    列車制御システムの全体を管理する。

    状態変化に応じて再計算を行う `update()` メソッドはこのクラスに実装されていないので、
    固定閉塞か移動閉塞かといったシステムの特性に応じて派生クラスを作って実装すること。
    """

    _current_time: int = field(default=0)  # 現在時刻

    junctions: dict[str, Junction] = field(default_factory=dict)
    sections: dict[str, Section] = field(default_factory=dict)
    trains: dict[str, Train] = field(default_factory=dict)
    stops: dict[str, Stop] = field(default_factory=dict)
    stations: dict[str, Station] = field(default_factory=dict)
    sensor_positions: dict[str, SensorPosition] = field(default_factory=dict)
    obstacles: dict[str, Obstacle] = field(default_factory=dict)

    event_queue: deque[Event] = field(default_factory=lambda: deque())

    logger: logging.Logger = field(default_factory=create_empty_logger)

    def add_junction(self, junction: Junction) -> None:
        assert junction.id not in self.junctions
        self.junctions[junction.id] = junction
        junction._control = self

    def add_section(self, section: Section) -> None:
        assert section.id not in self.sections
        self.sections[section.id] = section
        section._control = self

    def connect(
        self,
        section: Section,
        section_connection: SectionConnection,
        junction: Junction,
        junction_connection: JunctionConnection,
    ) -> None:
        assert section_connection not in section.connected_junctions
        section.connected_junctions[section_connection] = junction

        assert junction_connection not in junction.connected_sections
        junction.connected_sections[junction_connection] = section

    def add_train(self, train: Train) -> None:
        assert train.id not in self.trains
        self.trains[train.id] = train
        train._control = self

    def add_stop(self, stop: Stop) -> None:
        assert stop.id not in self.stops
        self.stops[stop.id] = stop
        stop._control = self

    def add_station(self, station: Station) -> None:
        assert station.id not in self.stations
        self.stations[station.id] = station
        station._control = self

    def add_sensor_position(self, position: SensorPosition) -> None:
        assert position.id not in self.sensor_positions
        self.sensor_positions[position.id] = position
        position._control = self

    def add_obstacle(self, obstacle: Obstacle) -> None:
        assert obstacle.id not in self.obstacles
        self.obstacles[obstacle.id] = obstacle
        obstacle._control = self

    def verify(self) -> None:
        for junction in self.junctions.values():
            junction.verify()
        for section in self.sections.values():
            section.verify()
        for train in self.trains.values():
            train.verify()
        for stop in self.stops.values():
            stop.verify()
        for position in self.sensor_positions.values():
            position.verify()
        for obstacle in self.obstacles.values():
            obstacle.verify()

    @property
    def current_time(self) -> int:
        return self._current_time

    @current_time.setter
    def current_time(self, value) -> None:
        # self.logger.info(f"current_time = {value}")
        self._current_time = value

    def tick(self, increment: int = 1) -> None:
        """
        内部時刻を進める。
        """
        self.current_time += increment

    @abstractmethod
    def update(self) -> None:
        """
        状態に変化が起こった後、すべてを再計算する。
        継承先のクラスで実装すること。
        """
        self.event_queue.clear()
