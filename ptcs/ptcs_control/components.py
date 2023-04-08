from enum import Enum
from typing import NewType


Junction = NewType("Junction", str)
"""
線路の分岐・合流点を表す識別子
"""

Section = NewType("Section", str)
"""
線路の区間を表す識別子
"""

Train = NewType("Train", str)
"""
列車を表す識別子
"""


class Direction(Enum):
    """
    サーボモーターの方向を表す列挙型

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
    ターンアウトレールにおける分岐・合流の接続のしかたを表す列挙型

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
