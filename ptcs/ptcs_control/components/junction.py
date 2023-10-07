from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .section import Section


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

        MERGIN: float = 40.0  # ポイント通過後すぐに切り替えるとまずいので余裕距離をとる

        for train in self.control.trains.values():
            # 列車の最後尾からMERGIN離れた位置(tail)を取得
            tail_position = train.position.get_retracted_position(train.length + MERGIN)

            # 列車の先頭は指定されたjunctionに向かっていないが、
            # 列車の最後尾は指定されたjunctionに向かっている場合、
            # 列車はそのjunctinoを通過中なので、切り替えを禁止する
            if train.position.target_junction != self and tail_position.target_junction == self:
                return True

        return False  # 誰も通過していなければFalseを返す
