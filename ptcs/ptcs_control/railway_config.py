from __future__ import annotations

import math

from pydantic import BaseModel, Field

from .components import PositionId, StationId, StopId, TrainId
from .constants import (
    CURVE_RAIL,
    STRAIGHT_1_4_RAIL,
    STRAIGHT_RAIL,
    WATARI_RAIL_A,
    WATARI_RAIL_B,
)


class RailwayConfig(BaseModel):
    """
    路線の設定
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる

    trains: dict[TrainId, "TrainConfig"] = Field(default_factory=dict)
    stations: dict[StationId, "StationConfig"] = Field(default_factory=dict)
    stops: dict[StopId, "StopConfig"] = Field(default_factory=dict)
    positions: dict[PositionId, "PositionConfig"] = Field(default_factory=dict)

    def define_trains(self, *train_tuples: tuple["TrainId", int, int, float, float]) -> None:
        for (
            train_id,
            min_input,
            max_input,
            max_speed,
            delta_per_motor_rotation,
        ) in train_tuples:
            self.trains[train_id] = TrainConfig(
                min_input=min_input,
                max_input=max_input,
                max_speed=max_speed,
                delta_per_motor_rotation=delta_per_motor_rotation,
            )


class TrainConfig(BaseModel):
    min_input: int
    max_input: int
    max_speed: float
    delta_per_motor_rotation: float  # モータ1回転で進む距離[cm]

    def calc_input(self, speed: float) -> int:
        if speed > self.max_speed:
            return self.max_input
        elif speed <= 0:
            return 0
        else:
            return math.floor(self.min_input + (self.max_input - self.min_input) * speed / self.max_speed)


class StationConfig(BaseModel):
    stops: list["StopId"] = Field(default_factory=list)


class StopConfig(BaseModel):
    section_id: str
    target_junction_id: str
    mileage: float


class PositionConfig(BaseModel):
    section_id: str
    mileage: float

    target_junction_id: str
    """
    NOTE: 将来的にはここに向きの情報を持たせなくて良いようにする。
    具体的には、通った向きがわかるようなセンシング技術を用いるか、
    計算で向きを予測するか（限界はある）のどちらか。
    """


RailwayConfig.update_forward_refs()


def init_config() -> RailwayConfig:
    config = RailwayConfig()

    j0a = "j0"
    j0b = "j1"
    j1a = "j2"
    j1b = "j3"

    s0 = "s0"
    s1 = "s1"
    s2 = "s2"
    s3 = "s3"

    t0 = TrainId("t0")
    t1 = TrainId("t1")

    station_0 = StationId("station_0")
    station_1 = StationId("station_1")

    stop_0 = StopId("stop_0")
    stop_1 = StopId("stop_1")
    stop_2 = StopId("stop_2")
    stop_3 = StopId("stop_3")
    stop_4 = StopId("stop_4")

    position_80 = PositionId("position_80")
    position_138 = PositionId("position_138")
    position_173 = PositionId("position_173")
    position_255 = PositionId("position_255")

    config.define_trains(
        (t0, 70, 130, 40.0, 0.2435 * 0.9),  # Dr
        (t1, 90, 130, 40.0, 0.1919 * 1.1 * 0.9),  # E6
        # E5はAPS故障につきまだ運用しない
    )

    config.stations.update(
        {
            station_0: StationConfig(stops=[stop_0, stop_1]),
            station_1: StationConfig(stops=[stop_2, stop_3, stop_4]),
        }
    )

    config.stops.update(
        {
            stop_0: StopConfig(section_id=s0, target_junction_id=j0b, mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 4.5),
            stop_1: StopConfig(
                section_id=s0,
                target_junction_id=j0b,
                mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 10.0 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
            ),
            stop_2: StopConfig(section_id=s1, target_junction_id=j0b, mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 1.5),
            stop_3: StopConfig(section_id=s1, target_junction_id=j1b, mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 1.5),
            stop_4: StopConfig(section_id=s3, target_junction_id=j0a, mileage=WATARI_RAIL_A * 1 + STRAIGHT_RAIL * 1.5),
        }
    )

    config.positions.update(
        {
            position_173: PositionConfig(
                section_id=s0, target_junction_id=j0b, mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 2.5
            ),
            position_138: PositionConfig(
                section_id=s0,
                target_junction_id=j0b,
                mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 9.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
            ),
            position_80: PositionConfig(
                section_id=s0,
                target_junction_id=j0b,
                mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 13.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
            ),
            position_255: PositionConfig(
                section_id=s2,
                target_junction_id=j1a,
                mileage=WATARI_RAIL_A * 1 + STRAIGHT_RAIL * 5.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
            ),
        }
    )

    return config
