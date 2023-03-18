from enum import Enum


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


class Direction(Enum):
    """
    サーボモーターの方向

    ```
    _______________
    ______  _______ STRAIGHT
          \ \______
           \_______ CURVE
    ```
    """

    STRAIGHT = "STRAIGHT"
    CURVE = "CURVE"


class Joint(Enum):
    """
    ターンアウトレールにおける分岐・合流の接続のしかた

    ```
               _______________
    CONVERGING ______  _______ THROUGH
                     \ \______
                      \_______ DIVERGING
    ```

    NOTE: いい名前を募集中
    """

    THROUGH = "THROUGH"
    DIVERGING = "DIVERGING"
    CONVERGING = "CONVERGING"
