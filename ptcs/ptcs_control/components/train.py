from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .junction import Junction
    from .section import Section
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
