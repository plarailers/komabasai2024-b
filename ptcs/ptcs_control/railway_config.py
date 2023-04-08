from pydantic import BaseModel, Field
from .components import Joint, Junction, Section, Train


class RailwayConfig(BaseModel):
    """
    路線の設定
    """

    junctions: dict["Junction", "JunctionConfig"] = Field(default_factory=dict)
    sections: dict["Section", "SectionConfig"] = Field(default_factory=dict)
    trains: dict["Train", "TrainConfig"] = Field(default_factory=dict)

    def define_junctions(self, *junction_tuples: tuple["Junction"]) -> None:
        """
        分岐・合流点を一斉に定義する。

        形式: `(ID,)`
        """
        for (junction_id,) in junction_tuples:
            self.junctions[junction_id] = JunctionConfig()

    def define_sections(
        self, *section_tuples: tuple["Section", "Junction", "Joint", "Junction", "Joint", float]
    ) -> None:
        """
        区間を一斉に定義する。

        形式: `(ID, j0のID, j0との接続方法, j1のID, j1との接続方法, 長さ[mm])`
        """
        for section_id, junction_0_id, junction_0_joint, junction_1_id, junction_1_joint, length in section_tuples:
            self.junctions[junction_0_id].add_section(junction_0_joint, section_id)
            self.junctions[junction_1_id].add_section(junction_1_joint, section_id)
            self.sections[section_id] = SectionConfig(
                junction_0=junction_0_id,
                junction_1=junction_1_id,
                length=length,
            )

    def define_trains(self, *train_tuples: tuple["Train"]) -> None:
        for (train_id,) in train_tuples:
            self.trains[train_id] = TrainConfig()


class JunctionConfig(BaseModel):
    sections: dict["Joint", "Section"] = Field(default_factory=dict)

    def add_section(self, joint: "Joint", section: "Section") -> None:
        self.sections[joint] = section


class SectionConfig(BaseModel):
    junction_0: "Junction"
    junction_1: "Junction"
    length: float

    def get_opposite_junction(self, junction: "Junction") -> "Junction":
        if junction == self.junction_0:
            return self.junction_1
        elif junction == self.junction_1:
            return self.junction_0
        else:
            raise


class TrainConfig(BaseModel):
    pass


def init_config() -> RailwayConfig:
    config = RailwayConfig()

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

    config.define_junctions(
        (j0a,),
        (j0b,),
        (j1a,),
        (j1b,),
        (j2a,),
        (j2b,),
        (j3a,),
        (j3b,),
    )

    config.define_sections(
        (s00, j0a, Joint.CONVERGING, j0b, Joint.THROUGH, 100),
        (s01, j0b, Joint.CONVERGING, j1b, Joint.CONVERGING, 100),
        (s02, j1b, Joint.THROUGH, j2b, Joint.THROUGH, 100),
        (s03, j2b, Joint.CONVERGING, j3b, Joint.CONVERGING, 100),
        (s04, j3b, Joint.THROUGH, j3a, Joint.CONVERGING, 100),
        (s05, j3a, Joint.THROUGH, j2a, Joint.THROUGH, 100),
        (s06, j2a, Joint.CONVERGING, j1a, Joint.CONVERGING, 100),
        (s07, j1a, Joint.THROUGH, j0a, Joint.THROUGH, 100),
        (s08, j0a, Joint.DIVERGING, j0b, Joint.DIVERGING, 100),
        (s09, j1a, Joint.DIVERGING, j1b, Joint.DIVERGING, 100),
        (s10, j2a, Joint.DIVERGING, j2b, Joint.DIVERGING, 100),
        (s11, j3a, Joint.DIVERGING, j3b, Joint.DIVERGING, 100),
    )

    config.define_trains(
        (t0,),
        (t1,),
    )

    return config
