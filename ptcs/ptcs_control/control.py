from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

from .components.junction import Junction, JunctionConnection, PointDirection
from .components.obstacle import Obstacle
from .components.position import DirectedPosition, UndirectedPosition
from .components.section import Section, SectionConnection
from .components.sensor_position import SensorPosition
from .components.station import Station
from .components.stop import Stop
from .components.train import Train


def create_empty_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    return logger


@dataclass
class Control:
    """
    列車制御システムの全体を管理する。
    """

    _current_time: int = field(default=0)  # 現在時刻

    junctions: dict[str, Junction] = field(default_factory=dict)
    sections: dict[str, Section] = field(default_factory=dict)
    trains: dict[str, Train] = field(default_factory=dict)
    stops: dict[str, Stop] = field(default_factory=dict)
    stations: dict[str, Station] = field(default_factory=dict)
    sensor_positions: dict[str, SensorPosition] = field(default_factory=dict)
    obstacles: dict[str, Obstacle] = field(default_factory=dict)

    logger: logging.Logger = field(default_factory=create_empty_logger)

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
        junction_connection: JunctionConnection,
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

    def add_obstacle(self, obstacle: Obstacle) -> None:
        assert obstacle.id not in self.obstacles
        self.obstacles[obstacle.id] = obstacle
        obstacle._control = self

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
        for obstacle in self.obstacles.values():
            obstacle.verify()

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

        # 合流点に向かっている列車が1つ以上ある場合、
        # 最も近い列車のいるほうにポイントを切り替える。
        #
        # 分岐点は決め打ちで、
        # obstacle_0 が出ていないときは、t0-t3 を内側、t4 を外側に運ぶ。
        # obstacle_0 が出ているときは、すべて外側に運ぶ。
        for junction in self.junctions.values():
            nearest_train = junction.find_nearest_train()

            if not nearest_train:
                continue

            match junction.id:
                case "j1" | "j3":
                    if junction.connected_sections[JunctionConnection.THROUGH] == nearest_train.head_position.section:
                        junction.manual_direction = PointDirection.STRAIGHT
                    elif (
                        junction.connected_sections[JunctionConnection.DIVERGING] == nearest_train.head_position.section
                    ):
                        junction.manual_direction = PointDirection.CURVE

                case "j0":
                    if not self.obstacles["obstacle_0"].is_detected:
                        match nearest_train.id:
                            case "t0" | "t1" | "t2" | "t3":
                                junction.manual_direction = PointDirection.CURVE
                            case "t4":
                                junction.manual_direction = PointDirection.STRAIGHT
                    else:
                        junction.manual_direction = PointDirection.STRAIGHT

                case "j2":
                    if not self.obstacles["obstacle_0"].is_detected:
                        match nearest_train.id:
                            case "t0" | "t1" | "t2" | "t3":
                                junction.manual_direction = PointDirection.STRAIGHT
                            case "t4":
                                junction.manual_direction = PointDirection.CURVE
                    else:
                        junction.manual_direction = PointDirection.CURVE

        # 障害物が発生した区間の手前の区間に列車がいるとき、
        # 障害が発生した区間に列車が入らないように
        # ポイントを切り替える。
        for obstacle in self.obstacles.values():
            if not obstacle.is_detected:
                continue

            for train in self.trains.values():
                next_section_and_target_junction = (
                    train.head_position.section.get_next_section_and_target_junction_strict(
                        train.head_position.target_junction
                    )
                )
                if next_section_and_target_junction:
                    next_section, next_target_junction = next_section_and_target_junction
                    if obstacle.position.section == next_section:
                        target_junction = train.head_position.target_junction
                        if target_junction.connected_sections[JunctionConnection.THROUGH] == next_section:
                            target_junction.manual_direction = PointDirection.CURVE
                        elif target_junction.connected_sections[JunctionConnection.DIVERGING] == next_section:
                            target_junction.manual_direction = PointDirection.STRAIGHT

        for junction in self.junctions.values():
            if junction.manual_direction:
                if not junction.is_toggle_prohibited():
                    junction.set_direction(junction.manual_direction)
                    junction.manual_direction = None

    def _calc_speed(self) -> None:
        BREAK_ACCLT: float = 10  # ブレーキ減速度[cm/s/s]  NOTE:将来的には車両のパラメータとして定義
        NORMAL_ACCLT: float = 5  # 常用加減速度[cm/s/s]  NOTE:将来的には車両のパラメータとして定義
        MAX_SPEED: float = 40  # 最高速度[cm/s]  NOTE:将来的には車両のパラメータとしてとして定義
        MERGIN: float = 10  # 停止余裕距離[cm]

        objects: list[tuple[Train, DirectedPosition] | tuple[Obstacle, UndirectedPosition]] = [
            *((train, train.compute_tail_position()) for train in self.trains.values()),
            *((obstacle, obstacle.position) for obstacle in self.obstacles.values() if obstacle.is_detected),
        ]

        for train in self.trains.values():
            # [ATP]停止位置までの距離`distance`を、先行列車の位置と、ジャンクションの状態をもとに計算する

            distance = 0.0

            current_section = train.head_position.section
            target_junction = train.head_position.target_junction

            forward_object_and_distance = train.find_forward_object(objects)
            if forward_object_and_distance:
                distance += forward_object_and_distance[1] - MERGIN
            else:
                while True:
                    next_section, next_junction = current_section.get_next_section_and_target_junction(target_junction)

                    # いま見ているセクションが閉鎖 -> 即時停止
                    # ただしすでに列車が閉鎖セクションに入ってしまった場合は、駅まで動かしたいので、止めない
                    if current_section != train.head_position.section and current_section.is_blocked is True:
                        distance += 0
                        break

                    # 先行列車に到達できる -> 先行列車の手前で停止
                    elif forward_train_and_distance := train.find_forward_train():
                        distance += forward_train_and_distance[1] - MERGIN
                        break

                    # 目指すジャンクションが自列車側に開通していない or 次のセクションが閉鎖
                    # -> 目指すジャンクションの手前で停止
                    elif (
                        current_section.get_next_section_and_target_junction_strict(target_junction) is None
                        or next_section.is_blocked is True
                    ):
                        if current_section == train.head_position.section:
                            if target_junction == current_section.connected_junctions[SectionConnection.A]:
                                distance += train.head_position.mileage - MERGIN
                            elif target_junction == current_section.connected_junctions[SectionConnection.B]:
                                distance += current_section.length - train.head_position.mileage - MERGIN
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
                        if current_section == train.head_position.section:
                            if (
                                train.head_position.target_junction
                                == current_section.connected_junctions[SectionConnection.A]
                            ):
                                distance += train.head_position.mileage
                            elif (
                                train.head_position.target_junction
                                == current_section.connected_junctions[SectionConnection.B]
                            ):
                                distance += current_section.length - train.head_position.mileage
                            else:
                                raise
                        else:
                            distance += current_section.length
                        (
                            current_section,
                            target_junction,
                        ) = current_section.get_next_section_and_target_junction(target_junction)

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

            speed_command = train.speed_command
            loop_time = 0.1  # NOTE: 1回の制御ループが何秒で回るか？をあとで入れたい
            if stop_speed > speed_command + NORMAL_ACCLT * loop_time:
                speed_command = speed_command + NORMAL_ACCLT * loop_time
            else:
                speed_command = stop_speed

            train.speed_command = speed_command

            print(
                train.id,
                ", ATP StopDistance: ",
                distance,
                ", ATO StopDistance: ",
                stop_distance,
                ", speed: ",
                speed_command,
            )

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
            forward_stop, forward_stop_distance = train.find_forward_stop() or (None, 0)

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
