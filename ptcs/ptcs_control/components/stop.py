from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .junction import Junction
    from .section import Section


@dataclass
class Stop(BaseComponent):
    """停止目標"""

    id: str

    # config
    section: Section
    target_junction: Junction
    mileage: float
