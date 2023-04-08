from .components import Direction, Joint, Train
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

    def get_config(self) -> "RailwayConfig":
        return self.config

    def get_state(self) -> "RailwayState":
        return self.state

    def move_train(self, train_id: "Train", delta: float) -> None:
        train_state = self.state.trains[train_id]
        current_section_config = self.config.sections[train_state.current_section]
        train_state.mileage += delta

        while train_state.mileage >= current_section_config.length:
            train_state.mileage -= current_section_config.length

            target_junction_config = self.config.junctions[train_state.target_junction]
            target_junction_state = self.state.junctions[train_state.target_junction]

            if target_junction_config.sections[Joint.THROUGH] == train_state.current_section:
                next_section = target_junction_config.sections[Joint.CONVERGING]
            elif target_junction_config.sections[Joint.DIVERGING] == train_state.current_section:
                next_section = target_junction_config.sections[Joint.CONVERGING]
            elif target_junction_config.sections[Joint.CONVERGING] == train_state.current_section:
                if target_junction_state.direction == Direction.STRAIGHT:
                    next_section = target_junction_config.sections[Joint.THROUGH]
                elif target_junction_state.direction == Direction.CURVE:
                    next_section = target_junction_config.sections[Joint.DIVERGING]
                else:
                    raise
            else:
                raise

            train_state.current_section = next_section
            next_section_config = self.config.sections[next_section]
            train_state.target_junction = next_section_config.get_opposite_junction(train_state.target_junction)
