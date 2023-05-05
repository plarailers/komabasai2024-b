from pydantic import BaseModel, Field
from .components import Direction, Junction, Train


class RailwayCommand(BaseModel):
    """
    指令値
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる

    junctions: dict[Junction, "JunctionCommand"] = Field(default_factory=dict)
    trains: dict[Train, "TrainCommand"] = Field(default_factory=dict)

    def define_junctions(self, *junction_tuples: tuple["Junction", "Direction"]) -> None:
        """
        分岐・合流点への指令を一斉に初期化する。

        形式: `(ID, ポイントの向き)`
        """
        for junction_id, direction in junction_tuples:
            self.junctions[junction_id] = JunctionCommand(direction=direction)

    def define_trains(self, *train_tuples: tuple["Train", float]) -> None:
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

    j0a = Junction("j0a")
    j0b = Junction("j0b")
    j1a = Junction("j1a")
    j1b = Junction("j1b")

    t0 = Train("t0")
    t1 = Train("t1")

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
