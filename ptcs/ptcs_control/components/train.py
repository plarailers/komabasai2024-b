from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import BaseComponent

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

        self.current_section, self.mileage, self.target_junction = self.control._get_new_position(
            self.current_section, self.mileage, self.target_junction, delta
        )

    def fix_position(self, sensor: SensorPosition) -> None:
        """
        列車の位置を修正する。
        TODO: 向きを割り出すためにどうするか
        """

        self.current_section = sensor.section
        self.target_junction = sensor.target_junction
        self.mileage = sensor.mileage
