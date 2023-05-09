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

        if train_state.target_junction == current_section_config.junction_1:
            train_state.mileage += delta
        elif train_state.target_junction == current_section_config.junction_0:
            train_state.mileage -= delta
        else:
            raise

        while (
            train_state.mileage > current_section_config.length
            or train_state.mileage < 0
        ):
            if train_state.mileage > current_section_config.length:
                surplus_mileage = train_state.mileage - current_section_config.length
            elif train_state.mileage < 0:
                surplus_mileage = -train_state.mileage
            else:
                raise

            next_section, next_target_junction = self._get_next_section_and_junction(
                train_state.current_section, train_state.target_junction
            )

            train_state.current_section = next_section
            current_section_config = self.config.sections[next_section]
            train_state.target_junction = next_target_junction
            if train_state.target_junction == current_section_config.junction_1:
                train_state.mileage = surplus_mileage
            elif train_state.target_junction == current_section_config.junction_0:
                train_state.mileage = current_section_config.length - surplus_mileage
            else:
                raise

    def calc_direction(self) -> None:
        """
        ポイントをどちら向きにするかを計算する。
        """

        # junction定義
        j0a = Junction("j0a")
        j0b = Junction("j0b")
        j1a = Junction("j1a")
        j1b = Junction("j1b")
        # sectionの定義
        s1 = Section("s1")
        s2 = Section("s2")
        s3 = Section("s3")
        s5 = Section("s5")
        # 「とりうるルート」の列挙
        possible_junction_direction: dict[str, list[tuple[Junction, Direction]]] = {
            "normal": [(j0a, Direction.STRAIGHT),
                       (j0b, Direction.STRAIGHT),
                       (j1a, Direction.STRAIGHT),
                       (j1b, Direction.STRAIGHT)],
            "blocked1": [(j0a, Direction.CURVE),
                         (j0b, Direction.STRAIGHT),
                         (j1a, Direction.CURVE),
                         (j1b, Direction.STRAIGHT)],
            "blocked2": [(j0a, Direction.CURVE),
                         (j0b, Direction.CURVE),
                         (j1a, Direction.CURVE),
                         (j1b, Direction.CURVE)]
        }

        # 列車位置と線路の状態（障害物の有無）に応じてどのルートを使うか判断する
        # s3がblockされているか
        s3_blocked: bool = self.state.sections[s3].blocked

        train_states = self.state.trains
        # s1にtarget_junctionがj1bであるtrainが存在するか
        s1_j1b_exist: bool = False
        # s2に列車が存在するか
        s2_exist: bool = False
        # s5にtrainが存在するか
        s5_exist: bool = False
        for train_state in train_states.values():
            if train_state.current_section == s1 and train_state.target_junction == j1b:
                s1_j1b_exist = True
            if train_state.current_section == s2:
                s2_exist = True
            if train_state.current_section == s5:
                s5_exist = True

        # ポイントの向きを判定
        junction_direction: list[tuple[Junction, Direction]]
        if not s3_blocked:
            junction_direction = possible_junction_direction["normal"]
        elif s1_j1b_exist or (not s2_exist and not s5_exist):
            junction_direction = possible_junction_direction["blocked1"]
        elif not s1_j1b_exist and (s2_exist or s5_exist):
            junction_direction = possible_junction_direction["blocked2"]

        # ポイント変更
        for junction_id, direction in junction_direction:
            self.update_junction(junction_id=junction_id, direction=direction)

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
