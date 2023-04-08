from pydantic import BaseModel, Field
from .components import Direction, Junction, Section, Train


class RailwayState(BaseModel):
    """
    路線の状態
    """

    junctions: dict["Junction", "JunctionState"] = Field(default_factory=dict)
    sections: dict["Section", "SectionState"] = Field(default_factory=dict)
    trains: dict["Train", "TrainState"] = Field(default_factory=dict)

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

    def define_trains(self, *train_tuples: tuple["Train", "Section", float]) -> None:
        for (train_id, current_section, mileage) in train_tuples:
            self.trains[train_id] = TrainState(current_section=current_section, mileage=mileage)


class JunctionState(BaseModel):
    direction: "Direction"


class SectionState(BaseModel):
    pass


class TrainState(BaseModel):
    current_section: "Section"
    mileage: float


def init_state() -> RailwayState:
    state = RailwayState()

    j0a = Junction("j0a")
    j0b = Junction("j0b")
    j1a = Junction("j1a")
    j1b = Junction("j1b")
    j2a = Junction("j2a")
    j2b = Junction("j2b")
    j3a = Junction("j3a")
    j3b = Junction("j3b")

    s00 = Section("s00")
    s01 = Section("s01")
    s02 = Section("s02")
    s03 = Section("s03")
    s04 = Section("s04")
    s05 = Section("s05")
    s06 = Section("s06")
    s07 = Section("s07")
    s08 = Section("s08")
    s09 = Section("s09")
    s10 = Section("s10")
    s11 = Section("s11")

    t0 = Train("t0")
    t1 = Train("t1")

    state.define_junctions(
        (j0a, Direction.STRAIGHT),
        (j0b, Direction.STRAIGHT),
        (j1a, Direction.STRAIGHT),
        (j1b, Direction.STRAIGHT),
        (j2a, Direction.STRAIGHT),
        (j2b, Direction.STRAIGHT),
        (j3a, Direction.STRAIGHT),
        (j3b, Direction.STRAIGHT),
    )

    state.define_sections(
        (s00,),
        (s01,),
        (s02,),
        (s03,),
        (s04,),
        (s05,),
        (s06,),
        (s07,),
        (s08,),
        (s09,),
        (s10,),
        (s11,),
    )

    state.define_trains(
        (t0, s00, 0),
        (t1, s04, 0),
    )

    return state
