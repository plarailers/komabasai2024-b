from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .stop import Stop


@dataclass
class Station(BaseComponent):
    """駅"""

    id: str

    # config
    stops: list[Stop] = field(default_factory=list)
