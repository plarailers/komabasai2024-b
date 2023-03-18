from enum import Enum, auto


class Direction(Enum):
    """
    分岐・合流点やサーボモーターの方向
    """

    STRAIGHT = auto()
    CURVE = auto()
