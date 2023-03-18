from enum import Enum, auto


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

    STRAIGHT = auto()
    CURVE = auto()
