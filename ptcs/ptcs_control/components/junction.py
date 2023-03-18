from .direction import Direction
from .joint import Joint
from .section import Section


class Junction:
    """
    線路の分岐・合流点
    """

    _id: str
    _direction: "Direction"
    _sections: dict["Joint", "Section"]

    def __init__(
        self,
        *,
        id: str,
        initial_direction: "Direction",
    ) -> None:
        self._id = id
        self._direction = initial_direction
        self._sections = {}

    def add_section(self, joint: "Joint", section: "Section") -> None:
        self._sections[joint] = section
