from .joint import Joint
from .junction import Junction


class Section:
    """
    線路の区間
    """

    _id: str
    _length: float
    _junction_0: "Junction"
    _junction_1: "Junction"

    def __init__(
        self,
        *,
        id: str,
        junction_0: "Junction",
        junction_0_joint: "Joint",
        junction_1: "Junction",
        junction_1_joint: "Joint",
        length: float,
    ) -> None:
        self._id = id
        self._length = length

        self._junction_0 = junction_0
        junction_0.add_section(junction_0_joint, self)

        self._junction_1 = junction_1
        junction_1.add_section(junction_1_joint, self)
