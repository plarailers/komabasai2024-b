from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..components.section import Section
    from ..components.train import Train


@dataclass
class TrainSectionChanged:
    "列車先頭の位置する区間が変わったことを表すイベント"
    train: Train
    previous_section: Section
    current_section: Section


Event = TrainSectionChanged
