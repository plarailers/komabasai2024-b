from pydantic import BaseModel, Field

from .components import Direction, JunctionId, TrainId


class RailwayCommand(BaseModel):
    """
    指令値
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる

    junctions: dict[JunctionId, "JunctionCommand"] = Field(default_factory=dict)
    trains: dict[TrainId, "TrainCommand"] = Field(default_factory=dict)

    def define_junctions(self, *junction_tuples: tuple["JunctionId", "Direction"]) -> None:
        """
        分岐・合流点への指令を一斉に初期化する。

        形式: `(ID, ポイントの向き)`
        """
        for junction_id, direction in junction_tuples:
            self.junctions[junction_id] = JunctionCommand(direction=direction)

    def define_trains(self, *train_tuples: tuple["TrainId", float]) -> None:
        """
        列車への指令を一斉に初期化する。

        形式: `(ID, 速度指令値)`
        """
        for train_id, speed in train_tuples:
            self.trains[train_id] = TrainCommand(speed=speed)


class JunctionCommand(BaseModel):
    direction: "Direction"


class TrainCommand(BaseModel):
    speed: float


RailwayCommand.update_forward_refs()


def init_command() -> RailwayCommand:
    command = RailwayCommand()

    j0a = JunctionId("j0")
    j0b = JunctionId("j1")
    j1a = JunctionId("j2")
    j1b = JunctionId("j3")

    t0 = TrainId("t0")
    t1 = TrainId("t1")

    command.define_junctions(
        (j0a, Direction.STRAIGHT),
        (j0b, Direction.STRAIGHT),
        (j1a, Direction.STRAIGHT),
        (j1b, Direction.STRAIGHT),
    )

    command.define_trains(
        (t0, 0),
        (t1, 0),
    )

    return command
