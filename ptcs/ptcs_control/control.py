from .state import State, init_state


class Control:
    """
    列車制御システムの全体を管理する。
    """

    state: State

    def __init__(self) -> None:
        self.state = init_state()

    def get_state(self) -> dict:
        return {"state": self.state.to_json()}
