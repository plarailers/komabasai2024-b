from .direction import Direction
from .junction import Junction


class Section:
    """
    線路の区間
    """

    _id: str
    _length: float
    _source_junction: "Junction"
    _target_junction: "Junction"

    def __init__(
        self,
        *,
        id: str,
        source_junction: "Junction",
        source_direction: "Direction",
        target_junction: "Junction",
        target_direction: "Direction",
        length: float,
    ) -> None:
        self._id = id
        self._length = length

        self._source_junction = source_junction
        source_junction.add_diverging_section(source_direction, self)

        self._target_junction = target_junction
        target_junction.add_converging_section(target_direction, self)
