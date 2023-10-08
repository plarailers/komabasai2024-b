from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .section import Section


@dataclass
class Obstacle(BaseComponent):
    """障害物"""

    id: str

    # config
    section: Section
    mileage: float

    # state
    is_detected: bool

    def verify(self) -> None:
        super().verify()
        assert 0 <= self.mileage <= self.section.length, f"{self}.length is wrong"
