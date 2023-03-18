from enum import Enum, auto


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

    THROUGH = auto()
    DIVERGING = auto()
    CONVERGING = auto()
