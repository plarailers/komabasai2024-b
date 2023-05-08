import math
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

    def calc_speed(self) -> None:
        BREAK_ACCLT: float = 10  # ブレーキ減速度[cm/s/s]  NOTE:将来的には車両のパラメータとして定義
        MAX_SPEED: float = 40  # 最高速度[cm/s]  NOTE:将来的には車両のパラメータとしてとして定義
        MERGIN: float = 10  # 停止余裕距離[cm]

        for train_id, train_state in self.state.trains.items():
            # [ATP]停止位置までの距離`distance`を、先行列車の位置と、ジャンクションの状態をもとに計算する

            distance = 0

            current_section = train_state.current_section
            target_junction = train_state.target_junction

            while True:
                current_section_config = self.config.sections[current_section]
                current_section_state = self.state.sections[current_section]
                next_section, next_junction = self._get_next_section_and_junction(
                    current_section, target_junction
                )
                next_section_state = self.state.sections[next_section]

                # いま見ているセクションが閉鎖 -> 即時停止
                if current_section_state.blocked is True:
                    distance = 0
                    break

                # 先行列車に到達できる -> 先行列車の手前で停止
                elif self._get_forward_train(train_id):
                    distance = self._get_forward_train(train_id)[1] - MERGIN
                    break

                # 目指すジャンクションが自列車側に開通していない -> 目指すジャンクションの手前で停止
                elif (
                    self._get_next_section_and_junction_strict(
                        current_section, target_junction
                    )
                    is None
                ):
                    if target_junction == current_section_config.junction_0:
                        distance = train_state.mileage - MERGIN
                    elif target_junction == current_section_config.junction_1:
                        distance = (
                            current_section_config.length - train_state.mileage - MERGIN
                        )
                    else:
                        raise
                    break

                # 次のセクションが閉鎖 -> 目指すジャンクションの手前で停止
                elif next_section_state.blocked is True:
                    if target_junction == current_section_config.junction_0:
                        distance = train_state.mileage - MERGIN
                    elif target_junction == current_section_config.junction_1:
                        distance = (
                            current_section_config.length - train_state.mileage - MERGIN
                        )
                    else:
                        raise
                    break

                # 停止条件を満たさなければ次に移る
                else:
                    (
                        current_section,
                        target_junction,
                    ) = self._get_next_section_and_junction(
                        current_section, target_junction
                    )

            if distance < 0:
                distance = 0

            # [ATP]停止位置までの距離を使って、列車の許容速度`speedlimit`を計算する

            speedlimit = math.sqrt(2 * BREAK_ACCLT * distance)
            if speedlimit > MAX_SPEED:
                speedlimit = MAX_SPEED

            print(train_id, distance, speedlimit)

            # [ATO]停車駅の情報から、停止位置を取得する
            # [ATO]ATPで計算した許容速度の範囲内で、停止位置で止まるための速度を計算する

    def _get_forward_train(self, train: Train) -> tuple[Train, float] | None:
        """
        指定された列車の先行列車とその距離を取得する。
        ジャンクションの開通方向によっては先行列車に到達できない場合があり、そのときはNoneを返す。
        """

        section = self.state.trains[train].current_section
        section_config = self.config.sections[section]
        target_junction = self.state.trains[train].target_junction
        mileage = self.state.trains[train].mileage

        distance: float = 0

        while True:
            distances: dict[Train, float] = {}

            # section 内に存在する列車のうち、先行列車(=mileageの位置から
            # バックではなく前進して到達できるもの)を取得し`distance`に入れる

            for train_id, train_state in self.state.trains.items():
                # section 内に存在する列車
                if train_state.current_section == section:
                    # 端点0(target_junction)<---|train|---mileage---<端点1
                    if target_junction == section_config.junction_0:
                        if train_state.mileage < mileage:
                            distances[train_id] = mileage - train_state.mileage

                    # 端点0>---mileage---|train|--->端点1(target_junction)
                    elif target_junction == section_config.junction_1:
                        if mileage < train_state.mileage:
                            distances[train_id] = train_state.mileage - mileage

                    else:
                        raise

            # 先行列車を発見した場合、もっとも近いものを取り出して返す
            if distances:
                nearest_train_id = min(distances, key=distances.get)
                return (nearest_train_id, distance + distances[nearest_train_id])

            # 先行列車を発見しなかった場合、検索対象を次のセクションに移す
            else:
                # 端点0(target_junction)<---mileage--<端点1
                if target_junction == section_config.junction_0:
                    distance += mileage
                # 端点0>--mileage--->端点1(target_junction)
                elif target_junction == section_config.junction_1:
                    distance += section_config.length - mileage
                else:
                    raise
                next = self._get_next_section_and_junction_strict(
                    section, target_junction
                )
                if next:
                    section, target_junction = next
                    section_config = self.config.sections[section]
                    # 端点0(target_junction)<-----mileage<端点1
                    if target_junction == section_config.junction_0:
                        mileage = section_config.length
                    # 端点0>mileage----->端点1(target_junction)
                    elif target_junction == section_config.junction_1:
                        mileage = 0
                    else:
                        raise
                else:
                    return None  # ジャンクションが開通しておらず到達できない

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
        next_target_junction = next_section_config.get_opposite_junction(
            target_junction
        )
        return next_section, next_target_junction

    def _get_next_section_and_junction_strict(
        self, current_section: Section, target_junction: Junction
    ) -> tuple[Section, Junction] | None:
        """
        与えられたセクションと目指すジャンクションから、次のセクションと目指すジャンクションを計算する。
        ジャンクションが開通しておらず先に進めない場合は、Noneを返す。
        """

        target_junction_config = self.config.junctions[target_junction]
        target_junction_state = self.state.junctions[target_junction]

        if target_junction_config.sections[Joint.THROUGH] == current_section:
            if target_junction_state.direction == Direction.STRAIGHT:
                next_section = target_junction_config.sections[Joint.CONVERGING]
            elif target_junction_state.direction == Direction.CURVE:
                return None
            else:
                raise
        elif target_junction_config.sections[Joint.DIVERGING] == current_section:
            if target_junction_state.direction == Direction.STRAIGHT:
                return None
            elif target_junction_state.direction == Direction.CURVE:
                next_section = target_junction_config.sections[Joint.CONVERGING]
            else:
                raise
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
        next_target_junction = next_section_config.get_opposite_junction(
            target_junction
        )
        return next_section, next_target_junction
