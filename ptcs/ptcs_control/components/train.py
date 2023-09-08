from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import BaseComponent
from .section import SectionConnection

if TYPE_CHECKING:
    from .junction import Junction
    from .section import Section
    from .sensor_position import SensorPosition
    from .stop import Stop


@dataclass
class Train(BaseComponent):
    """列車"""

    id: str

    # config
    min_input: int
    max_input: int
    max_speed: float
    delta_per_motor_rotation: float  # モータ1回転で進む距離[cm]

    # state
    current_section: Section
    target_junction: Junction
    mileage: float
    stop: Stop | None = field(default=None)  # 列車の停止目標
    stop_distance: float = field(default=0.0)  # 停止目標までの距離[cm]
    departure_time: int | None = field(default=None)  # 発車予定時刻

    # commands
    command_speed: float = field(default=0.0)  # 速度指令値

    def calc_input(self, speed: float) -> int:
        if speed > self.max_speed:
            return self.max_input
        elif speed <= 0:
            return 0
        else:
            return math.floor(self.min_input + (self.max_input - self.min_input) * speed / self.max_speed)

    def move_forward_mr(self, motor_rotation: int) -> None:
        """
        列車をモータ motor_rotation 回転分だけ進める。
        """

        self.move_forward(motor_rotation * self.delta_per_motor_rotation)

    def move_forward(self, delta: float) -> None:
        """
        列車を距離 delta 分だけ進める。
        """

        current_section = self.current_section

        if self.target_junction == current_section.connected_junctions[SectionConnection.B]:
            self.mileage += delta
        elif self.target_junction == current_section.connected_junctions[SectionConnection.A]:
            self.mileage -= delta
        else:
            raise

        while self.mileage > current_section.length or self.mileage < 0:
            if self.mileage > current_section.length:
                surplus_mileage = self.mileage - current_section.length
            elif self.mileage < 0:
                surplus_mileage = -self.mileage
            else:
                raise

            next_section, next_target_junction = self.control._get_next_section_and_junction(
                self.current_section, self.target_junction
            )

            self.current_section = next_section
            current_section = next_section
            self.target_junction = next_target_junction
            if self.target_junction == current_section.connected_junctions[SectionConnection.B]:
                self.mileage = surplus_mileage
            elif self.target_junction == current_section.connected_junctions[SectionConnection.A]:
                self.mileage = current_section.length - surplus_mileage
            else:
                raise

    def fix_position(self, sensor: SensorPosition) -> None:
        """
        列車の位置を修正する。
        TODO: 向きを割り出すためにどうするか
        """

        self.current_section = sensor.section
        self.target_junction = sensor.target_junction
        self.mileage = sensor.mileage
