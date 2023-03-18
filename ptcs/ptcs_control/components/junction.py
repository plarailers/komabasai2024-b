from .direction import Direction
from .section import Section


class Junction:
    """
    線路の分岐・合流点
    """

    _id: str
    _direction: "Direction"
    _converging_sections: dict["Direction", "Section"]
    _diverging_sections: dict["Direction", "Section"]

    def __init__(
        self,
        *,
        id: str,
        initial_direction: "Direction",
    ) -> None:
        self._id = id
        self._direction = initial_direction
        self._converging_sections = {}
        self._diverging_sections = {}

    def add_converging_section(self, direction: "Direction", section: "Section") -> None:
        self._converging_sections[direction] = section

    def add_diverging_section(self, direction: "Direction", section: "Section") -> None:
        self._diverging_sections[direction] = section
