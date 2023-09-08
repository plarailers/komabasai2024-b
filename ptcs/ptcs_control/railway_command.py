from __future__ import annotations

from pydantic import BaseModel, Field

from .components import TrainId


class RailwayCommand(BaseModel):
    """
    指令値
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる

    trains: dict[TrainId, "TrainCommand"] = Field(default_factory=dict)

    def define_trains(self, *train_tuples: tuple["TrainId", float]) -> None:
        """
        列車への指令を一斉に初期化する。

        形式: `(ID, 速度指令値)`
        """
        for train_id, speed in train_tuples:
            self.trains[train_id] = TrainCommand(speed=speed)


class TrainCommand(BaseModel):
    speed: float


RailwayCommand.update_forward_refs()


def init_command() -> RailwayCommand:
    command = RailwayCommand()

    t0 = TrainId("t0")
    t1 = TrainId("t1")

    command.define_trains(
        (t0, 0),
        (t1, 0),
    )

    return command
