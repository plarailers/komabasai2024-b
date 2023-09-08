from __future__ import annotations

from pydantic import BaseModel, Field

from .components import StationId, StopId
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

    stations: dict[StationId, "StationConfig"] = Field(default_factory=dict)
    stops: dict[StopId, "StopConfig"] = Field(default_factory=dict)


class StationConfig(BaseModel):
    stops: list["StopId"] = Field(default_factory=list)


class StopConfig(BaseModel):
    section_id: str
    target_junction_id: str
    mileage: float


RailwayConfig.update_forward_refs()


def init_config() -> RailwayConfig:
    config = RailwayConfig()

    j0a = "j0"
    j0b = "j1"
    j1b = "j3"

    s0 = "s0"
    s1 = "s1"
    s3 = "s3"

    station_0 = StationId("station_0")
    station_1 = StationId("station_1")

    stop_0 = StopId("stop_0")
    stop_1 = StopId("stop_1")
    stop_2 = StopId("stop_2")
    stop_3 = StopId("stop_3")
    stop_4 = StopId("stop_4")

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

    return config
