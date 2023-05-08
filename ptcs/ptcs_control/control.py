from .components import Direction, Joint, Junction, Section, Train
from .railway_config import RailwayConfig, init_config
from .railway_state import RailwayState, init_state
from .railway_command import RailwayCommand, init_command


class Control:
    """
    列車制御システムの全体を管理する。
    """

    config: "RailwayConfig"
    state: "RailwayState"
    command: "RailwayCommand"

    def __init__(self) -> None:
        self.config = init_config()
        self.state = init_state()
        self.command = init_command()

    def get_config(self) -> "RailwayConfig":
        return self.config

    def get_state(self) -> "RailwayState":
        return self.state

    def get_command(self) -> "RailwayCommand":
        return self.command

    def block_section(self, section_id: "Section") -> None:
        """
        指定された区間上に障害物を発生させ、使えなくさせる。
        """
        self.state.sections[section_id].blocked = True

    def unblock_section(self, section_id: "Section") -> None:
        """
        指定された区間上の障害物を取り除き、使えるようにする。
        """
        self.state.sections[section_id].blocked = False

    def toggle_junction(self, junction_id: "Junction", direction: "Direction") -> None:
        """
        指定された分岐・合流点の方向を指示する。
        """

        self.command.junctions[junction_id] = direction

    def set_speed(self, train_id: "Train", speed: float) -> None:
        """
        指定された列車の速度を指示する。
        """

        self.command.trains[train_id].speed = speed

    def update_junction(self, junction_id: "Junction", direction: "Direction") -> None:
        """
        指定された分岐・合流点の方向を更新する。
        """

        self.state.junctions[junction_id].direction = direction

    def move_train(self, train_id: "Train", delta: float) -> None:
        """
        指定された列車を距離 delta 分だけ進める。
        """

        train_state = self.state.trains[train_id]
        current_section_config = self.config.sections[train_state.current_section]
        train_state.mileage += delta

        while train_state.mileage >= current_section_config.length:
            train_state.mileage -= current_section_config.length

            next_section, next_target_junction = self._get_next_section_and_junction(
                train_state.current_section, train_state.target_junction
            )

            train_state.current_section = next_section
            train_state.target_junction = next_target_junction

    def calc_speed(self) -> None:
        # [ATP]停止位置までの距離を、先行列車の位置と、ジャンクションの状態をもとに計算する
        # [ATP]停止位置までの距離を使って、列車の許容速度を計算する
        # [ATO]停車駅の情報から、停止位置を取得する
        # [ATO]ATPで計算した許容速度の範囲内で、停止位置で止まるための速度を計算する
        pass
    
    def _get_next_section_and_junction(
        self, current_section: Section, target_junction: Junction
    ) -> tuple[Section, Junction]:
        """
        与えられたセクションと目指すジャンクションから、次のセクションと目指すジャンクションを計算する。
        """

        target_junction_config = self.config.junctions[target_junction]
        target_junction_state = self.state.junctions[target_junction]

        if target_junction_config.sections[Joint.THROUGH] == current_section:
            next_section = target_junction_config.sections[Joint.CONVERGING]
        elif target_junction_config.sections[Joint.DIVERGING] == current_section:
            next_section = target_junction_config.sections[Joint.CONVERGING]
        elif target_junction_config.sections[Joint.CONVERGING] == current_section:
            if target_junction_state.direction == Direction.STRAIGHT:
                next_section = target_junction_config.sections[Joint.THROUGH]
            elif target_junction_state.direction == Direction.CURVE:
                next_section = target_junction_config.sections[Joint.DIVERGING]
            else:
                raise
        else:
            raise

        next_section_config = self.config.sections[next_section]
        next_target_junction = next_section_config.get_opposite_junction(target_junction)
        return next_section, next_target_junction
