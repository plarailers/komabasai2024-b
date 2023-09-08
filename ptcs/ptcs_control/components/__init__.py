from enum import Enum
from typing import NewType

StationId = NewType("StationId", str)
"""
駅を表す識別子
"""

StopId = NewType("StopId", str)
"""
停止目標を表す識別子
"""


class Direction(Enum):
    r"""
    サーボモーターの方向を表す列挙型

    ```
    _______________
    ______  _______ straight
          \ \______
           \_______ curve
    ```
    """

    STRAIGHT = "straight"
    CURVE = "curve"


class Joint(str, Enum):
    r"""
    ターンアウトレールにおける分岐・合流の接続のしかたを表す列挙型

    ```
               _______________
    converging ______  _______ through
                     \ \______
                      \_______ diverging
    ```

    NOTE: いい名前を募集中
    """

    THROUGH = "through"
    DIVERGING = "diverging"
    CONVERGING = "converging"
