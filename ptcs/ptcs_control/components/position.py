from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .section import SectionConnection

if TYPE_CHECKING:
    from .junction import Junction
    from .section import Section


@dataclass(frozen=True)
class UndirectedPosition:
    """線路上の汎用的な位置"""

    section: Section
    mileage: float


@dataclass(frozen=True)
class DirectedPosition:
    """線路上の汎用的な位置と方向"""

    section: Section
    target_junction: Junction
    mileage: float

    def get_reversed(self) -> DirectedPosition:
        return DirectedPosition(self.section, self.section.get_opposite_junction(self.target_junction), self.mileage)

    def get_advanced_position(self, delta: float) -> DirectedPosition:
        """
        現在の位置と方向から距離 `delta` 分だけ進んだ位置と方向を計算する。
        """

        section = self.section
        target_junction = self.target_junction
        mileage = self.mileage

        if target_junction == section.connected_junctions[SectionConnection.B]:
            mileage += delta
        elif target_junction == section.connected_junctions[SectionConnection.A]:
            mileage -= delta
        else:
            raise

        while mileage > section.length or mileage < 0:
            if mileage > section.length:
                surplus_mileage = mileage - section.length
            elif mileage < 0:
                surplus_mileage = -mileage
            else:
                raise

            section, target_junction = section.get_next_section_and_target_junction(target_junction)

            if target_junction == section.connected_junctions[SectionConnection.B]:
                mileage = surplus_mileage
            elif target_junction == section.connected_junctions[SectionConnection.A]:
                mileage = section.length - surplus_mileage
            else:
                raise

        return DirectedPosition(section, target_junction, mileage)

    def get_retracted_position(self, delta: float) -> DirectedPosition:
        """
        現在の位置と方向から距離 `delta` 分だけ退いた位置と方向を計算する。
        """

        return self.get_reversed().get_advanced_position(delta).get_reversed()

    def get_advanced_position_with_path(self, delta: float) -> tuple[DirectedPosition, list[Section]]:
        """
        現在の位置と方向から距離 `delta` 分だけ進んだ位置と方向を計算し、
        そこまでに通過したセクションとともに返す。
        """

        path: list[Section] = []

        section = self.section
        target_junction = self.target_junction
        mileage = self.mileage

        if target_junction == section.connected_junctions[SectionConnection.B]:
            mileage += delta
        elif target_junction == section.connected_junctions[SectionConnection.A]:
            mileage -= delta
        else:
            raise

        while mileage > section.length or mileage < 0:
            if mileage > section.length:
                surplus_mileage = mileage - section.length
            elif mileage < 0:
                surplus_mileage = -mileage
            else:
                raise

            section, target_junction = section.get_next_section_and_target_junction(target_junction)

            if target_junction == section.connected_junctions[SectionConnection.B]:
                mileage = surplus_mileage
            elif target_junction == section.connected_junctions[SectionConnection.A]:
                mileage = section.length - surplus_mileage
            else:
                raise

            path.append(section)

        if path:
            path.pop()

        return DirectedPosition(section, target_junction, mileage), path

    def get_retracted_position_with_path(self, delta: float) -> tuple[DirectedPosition, list[Section]]:
        """
        現在の位置と方向から距離 `delta` 分だけ退いた位置と方向を計算し、
        そこまでに通過したセクションとともに返す。
        """

        position, path = self.get_reversed().get_advanced_position_with_path(delta)
        return position.get_reversed(), list(reversed(path))
