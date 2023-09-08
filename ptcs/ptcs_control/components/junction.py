from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..components import Direction, Joint
from .base import BaseComponent

if TYPE_CHECKING:
    from .section import Section


@dataclass
class Junction(BaseComponent):
    """分岐・合流点"""

    id: str

    # config
    connected_sections: dict[Joint, Section] = field(default_factory=dict)

    # state
    current_direction: Direction = field(default=Direction.STRAIGHT)

    # commands
    direction_command: Direction = field(default=Direction.STRAIGHT)

    def __hash__(self) -> int:
        return self.id.__hash__()

    def verify(self) -> None:
        super().verify()
        assert self.connected_sections.get(Joint.THROUGH) is not None
        assert self.connected_sections.get(Joint.DIVERGING) is not None
        assert self.connected_sections.get(Joint.CONVERGING) is not None

    def set_direction(self, direction: Direction) -> None:
        """
        ポイントの方向を更新する。
        """

        self.current_direction = direction

    def is_toggle_prohibited(self) -> bool:
        """
        ジャンクションを列車が通過中であり、切り替えてはいけない場合に `True` を返す。
        """

        MERGIN: float = 40  # ポイント通過後すぐに切り替えるとまずいので余裕距離をとる
        TRAIN_LENGTH: float = 60  # 列車の長さ[cm] NOTE: 将来的には車両等のパラメータとして外に出す

        for train in self.control.trains.values():
            # 列車の最後尾からMERGIN離れた位置(tail)を取得
            tail_position = train.position.get_retracted_position(TRAIN_LENGTH + MERGIN)

            # 列車の先頭は指定されたjunctionに向かっていないが、
            # 列車の最後尾は指定されたjunctionに向かっている場合、
            # 列車はそのjunctinoを通過中なので、切り替えを禁止する
            if train.position.target_junction != self and tail_position.target_junction == self:
                return True

        return False  # 誰も通過していなければFalseを返す
