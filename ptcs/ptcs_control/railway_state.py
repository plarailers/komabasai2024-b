from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .components import StopId, TrainId
from .constants import STRAIGHT_RAIL, WATARI_RAIL_B


class RailwayState(BaseModel):
    """
    路線の状態
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる

    time: int = Field(default=0, description="内部時刻")

    trains: dict[TrainId, "TrainState"] = Field(default_factory=dict)

    def define_trains(self, *train_tuples: tuple["TrainId", str, str, float]) -> None:
        for train_id, current_section_id, target_junction_id, mileage in train_tuples:
            self.trains[train_id] = TrainState(
                current_section_id=current_section_id,
                target_junction_id=target_junction_id,
                mileage=mileage,
            )


class TrainState(BaseModel):
    current_section_id: str
    target_junction_id: str
    mileage: float
    stop: Optional["StopId"] = Field(default=None, description="列車の停止目標")
    stop_distance: Optional[float] = Field(default=0, description="停止目標までの距離[cm]")
    departure_time: Optional[int] = Field(default=None, description="発車予定時刻")


RailwayState.update_forward_refs()


def init_state() -> RailwayState:
    state = RailwayState()

    j0b = "j1"
    j1b = "j3"

    s0 = "s0"
    s1 = "s1"

    t0 = TrainId("t0")
    t1 = TrainId("t1")

    state.define_trains(
        (t0, s0, j0b, STRAIGHT_RAIL * 4.5 + WATARI_RAIL_B + 1),  # 次駅探索の都合上、stopを1cm通り過ぎた場所にしておく
        (t1, s1, j1b, STRAIGHT_RAIL * 2.5 + WATARI_RAIL_B + 1),
    )

    return state
