from .components import Direction, Joint, Junction, Section


class State:
    junctions: dict[str, "Junction"]
    sections: dict[str, "Section"]

    def __init__(self) -> None:
        self.junctions = {}
        self.sections = {}

    def define_junctions(self, *junction_tuples: tuple[str, "Direction"]):
        """
        分岐・合流点を一斉に定義する。

        形式: `(ID, ポイントの最初の向き)`
        """
        for id, initial_direction in junction_tuples:
            junction = Junction(id=id, initial_direction=initial_direction)
            self.junctions[id] = junction

    def define_sections(self, *section_tuples: tuple[str, str, "Joint", str, "Joint", float]):
        """
        区間を一斉に定義する。

        形式: `(ID, j0のID, j0との接続方法, j1のID, j1との接続方法, 長さ[mm])`
        """
        for id, junction_0_id, junction_0_joint, junction_1_id, junction_1_joint, length in section_tuples:
            section = Section(
                id=id,
                junction_0=self.junctions[junction_0_id],
                junction_0_joint=junction_0_joint,
                junction_1=self.junctions[junction_1_id],
                junction_1_joint=junction_1_joint,
                length=length,
            )
            self.sections[id] = section


def init_state() -> State:
    state = State()

    state.define_junctions(
        ("j0a", Direction.STRAIGHT),
        ("j0b", Direction.STRAIGHT),
        ("j1a", Direction.STRAIGHT),
        ("j1b", Direction.STRAIGHT),
        ("j2a", Direction.STRAIGHT),
        ("j2b", Direction.STRAIGHT),
        ("j3a", Direction.STRAIGHT),
        ("j3b", Direction.STRAIGHT),
    )

    state.define_sections(
        ("s0", "j0a", Joint.CONVERGING, "j0b", Joint.THROUGH, 100),
        ("s1", "j0b", Joint.CONVERGING, "j1b", Joint.CONVERGING, 100),
        ("s2", "j1b", Joint.THROUGH, "j2b", Joint.THROUGH, 100),
        ("s3", "j2b", Joint.CONVERGING, "j3b", Joint.CONVERGING, 100),
        ("s4", "j3b", Joint.THROUGH, "j3a", Joint.CONVERGING, 100),
        ("s5", "j3a", Joint.THROUGH, "j2a", Joint.THROUGH, 100),
        ("s6", "j2a", Joint.CONVERGING, "j1a", Joint.CONVERGING, 100),
        ("s7", "j1a", Joint.THROUGH, "j0a", Joint.THROUGH, 100),
        ("s8", "j0a", Joint.DIVERGING, "j0b", Joint.DIVERGING, 100),
        ("s9", "j1a", Joint.DIVERGING, "j1b", Joint.DIVERGING, 100),
        ("s10", "j2a", Joint.DIVERGING, "j2b", Joint.DIVERGING, 100),
        ("s11", "j3a", Joint.DIVERGING, "j3b", Joint.DIVERGING, 100),
    )

    return state
