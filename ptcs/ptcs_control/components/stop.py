from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .position import DirectedPosition


@dataclass
class Stop(BaseComponent):
    """停止目標"""

    id: str

    # config
    position: DirectedPosition
