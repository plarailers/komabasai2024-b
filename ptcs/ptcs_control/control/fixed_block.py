from .base import BaseControl


class FixedBlockControl(BaseControl):
    """
    固定閉塞システムの全体を管理する。
    """

    def update(self) -> None:
        """
        状態に変化が起こった後、すべてを再計算する。
        """
        pass
