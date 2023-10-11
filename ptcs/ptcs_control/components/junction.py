from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .section import Section
    from .train import Train


class PointDirection(Enum):
    r"""
    サーボモーターの方向を表す列挙型

    ```
    _______________
    ______  _______ straight
          \ \______
           \_______ curve
    ```
    """

    STRAIGHT = "straight"
    CURVE = "curve"


class JunctionConnection(str, Enum):
    r"""
    ターンアウトレールにおける分岐・合流の接続のしかたを表す列挙型

    ```
               _______________
    converging ______  _______ through
                     \ \______
                      \_______ diverging
    ```

    NOTE: いい名前を募集中
    """

    THROUGH = "through"
    DIVERGING = "diverging"
    CONVERGING = "converging"


@dataclass
class Junction(BaseComponent):
    """分岐・合流点"""

    id: str

    # config
    connected_sections: dict[JunctionConnection, Section] = field(default_factory=dict)

    # manual
    manual_direction: PointDirection | None = field(default=None)

    # state
    current_direction: PointDirection = field(default=PointDirection.STRAIGHT)

    # commands
    direction_command: PointDirection = field(default=PointDirection.STRAIGHT)

    def __hash__(self) -> int:
        return self.id.__hash__()

    def verify(self) -> None:
        super().verify()
        assert self.connected_sections.get(JunctionConnection.THROUGH) is not None
        assert self.connected_sections.get(JunctionConnection.DIVERGING) is not None
        assert self.connected_sections.get(JunctionConnection.CONVERGING) is not None

    def set_direction(self, direction: PointDirection) -> None:
        """
        ポイントの方向を更新する。
        """

        self.current_direction = direction

    def is_toggle_prohibited(self) -> bool:
        """
        ジャンクションを列車が通過中であり、切り替えてはいけない場合に `True` を返す。
        """

        MERGIN: float = 10.0  # ポイント通過後すぐに切り替えるとまずいので余裕距離をとる

        for train in self.control.trains.values():
            # 列車の最後尾からMERGIN離れた位置(tail)を取得
            tail_position = train.head_position.get_retracted_position(train.length + MERGIN)

            # 列車の先頭は指定されたjunctionに向かっていないが、
            # 列車の最後尾は指定されたjunctionに向かっている場合、
            # 列車はそのjunctinoを通過中なので、切り替えを禁止する
            if train.head_position.target_junction != self and tail_position.target_junction == self:
                return True

        return False  # 誰も通過していなければFalseを返す

    def find_nearest_train(self) -> Train | None:
        """
        ジャンクションに迫っている列車が1つ以上あれば、最も距離の近いものを返す。
        """

        from .section import SectionConnection

        nearest_train: Train | None = None
        nearest_distance = math.inf

        for train in self.control.trains.values():
            if train.head_position.target_junction == self:
                if (
                    train.head_position.target_junction
                    == train.head_position.section.connected_junctions[SectionConnection.A]
                ):
                    distance = train.head_position.mileage
                elif (
                    train.head_position.target_junction
                    == train.head_position.section.connected_junctions[SectionConnection.B]
                ):
                    distance = train.head_position.section.length - train.head_position.mileage
                else:
                    raise

                if distance < nearest_distance:
                    nearest_train = train
                    nearest_distance = distance

        return nearest_train
