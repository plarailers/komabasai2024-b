from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .base import BaseComponent
from .junction import JunctionConnection, PointDirection

if TYPE_CHECKING:
    from .junction import Junction


class SectionConnection(str, Enum):
    """区間の端点"""

    A = "A"
    B = "B"


@dataclass
class Section(BaseComponent):
    """区間"""

    id: str

    # config
    length: float
    connected_junctions: dict[SectionConnection, Junction] = field(default_factory=dict)
    block_id: str | None = field(default=None)

    # state
    _is_blocked: bool = field(default=False)  # 区間上に障害物が発生していて使えない状態になっているかどうか

    def __hash__(self) -> int:
        return self.id.__hash__()

    def verify(self) -> None:
        super().verify()
        assert self.connected_junctions.get(SectionConnection.A) is not None
        assert self.connected_junctions.get(SectionConnection.B) is not None

    @property
    def is_blocked(self) -> bool:
        return self._is_blocked

    @is_blocked.setter
    def is_blocked(self, value: bool):
        # self.control.logger.info(f"{self.id}.is_blocked = {value}")
        self._is_blocked = value

    def block(self) -> None:
        """
        区間上に障害物を発生させ、使えなくさせる。
        """
        self.is_blocked = True

    def unblock(self) -> None:
        """
        区間上の障害物を取り除き、使えるようにする。
        """
        self.is_blocked = False

    def get_opposite_junction(self, junction: Junction) -> Junction:
        if junction == self.connected_junctions[SectionConnection.A]:
            return self.connected_junctions[SectionConnection.B]
        elif junction == self.connected_junctions[SectionConnection.B]:
            return self.connected_junctions[SectionConnection.A]
        else:
            raise

    def get_next_section_and_target_junction(self, target_junction: Junction) -> tuple[Section, Junction]:
        """
        セクションと目指すジャンクションから、次のセクションと目指すジャンクションを計算する。
        """

        if target_junction.connected_sections[JunctionConnection.THROUGH] == self:
            next_section = target_junction.connected_sections[JunctionConnection.CONVERGING]
        elif target_junction.connected_sections.get(JunctionConnection.DIVERGING) == self:  # DIVERGING が無い場合がある
            next_section = target_junction.connected_sections[JunctionConnection.CONVERGING]
        elif target_junction.connected_sections[JunctionConnection.CONVERGING] == self:
            if target_junction.current_direction == PointDirection.STRAIGHT:
                next_section = target_junction.connected_sections[JunctionConnection.THROUGH]
            elif target_junction.current_direction == PointDirection.CURVE:
                next_section = target_junction.connected_sections[JunctionConnection.DIVERGING]
            else:
                raise
        else:
            raise

        next_target_junction = next_section.get_opposite_junction(target_junction)
        return next_section, next_target_junction

    def get_next_section_and_target_junction_strict(self, target_junction: Junction) -> tuple[Section, Junction] | None:
        """
        与えられたセクションと目指すジャンクションから、次のセクションと目指すジャンクションを計算する。
        ジャンクションが開通しておらず先に進めない場合は、Noneを返す。
        """

        if target_junction.connected_sections[JunctionConnection.THROUGH] == self:
            if target_junction.current_direction == PointDirection.STRAIGHT:
                next_section = target_junction.connected_sections[JunctionConnection.CONVERGING]
            elif target_junction.current_direction == PointDirection.CURVE:
                return None
            else:
                raise
        elif target_junction.connected_sections.get(JunctionConnection.DIVERGING) == self:  # DIVERGING が無い場合がある
            if target_junction.current_direction == PointDirection.STRAIGHT:
                return None
            elif target_junction.current_direction == PointDirection.CURVE:
                next_section = target_junction.connected_sections[JunctionConnection.CONVERGING]
            else:
                raise
        elif target_junction.connected_sections[JunctionConnection.CONVERGING] == self:
            if target_junction.current_direction == PointDirection.STRAIGHT:
                next_section = target_junction.connected_sections[JunctionConnection.THROUGH]
            elif target_junction.current_direction == PointDirection.CURVE:
                next_section = target_junction.connected_sections[JunctionConnection.DIVERGING]
            else:
                raise
        else:
            raise

        next_target_junction = next_section.get_opposite_junction(target_junction)
        return next_section, next_target_junction


def compute_connected_components(sections: list["Section"]) -> list[set[str]]:
    """
    与えられたセクションの集合に対して連結成分分解を行う。
    すなわち、ポイントの向きに応じて、セクションからセクションにたどり着ける場合に同じグループとみなし、
    そうでない場合は別のグループとみなす。
    """

    def bfs(s0: "Section") -> set[str]:
        que: deque["Section"] = deque()
        visited: set[str] = set()
        que.append(s0)
        visited.add(s0.id)

        while que:
            s = que.popleft()
            for j in s.connected_junctions.values():
                t, _ = s.get_next_section_and_target_junction_strict(j) or (None, None)
                if t is None:
                    continue
                if t.id in visited:
                    continue
                if t not in sections:
                    continue
                que.append(t)
                visited.add(t.id)

        return visited

    components: list[set[str]] = []
    visited: set[str] = set()
    for s in sections:
        if s.id in visited:
            continue
        component = bfs(s)
        components.append(component)
        visited |= component

    return components
