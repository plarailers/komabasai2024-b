from typing import Optional
from pydantic import BaseModel, Field
from .components import Direction, Junction, Section, Stop, Train
from .constants import (
    STRAIGHT_RAIL,
    STRAIGHT_1_4_RAIL,
    STRAIGHT_1_6_RAIL,
    CURVE_RAIL,
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

    junctions: dict[Junction, "JunctionState"] = Field(default_factory=dict)
    sections: dict[Section, "SectionState"] = Field(default_factory=dict)
    trains: dict[Train, "TrainState"] = Field(default_factory=dict)

    def define_junctions(
        self, *junction_tuples: tuple["Junction", "Direction"]
    ) -> None:
        """
        分岐・合流点を一斉に初期化する。

        形式: `(ID, ポイントの最初の向き)`
        """
        for junction_id, initial_direction in junction_tuples:
            self.junctions[junction_id] = JunctionState(direction=initial_direction)

    def define_sections(self, *section_tuples: tuple["Section"]) -> None:
        """
        区間を一斉に初期化する。

        形式: `(ID,)`
        """
        for (section_id,) in section_tuples:
            self.sections[section_id] = SectionState()

    def define_trains(
        self, *train_tuples: tuple["Train", "Section", "Junction", float]
    ) -> None:
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
    current_section: "Section"
    target_junction: "Junction"
    mileage: float
    stop: Optional["Stop"] = Field(default=None, description="列車の停止目標")
    stop_distance: Optional[float] = Field(default=0, description="停止目標までの距離[cm]")
    departure_time: Optional[int] = Field(default=None, description="発車予定時刻")


RailwayState.update_forward_refs()


def init_state() -> RailwayState:
    state = RailwayState()

    j0a = Junction("j0a")
    j0b = Junction("j0b")
    j1a = Junction("j1a")
    j1b = Junction("j1b")

    s0 = Section("s0")
    s1 = Section("s1")
    s2 = Section("s2")
    s3 = Section("s3")
    s4 = Section("s4")
    s5 = Section("s5")

    t0 = Train("t0")
    t1 = Train("t1")

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
