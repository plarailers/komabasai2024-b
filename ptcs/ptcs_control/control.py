from __future__ import annotations

import logging
import math

from .components import Direction, Joint
from .components.junction import Junction
from .components.section import Section, SectionConnection
from .components.sensor_position import SensorPosition
from .components.station import Station
from .components.stop import Stop
from .components.train import Train
from .constants import (
    CURVE_RAIL,
    STRAIGHT_1_4_RAIL,
    STRAIGHT_RAIL,
    WATARI_RAIL_A,
    WATARI_RAIL_B,
    WATARI_RAIL_C,
)


class Control:
    """
    列車制御システムの全体を管理する。
    """

    _current_time: int  # 現在時刻

    junctions: dict[str, Junction]
    sections: dict[str, Section]
    trains: dict[str, Train]
    stops: dict[str, Stop]
    stations: dict[str, Station]
    sensor_positions: dict[str, SensorPosition]

    logger: logging.Logger

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._current_time = 0

        self.junctions = {}
        self.sections = {}
        self.trains = {}
        self.stops = {}
        self.stations = {}
        self.sensor_positions = {}

        # TODO: 適切な場所に移動する
        j0a = Junction(id="j0")
        j0b = Junction(id="j1")
        j1a = Junction(id="j2")
        j1b = Junction(id="j3")

        self.add_junction(j0a)
        self.add_junction(j0b)
        self.add_junction(j1a)
        self.add_junction(j1b)

        s0 = Section(
            id="s0",
            length=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 14 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1 + WATARI_RAIL_A * 1,
        )
        s1 = Section(
            id="s1",
            length=STRAIGHT_RAIL * 3 + WATARI_RAIL_B * 2,
        )
        s2 = Section(
            id="s2",
            length=WATARI_RAIL_A * 1 + STRAIGHT_RAIL * 6 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1 + WATARI_RAIL_B * 1,
        )
        s3 = Section(
            id="s3",
            length=WATARI_RAIL_A * 2 + STRAIGHT_RAIL * 3,
        )
        s4 = Section(
            id="s4",
            length=WATARI_RAIL_C,
        )
        s5 = Section(
            id="s5",
            length=WATARI_RAIL_C,
        )

        self.add_section(s0)
        self.add_section(s1)
        self.add_section(s2)
        self.add_section(s3)
        self.add_section(s4)
        self.add_section(s5)

        A, B = SectionConnection.A, SectionConnection.B
        self.connect(s0, A, j0a, Joint.CONVERGING)
        self.connect(s0, B, j0b, Joint.THROUGH)
        self.connect(s1, A, j0b, Joint.CONVERGING)
        self.connect(s1, B, j1b, Joint.CONVERGING)
        self.connect(s2, A, j1b, Joint.THROUGH)
        self.connect(s2, B, j1a, Joint.CONVERGING)
        self.connect(s3, A, j1a, Joint.THROUGH)
        self.connect(s3, B, j0a, Joint.THROUGH)
        self.connect(s4, A, j0a, Joint.DIVERGING)
        self.connect(s4, B, j0b, Joint.DIVERGING)
        self.connect(s5, A, j1a, Joint.DIVERGING)
        self.connect(s5, B, j1b, Joint.DIVERGING)

        t0 = Train(
            id="t0",
            min_input=70,
            max_input=130,
            max_speed=40.0,
            delta_per_motor_rotation=0.2435 * 0.9,
            current_section=s0,
            target_junction=j0b,
            mileage=STRAIGHT_RAIL * 4.5 + WATARI_RAIL_B + 1,  # 次駅探索の都合上、stopを1cm通り過ぎた場所にしておく
        )  # Dr
        t1 = Train(
            id="t1",
            min_input=90,
            max_input=130,
            max_speed=40.0,
            delta_per_motor_rotation=0.1919 * 1.1 * 0.9,
            current_section=s1,
            target_junction=j1b,
            mileage=STRAIGHT_RAIL * 2.5 + WATARI_RAIL_B + 1,
        )  # E6
        # E5はAPS故障につきまだ運用しない

        self.add_train(t0)
        self.add_train(t1)

        stop_0 = Stop(
            id="stop_0",
            section=s0,
            target_junction=j0b,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 4.5,
        )
        stop_1 = Stop(
            id="stop_1",
            section=s0,
            target_junction=j0b,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 10.0 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
        )
        stop_2 = Stop(
            id="stop_2",
            section=s1,
            target_junction=j0b,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 1.5,
        )
        stop_3 = Stop(
            id="stop_3",
            section=s1,
            target_junction=j1b,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 1.5,
        )
        stop_4 = Stop(
            id="stop_4",
            section=s3,
            target_junction=j0a,
            mileage=WATARI_RAIL_A * 1 + STRAIGHT_RAIL * 1.5,
        )

        self.add_stop(stop_0)
        self.add_stop(stop_1)
        self.add_stop(stop_2)
        self.add_stop(stop_3)
        self.add_stop(stop_4)

        station_0 = Station(id="station_0", stops=[stop_0, stop_1])
        station_1 = Station(id="station_1", stops=[stop_2, stop_3, stop_4])

        self.add_station(station_0)
        self.add_station(station_1)

        position_173 = SensorPosition(
            id="position_173",
            section=s0,
            target_junction=j0b,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 2.5,
        )
        position_138 = SensorPosition(
            id="position_138",
            section=s0,
            target_junction=j0b,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 9.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
        )
        position_80 = SensorPosition(
            id="position_80",
            section=s0,
            target_junction=j0b,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 13.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
        )
        position_255 = SensorPosition(
            id="position_255",
            section=s2,
            target_junction=j1a,
            mileage=WATARI_RAIL_A * 1 + STRAIGHT_RAIL * 5.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
        )

        self.add_sensor_position(position_173)
        self.add_sensor_position(position_138)
        self.add_sensor_position(position_80)
        self.add_sensor_position(position_255)

        if logger is None:
            logger = logging.getLogger(__name__)
            logger.addHandler(logging.NullHandler())

        self.logger = logger

        self.verify()

    def add_junction(self, junction: Junction) -> None:
        assert junction.id not in self.junctions
        self.junctions[junction.id] = junction
        junction._control = self

    def add_section(self, section: Section) -> None:
        assert section.id not in self.sections
        self.sections[section.id] = section
        section._control = self

    def connect(
        self,
        section: Section,
        section_connection: SectionConnection,
        junction: Junction,
        junction_connection: Joint,
    ) -> None:
        assert section_connection not in section.connected_junctions
        section.connected_junctions[section_connection] = junction

        assert junction_connection not in junction.connected_sections
        junction.connected_sections[junction_connection] = section

    def add_train(self, train: Train) -> None:
        assert train.id not in self.trains
        self.trains[train.id] = train
        train._control = self

    def add_stop(self, stop: Stop) -> None:
        assert stop.id not in self.stops
        self.stops[stop.id] = stop
        stop._control = self

    def add_station(self, station: Station) -> None:
        assert station.id not in self.stations
        self.stations[station.id] = station
        station._control = self

    def add_sensor_position(self, position: SensorPosition) -> None:
        assert position.id not in self.sensor_positions
        self.sensor_positions[position.id] = position
        position._control = self

    def verify(self) -> None:
        for junction in self.junctions.values():
            junction.verify()
        for section in self.sections.values():
            section.verify()
        for train in self.trains.values():
            train.verify()
        for stop in self.stops.values():
            stop.verify()
        for position in self.sensor_positions.values():
            position.verify()

    @property
    def current_time(self) -> int:
        return self._current_time

    @current_time.setter
    def current_time(self, value) -> None:
        self.logger.info(f"current_time = {value}")
        self._current_time = value

    def tick(self, increment: int = 1) -> None:
        """
        内部時刻を進める。
        """
        self.current_time += increment

    def block_section(self, section: Section) -> None:
        """
        指定された区間上に障害物を発生させ、使えなくさせる。
        """
        section.is_blocked = True

    def unblock_section(self, section: Section) -> None:
        """
        指定された区間上の障害物を取り除き、使えるようにする。
        """
        section.is_blocked = False

    def toggle_junction(self, junction: Junction, direction: Direction) -> None:
        """
        指定された分岐・合流点の方向を指示する。
        """

        junction.command_direction = direction

    def set_speed(self, train: Train, speed: float) -> None:
        """
        指定された列車の速度を指示する。
        """

        train.command_speed = speed

    def update_junction(self, junction: Junction, direction: Direction) -> None:
        """
        指定された分岐・合流点の方向を更新する。
        """

        junction.current_direction = direction

    def move_train_mr(self, train: Train, motor_rotation: int) -> None:
        """
        指定された列車をモータ motor_rotation 回転分だけ進める
        """

        delta_per_motor_rotation = train.delta_per_motor_rotation
        self.move_train(train, motor_rotation * delta_per_motor_rotation)

    def move_train(self, train: Train, delta: float) -> None:
        """
        指定された列車を距離 delta 分だけ進める。
        """

        current_section = train.current_section

        if train.target_junction == current_section.connected_junctions[SectionConnection.B]:
            train.mileage += delta
        elif train.target_junction == current_section.connected_junctions[SectionConnection.A]:
            train.mileage -= delta
        else:
            raise

        while train.mileage > current_section.length or train.mileage < 0:
            if train.mileage > current_section.length:
                surplus_mileage = train.mileage - current_section.length
            elif train.mileage < 0:
                surplus_mileage = -train.mileage
            else:
                raise

            next_section, next_target_junction = self._get_next_section_and_junction(
                train.current_section, train.target_junction
            )

            train.current_section = next_section
            current_section = next_section
            train.target_junction = next_target_junction
            if train.target_junction == current_section.connected_junctions[SectionConnection.B]:
                train.mileage = surplus_mileage
            elif train.target_junction == current_section.connected_junctions[SectionConnection.A]:
                train.mileage = current_section.length - surplus_mileage
            else:
                raise

    def put_train(self, train: Train, sensor: SensorPosition) -> None:
        """
        指定された列車の位置を修正する。
        TODO: 向きを割り出すためにどうするか
        """

        train.current_section = sensor.section
        train.target_junction = sensor.target_junction
        train.mileage = sensor.mileage

    def update(self) -> None:
        """
        状態に変化が起こった後、すべてを再計算する。
        """
        self._calc_direction()
        self._calc_stop()
        self._calc_speed()

    def _calc_direction(self) -> None:
        """
        ポイントをどちら向きにするかを計算する。
        """

        # junction定義
        j0a = self.junctions["j0"]
        j0b = self.junctions["j1"]
        j1a = self.junctions["j2"]
        j1b = self.junctions["j3"]
        # sectionの定義
        s1 = self.sections["s1"]
        s3 = self.sections["s3"]
        s4 = self.sections["s4"]
        s5 = self.sections["s5"]
        # 「とりうるルート」の列挙
        possible_junction_direction: dict[str, list[tuple[Junction, Direction]]] = {
            "pattern1": [
                (j0a, Direction.STRAIGHT),
                (j0b, Direction.STRAIGHT),
                (j1a, Direction.STRAIGHT),
                (j1b, Direction.STRAIGHT),
            ],
            "pattern2": [
                (j0a, Direction.CURVE),
                (j0b, Direction.CURVE),
                (j1a, Direction.STRAIGHT),
                (j1b, Direction.STRAIGHT),
            ],
            "pattern3": [
                (j0a, Direction.CURVE),
                (j0b, Direction.STRAIGHT),
                (j1a, Direction.CURVE),
                (j1b, Direction.STRAIGHT),
            ],
            "pattern4": [
                (j0a, Direction.CURVE),
                (j0b, Direction.CURVE),
                (j1a, Direction.CURVE),
                (j1b, Direction.CURVE),
            ],
        }

        # 列車位置と線路の状態（障害物の有無）に応じてどのルートを使うか判断する
        # s3がblockされているか
        s3_blocked: bool = s3.is_blocked

        # s1にtarget_junctionがj0bであるtrainが存在するか
        s1_j0b_exist: bool = False
        # s1にtarget_junctionがj1bであるtrainが存在するか
        s1_j1b_exist: bool = False
        # s4にtrainが存在するか
        s4_exist: bool = False
        # s5にtrainが存在するか
        s5_exist: bool = False
        for train in self.trains.values():
            if train.current_section == s1 and train.target_junction == j0b:
                s1_j0b_exist = True
            if train.current_section == s1 and train.target_junction == j1b:
                s1_j1b_exist = True
            if train.current_section == s4:
                s4_exist = True
            if train.current_section == s5:
                s5_exist = True

        # ポイントの向きを判定
        junction_direction: list[tuple[Junction, Direction]]
        if s3_blocked:
            if not s1_j0b_exist and (s1_j1b_exist or not s5_exist):
                junction_direction = possible_junction_direction["pattern3"]
            elif s1_j0b_exist or (not s1_j1b_exist and s5_exist):
                junction_direction = possible_junction_direction["pattern4"]
            else:
                raise
        else:
            if not s1_j0b_exist and not s4_exist and not s5_exist:
                junction_direction = possible_junction_direction["pattern1"]
            elif (s1_j0b_exist or s4_exist) and not s5_exist:
                junction_direction = possible_junction_direction["pattern2"]
            elif not s1_j0b_exist and (s1_j1b_exist or not s5_exist):
                junction_direction = possible_junction_direction["pattern3"]
            elif not s1_j1b_exist and s5_exist:
                junction_direction = possible_junction_direction["pattern4"]
            else:
                raise

        # ポイント変更
        for junction, direction in junction_direction:
            if not self.junction_toggle_prohibited(junction):
                self.update_junction(junction, direction)

    def junction_toggle_prohibited(self, junction: Junction) -> bool:
        """
        指定されたjunctionを列車が通過中であり、切り替えてはいけない場合にTrueを返す
        """

        MERGIN: float = 40  # ポイント通過後すぐに切り替えるとまずいので余裕距離をとる
        TRAIN_LENGTH: float = 60  # 列車の長さ[cm] NOTE: 将来的には車両等のパラメータとして外に出す

        for train in self.trains.values():
            # 列車の最後尾からMERGIN離れた位置(tail_section, tail_mileage, tail_target_junction)を取得
            (
                tail_section,
                tail_mileage,
                tail_target_junction_opposite,
            ) = self._get_new_position(
                train.current_section,
                train.mileage,
                train.current_section.get_opposite_junction(train.target_junction),  # 進行方向と反対向きにたどる
                TRAIN_LENGTH + MERGIN,
            )
            tail_target_junction = tail_section.get_opposite_junction(
                tail_target_junction_opposite  # 進行方向と反対のjunctionなので元に戻す
            )

            # 列車の先頭は指定されたjunctionに向かっていないが、
            # 列車の最後尾は指定されたjunctionに向かっている場合、
            # 列車はそのjunctinoを通過中なので、切り替えを禁止する
            if train.target_junction != junction and tail_target_junction == junction:
                return True

        return False  # 誰も通過していなければFalseを返す

    def _calc_speed(self) -> None:
        BREAK_ACCLT: float = 10  # ブレーキ減速度[cm/s/s]  NOTE:将来的には車両のパラメータとして定義
        NORMAL_ACCLT: float = 5  # 常用加減速度[cm/s/s]  NOTE:将来的には車両のパラメータとして定義
        MAX_SPEED: float = 40  # 最高速度[cm/s]  NOTE:将来的には車両のパラメータとしてとして定義
        MERGIN: float = 10  # 停止余裕距離[cm]

        for train in self.trains.values():
            # [ATP]停止位置までの距離`distance`を、先行列車の位置と、ジャンクションの状態をもとに計算する

            distance = 0.0

            current_section = train.current_section
            target_junction = train.target_junction

            while True:
                next_section, next_junction = self._get_next_section_and_junction(current_section, target_junction)

                # いま見ているセクションが閉鎖 -> 即時停止
                # ただしすでに列車が閉鎖セクションに入ってしまった場合は、駅まで動かしたいので、止めない
                if current_section != train.current_section and current_section.is_blocked is True:
                    distance += 0
                    break

                # 先行列車に到達できる -> 先行列車の手前で停止
                elif forward_train_and_distance := self._get_forward_train(train):
                    distance += forward_train_and_distance[1] - MERGIN
                    break

                # 目指すジャンクションが自列車側に開通していない or 次のセクションが閉鎖
                # -> 目指すジャンクションの手前で停止
                elif (
                    self._get_next_section_and_junction_strict(current_section, target_junction) is None
                    or next_section.is_blocked is True
                ):
                    if current_section == train.current_section:
                        if target_junction == current_section.connected_junctions[SectionConnection.A]:
                            distance += train.mileage - MERGIN
                        elif target_junction == current_section.connected_junctions[SectionConnection.B]:
                            distance += current_section.length - train.mileage - MERGIN
                        else:
                            raise
                    else:
                        distance += current_section.length - MERGIN
                    break

                # 次のセクションが閉鎖 -> 目指すジャンクションの手前で停止
                elif next_section.is_blocked is True:
                    if target_junction == current_section.connected_junctions[SectionConnection.A]:
                        distance += train.mileage - MERGIN
                    elif target_junction == current_section.connected_junctions[SectionConnection.B]:
                        distance += current_section.length - train.mileage - MERGIN
                    else:
                        raise
                    break

                # 停止条件を満たさなければ次に移る
                else:
                    if current_section == train.current_section:
                        if train.target_junction == current_section.connected_junctions[SectionConnection.A]:
                            distance += train.mileage
                        elif train.target_junction == current_section.connected_junctions[SectionConnection.B]:
                            distance += current_section.length - train.mileage
                        else:
                            raise
                    else:
                        distance += current_section.length
                    (
                        current_section,
                        target_junction,
                    ) = self._get_next_section_and_junction(current_section, target_junction)

            if distance < 0:
                distance = 0

            # [ATP]停止位置までの距離を使って、列車の許容速度`speedlimit`を計算する

            speedlimit = math.sqrt(2 * BREAK_ACCLT * distance)
            if speedlimit > MAX_SPEED:
                speedlimit = MAX_SPEED

            # [ATO]駅の停止目標までの距離と、ATP停止位置までの距離を比較して、より近い
            # 停止位置までの距離`stop_distance`を計算

            if train.stop:
                stop_distance = min(train.stop_distance, distance)
            else:
                stop_distance = distance
            if stop_distance < 0:
                stop_distance = 0

            # [ATO]運転速度を、許容速度の範囲内で計算する。
            # まず、停止位置でちゃんと止まれる速度`stop_speed`を計算。

            stop_speed = min(math.sqrt(2 * NORMAL_ACCLT * stop_distance), speedlimit)

            # [ATO]急加速しないよう緩やかに速度を増やす

            speed_command = train.command_speed
            loop_time = 0.1  # NOTE: 1回の制御ループが何秒で回るか？をあとで入れたい
            if stop_speed > speed_command + NORMAL_ACCLT * loop_time:
                speed_command = speed_command + NORMAL_ACCLT * loop_time
            else:
                speed_command = stop_speed

            train.command_speed = speed_command

            print(
                train.id,
                ", ATP StopDistance: ",
                distance,
                ", ATO StopDistance: ",
                stop_distance,
                ", speed: ",
                speed_command,
            )

    def _get_new_position(
        self,
        section: Section,
        mileage: float,
        target_junction: Junction,
        delta: float,
    ) -> tuple[Section, float, Junction]:
        """
        指定された section と mileage から、target_junction 方向に delta 進んだ場所の
        section と mileage と target_junction を取得する
        """

        if target_junction == section.connected_junctions[SectionConnection.B]:
            mileage += delta
        elif target_junction == section.connected_junctions[SectionConnection.A]:
            mileage -= delta
        else:
            raise

        while mileage > section.length or mileage < 0:
            if mileage > section.length:
                surplus_mileage = mileage - section.length
            elif mileage < 0:
                surplus_mileage = -mileage
            else:
                raise

            next_section, next_target_junction = self._get_next_section_and_junction(section, target_junction)

            section = next_section
            target_junction = next_target_junction
            if target_junction == section.connected_junctions[SectionConnection.B]:
                mileage = surplus_mileage
            elif target_junction == section.connected_junctions[SectionConnection.A]:
                mileage = section.length - surplus_mileage
            else:
                raise

        return (section, mileage, target_junction)

    def _get_forward_train(self, train: Train) -> tuple[Train, float] | None:
        """
        指定された列車の先行列車とその最後尾までの距離を取得する。
        一周して指定された列車自身にたどりついた場合は、指定された列車自身を先行列車とみなす。
        ジャンクションの開通方向によっては先行列車に到達できない場合があり、そのときはNoneを返す。
        """

        TRAIN_LENGTH: float = 60  # 列車の長さ[cm] NOTE:将来的には車両のパラメータとして定義

        section = train.current_section

        forward_train: Train | None = None
        forward_train_distance: float = 99999999  # ありえない大きな値

        # 指定された列車と同一セクションに存在する、指定された列車とは異なる列車で、
        # 指定された列車の前方にいる列車のうち、最も近いもの`forward_train`を取得

        for other_train in self.trains.values():
            if other_train.current_section == train.current_section:
                if other_train != train:
                    if (
                        # 端点A(target_junction)<---|other_train|--train---<端点B
                        train.target_junction == section.connected_junctions[SectionConnection.A]
                        and train.mileage <= train.mileage
                    ) or (
                        # 端点A>---train--|other_train|--->端点B(target_junction)
                        train.target_junction == section.connected_junctions[SectionConnection.B]
                        and train.mileage <= other_train.mileage
                    ):
                        distance = abs(train.mileage - other_train.mileage)
                        if distance < forward_train_distance:
                            forward_train = other_train
                            forward_train_distance = distance

        # 指定された列車と同一セクションに先行列車が存在しなければ次のセクションに移り、
        # 先行列車が見つかるまで繰り返す

        section = train.current_section
        target_junction = train.target_junction

        if train.target_junction == section.connected_junctions[SectionConnection.A]:
            distance = train.mileage
        elif train.target_junction == section.connected_junctions[SectionConnection.B]:
            distance = section.length - train.mileage
        else:
            raise

        while forward_train is None:
            next_section_and_junction = self._get_next_section_and_junction_strict(section, target_junction)

            if next_section_and_junction:
                section, target_junction = next_section_and_junction

                for other_train in self.trains.values():
                    if other_train.current_section == section:
                        # 端点A(target_junction)<---|other_train|-----<端点B
                        if target_junction == section.connected_junctions[SectionConnection.A]:
                            new_distance = distance + section.length - other_train.mileage
                        # 端点A>-----|other_train|--->端点B(target_junction)
                        elif target_junction == section.connected_junctions[SectionConnection.B]:
                            new_distance = distance + other_train.mileage
                        else:
                            raise

                        if new_distance < forward_train_distance:
                            forward_train = other_train
                            forward_train_distance = new_distance
            else:
                break

            distance += section.length

        # 先行列車を発見できたら、その最後尾までの距離を計算し、返す
        if forward_train:
            return (forward_train, forward_train_distance - TRAIN_LENGTH)
        else:
            return None

    def _get_next_section_and_junction(
        self, current_section: Section, target_junction: Junction
    ) -> tuple[Section, Junction]:
        """
        与えられたセクションと目指すジャンクションから、次のセクションと目指すジャンクションを計算する。
        """

        if target_junction.connected_sections[Joint.THROUGH] == current_section:
            next_section = target_junction.connected_sections[Joint.CONVERGING]
        elif target_junction.connected_sections[Joint.DIVERGING] == current_section:
            next_section = target_junction.connected_sections[Joint.CONVERGING]
        elif target_junction.connected_sections[Joint.CONVERGING] == current_section:
            if target_junction.current_direction == Direction.STRAIGHT:
                next_section = target_junction.connected_sections[Joint.THROUGH]
            elif target_junction.current_direction == Direction.CURVE:
                next_section = target_junction.connected_sections[Joint.DIVERGING]
            else:
                raise
        else:
            raise

        next_target_junction = next_section.get_opposite_junction(target_junction)
        return next_section, next_target_junction

    def _get_next_section_and_junction_strict(
        self, current_section: Section, target_junction: Junction
    ) -> tuple[Section, Junction] | None:
        """
        与えられたセクションと目指すジャンクションから、次のセクションと目指すジャンクションを計算する。
        ジャンクションが開通しておらず先に進めない場合は、Noneを返す。
        """

        if target_junction.connected_sections[Joint.THROUGH] == current_section:
            if target_junction.current_direction == Direction.STRAIGHT:
                next_section = target_junction.connected_sections[Joint.CONVERGING]
            elif target_junction.current_direction == Direction.CURVE:
                return None
            else:
                raise
        elif target_junction.connected_sections[Joint.DIVERGING] == current_section:
            if target_junction.current_direction == Direction.STRAIGHT:
                return None
            elif target_junction.current_direction == Direction.CURVE:
                next_section = target_junction.connected_sections[Joint.CONVERGING]
            else:
                raise
        elif target_junction.connected_sections[Joint.CONVERGING] == current_section:
            if target_junction.current_direction == Direction.STRAIGHT:
                next_section = target_junction.connected_sections[Joint.THROUGH]
            elif target_junction.current_direction == Direction.CURVE:
                next_section = target_junction.connected_sections[Joint.DIVERGING]
            else:
                raise
        else:
            raise

        next_target_junction = next_section.get_opposite_junction(target_junction)
        return next_section, next_target_junction

    def _calc_stop(self) -> None:
        """
        列車の現在あるべき停止目標を割り出し、列車の状態として格納する。
        この情報は列車の速度を計算するのに使われる。

        実際の挙動は「列車より手前にある停止目標を計算し、ちょっと待ってから格納する」であり、
        これは以下の仮定をおいた上でうまく動作する。
          - 列車は停止目標付近で停止する（= IPS 信号がしばらく送られなくなる）。
          - 停止したときに停止目標の位置を過ぎている。
        """

        STOPPAGE_TIME: int = 50  # 列車の停止時間[フレーム] NOTE: 将来的にはパラメータとして定義

        for train in self.trains.values():
            # 列車より手前にある停止目標を取得する
            forward_stop_and_distance = self._get_forward_stop(train)
            forward_stop, forward_stop_distance = forward_stop_and_distance if forward_stop_and_distance else (None, 0)

            # 停止目標がないままのとき（None → None）
            # 停止目標を見つけたとき（None → not None）
            if train.stop is None:
                train.stop = forward_stop
                if forward_stop:
                    train.stop_distance = forward_stop_distance
                else:
                    train.stop_distance = 0

            # 停止目標を過ぎたとき（異なる）
            # 停止目標を見失ったとき（not None → None）
            # NOTE: セクションがblockされると停止目標を見失う場合がある。
            # このときは駅に着いたと勘違いして止まってしまう現象が起きるが、
            # 駅到着により見失う場合との区別が難しいので、無視する。
            elif train.stop != forward_stop:
                # 最初は発車時刻を設定
                if train.departure_time is None:
                    train.departure_time = self.current_time + STOPPAGE_TIME
                    train.stop_distance = 0

                # 発車時刻になっていれば、次の停止目標に切り替える
                elif self.current_time >= train.departure_time:
                    train.departure_time = None
                    train.stop = forward_stop
                    train.stop_distance = forward_stop_distance

            # 停止目標が変わらないとき
            else:
                train.stop_distance = forward_stop_distance

    def _get_forward_stop(self, train: Train) -> tuple[Stop, float] | None:
        """
        指定された列車が次にたどり着く停止位置とそこまでの距離を取得する。
        停止位置に到達できない場合は None を返す。
        NOTE: `_get_forward_train` とほぼ同じアルゴリズム
        """

        section = train.current_section

        forward_stop: Stop | None = None
        forward_stop_distance: float = 99999999  # ありえない大きな値

        # 指定された列車と同一セクションに存在する、
        # 指定された列車の前方にある停止位置のうち、最も近いもの`forward_stop`を取得

        for stop in self.stops.values():
            if stop.section == train.current_section and stop.target_junction == train.target_junction:
                if (
                    # 端点A(target_junction)<---|stop|--train---<端点B
                    train.target_junction == section.connected_junctions[SectionConnection.A]
                    and stop.mileage <= train.mileage
                ) or (
                    # 端点A>---train--|stop|--->端点B(target_junction)
                    train.target_junction == section.connected_junctions[SectionConnection.B]
                    and train.mileage <= stop.mileage
                ):
                    distance = abs(train.mileage - stop.mileage)
                    if distance < forward_stop_distance:
                        forward_stop = stop
                        forward_stop_distance = distance

        # 指定された列車と同一セクションに停止位置が存在しなければ次のセクションに移り、
        # 停止位置が見つかるまで繰り返す

        section = train.current_section
        target_junction = train.target_junction

        if train.target_junction == section.connected_junctions[SectionConnection.A]:
            distance = train.mileage
        elif train.target_junction == section.connected_junctions[SectionConnection.B]:
            distance = section.length - train.mileage
        else:
            raise

        # 無限ループ検出用
        visited: set[tuple[Section, Junction]] = set()

        while forward_stop is None:
            next_section_and_junction = self._get_next_section_and_junction_strict(section, target_junction)

            if next_section_and_junction:
                # 無限ループを検出したら None を返す
                if next_section_and_junction in visited:
                    return None

                visited.add(next_section_and_junction)

                section, target_junction = next_section_and_junction

                for stop in self.stops.values():
                    if stop.section == section and stop.target_junction == target_junction:
                        # 端点A(target_junction)<---|stop|-----<端点B
                        if target_junction == section.connected_junctions[SectionConnection.A]:
                            new_distance = distance + section.length - stop.mileage
                        # 端点A>-----|stop|--->端点B(target_junction)
                        elif target_junction == section.connected_junctions[SectionConnection.B]:
                            new_distance = distance + stop.mileage
                        else:
                            raise

                        if new_distance < forward_stop_distance:
                            forward_stop = stop
                            forward_stop_distance = new_distance
            else:
                break

            distance += section.length

        # 停止目標を発見できたら、そこまでの距離とともに返す
        if forward_stop:
            return (forward_stop, forward_stop_distance)
        else:
            return None
