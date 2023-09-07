from typing import Optional

from pydantic import BaseModel, Field

from .components import Direction, JunctionId, SectionId, StopId, TrainId
from .constants import (
    CURVE_RAIL,
    STRAIGHT_1_4_RAIL,
    STRAIGHT_1_6_RAIL,
    STRAIGHT_RAIL,
    U_TURN_RAIL,
    WATARI_RAIL_A,
    WATARI_RAIL_B,
    WATARI_RAIL_C,
)


class RailwayState(BaseModel):
    """
    路線の状態
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる

    time: int = Field(default=0, description="内部時刻")

    junctions: dict[JunctionId, "JunctionState"] = Field(default_factory=dict)
    sections: dict[SectionId, "SectionState"] = Field(default_factory=dict)
    trains: dict[TrainId, "TrainState"] = Field(default_factory=dict)

    def define_junctions(self, *junction_tuples: tuple["JunctionId", "Direction"]) -> None:
        """
        分岐・合流点を一斉に初期化する。

        形式: `(ID, ポイントの最初の向き)`
        """
        for junction_id, initial_direction in junction_tuples:
            self.junctions[junction_id] = JunctionState(direction=initial_direction)

    def define_sections(self, *section_tuples: tuple["SectionId"]) -> None:
        """
        区間を一斉に初期化する。

        形式: `(ID,)`
        """
        for (section_id,) in section_tuples:
            self.sections[section_id] = SectionState()

    def define_trains(self, *train_tuples: tuple["TrainId", "SectionId", "JunctionId", float]) -> None:
        for train_id, current_section, target_junction, mileage in train_tuples:
            self.trains[train_id] = TrainState(
                current_section=current_section,
                target_junction=target_junction,
                mileage=mileage,
            )


class JunctionState(BaseModel):
    direction: "Direction"


class SectionState(BaseModel):
    blocked: bool = Field(default=False, description="区間上に障害物が発生していて使えない状態になっているかどうか")


class TrainState(BaseModel):
    current_section: "SectionId"
    target_junction: "JunctionId"
    mileage: float
    stop: Optional["StopId"] = Field(default=None, description="列車の停止目標")
    stop_distance: Optional[float] = Field(default=0, description="停止目標までの距離[cm]")
    departure_time: Optional[int] = Field(default=None, description="発車予定時刻")


RailwayState.update_forward_refs()


def init_state() -> RailwayState:
    state = RailwayState()

    j0a = JunctionId("j0")
    j0b = JunctionId("j1")
    j1a = JunctionId("j2")
    j1b = JunctionId("j3")

    s0 = SectionId("s0")
    s1 = SectionId("s1")
    s2 = SectionId("s2")
    s3 = SectionId("s3")
    s4 = SectionId("s4")
    s5 = SectionId("s5")

    t0 = TrainId("t0")
    t1 = TrainId("t1")

    state.define_junctions(
        (j0a, Direction.STRAIGHT),
        (j0b, Direction.STRAIGHT),
        (j1a, Direction.STRAIGHT),
        (j1b, Direction.STRAIGHT),
    )

    state.define_sections(
        (s0,),
        (s1,),
        (s2,),
        (s3,),
        (s4,),
        (s5,),
    )

    state.define_trains(
        (t0, s0, j0b, STRAIGHT_RAIL * 4.5 + WATARI_RAIL_B + 1),  # 次駅探索の都合上、stopを1cm通り過ぎた場所にしておく
        (t1, s1, j1b, STRAIGHT_RAIL * 2.5 + WATARI_RAIL_B + 1),
    )

    return state
