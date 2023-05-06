from pydantic import BaseModel, Field
from .components import Direction, Junction, Section, Train


class RailwayState(BaseModel):
    """
    路線の状態
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる

    junctions: dict[Junction, "JunctionState"] = Field(default_factory=dict)
    sections: dict[Section, "SectionState"] = Field(default_factory=dict)
    trains: dict[Train, "TrainState"] = Field(default_factory=dict)

    def define_junctions(self, *junction_tuples: tuple["Junction", "Direction"]) -> None:
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

    def define_trains(self, *train_tuples: tuple["Train", "Section", "Junction", float]) -> None:
        for train_id, current_section, target_junction, mileage in train_tuples:
            self.trains[train_id] = TrainState(
                current_section=current_section, target_junction=target_junction, mileage=mileage
            )


class JunctionState(BaseModel):
    direction: "Direction"


class SectionState(BaseModel):
    blocked: bool = Field(False, description="区間上に障害物が発生していて使えない状態になっているかどうか")


class TrainState(BaseModel):
    current_section: "Section"
    target_junction: "Junction"
    mileage: float


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
        (t0, s0, j0b, 0),
        (t1, s2, j1a, 0),
    )

    return state
