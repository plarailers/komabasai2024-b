from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseComponent

if TYPE_CHECKING:
    from .junction import Junction
    from .section import Section


@dataclass
class SensorPosition(BaseComponent):
    """センサー位置"""

    id: str

    # config
    section: Section
    mileage: float

    target_junction: Junction
    """
    NOTE: 将来的にはここに向きの情報を持たせなくて良いようにする。
    具体的には、通った向きがわかるようなセンシング技術を用いるか、
    計算で向きを予測するか（限界はある）のどちらか。
    """
