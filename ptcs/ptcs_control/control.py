from .railway_config import RailwayConfig, init_config
from .railway_state import RailwayState, init_state


class Control:
    """
    列車制御システムの全体を管理する。
    """

    config: "RailwayConfig"
    state: "RailwayState"

    def __init__(self) -> None:
        self.config = init_config()
        self.state = init_state()

    def get_config(self) -> dict:
        return {"config": self.config.to_json()}

    def get_state(self) -> dict:
        return {"state": self.state.to_json()}
