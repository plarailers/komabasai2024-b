from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import BaseComponent
from .section import SectionConnection

if TYPE_CHECKING:
    from .junction import Junction
    from .position import DirectedPosition
    from .section import Section
    from .sensor_position import SensorPosition
    from .stop import Stop


@dataclass
class Train(BaseComponent):
    """列車"""

    id: str

    # config
    min_input: int
    max_input: int
    max_speed: float
    length: float  # 列車の長さ[cm]
    delta_per_motor_rotation: float  # モータ1回転で進む距離[cm]

    # state
    head_position: DirectedPosition  # 列車先頭の位置と方向
    stop: Stop | None = field(default=None)  # 列車の停止目標
    stop_distance: float = field(default=0.0)  # 停止目標までの距離[cm]
    departure_time: int | None = field(default=None)  # 発車予定時刻

    # commands
    speed_command: float = field(default=0.0)  # 速度指令値

    def verify(self) -> None:
        super().verify()
        assert (
            self.head_position.target_junction in self.head_position.section.connected_junctions.values()
        ), f"{self}.position.target_junction is wrong"
        assert 0 <= self.head_position.mileage <= self.head_position.section.length, f"{self}.position.length is wrong"

    def calc_input(self, speed: float) -> int:
        if speed > self.max_speed:
            return self.max_input
        elif speed <= 0:
            return 0
        else:
            return math.floor(self.min_input + (self.max_input - self.min_input) * speed / self.max_speed)

    def move_forward_mr(self, motor_rotation: int) -> None:
        """
        列車をモータ motor_rotation 回転分だけ進める。
        """

        self.move_forward(motor_rotation * self.delta_per_motor_rotation)

    def move_forward(self, delta: float) -> None:
        """
        列車を距離 delta 分だけ進める。
        """

        self.head_position = self.head_position.get_advanced_position(delta)

    def fix_position(self, sensor: SensorPosition) -> None:
        """
        列車の位置を修正する。
        TODO: 向きを割り出すためにどうするか
        """

        self.head_position = DirectedPosition(sensor.section, sensor.target_junction, sensor.mileage)

    def send_speed_command(self, speed_command: float) -> None:
        """
        指定された列車の速度を指示する。
        """

        self.speed_command = speed_command

    def find_forward_train(self) -> tuple[Train, float] | None:
        """
        指定された列車の先行列車とその最後尾までの距離を取得する。
        一周して指定された列車自身にたどりついた場合は、指定された列車自身を先行列車とみなす。
        ジャンクションの開通方向によっては先行列車に到達できない場合があり、そのときはNoneを返す。
        """

        section = self.head_position.section

        forward_train: Train | None = None
        forward_train_distance: float = 99999999  # ありえない大きな値

        # 指定された列車と同一セクションに存在する、指定された列車とは異なる列車で、
        # 指定された列車の前方にいる列車のうち、最も近いもの`forward_train`を取得

        for other_train in self.control.trains.values():
            if other_train.head_position.section == self.head_position.section:
                if other_train != self:
                    if (
                        # 端点A(target_junction)<---|other_train|--train---<端点B
                        self.head_position.target_junction == section.connected_junctions[SectionConnection.A]
                        and self.head_position.mileage <= self.head_position.mileage
                    ) or (
                        # 端点A>---train--|other_train|--->端点B(target_junction)
                        self.head_position.target_junction == section.connected_junctions[SectionConnection.B]
                        and self.head_position.mileage <= other_train.head_position.mileage
                    ):
                        distance = abs(self.head_position.mileage - other_train.head_position.mileage)
                        if distance < forward_train_distance:
                            forward_train = other_train
                            forward_train_distance = distance

        # 指定された列車と同一セクションに先行列車が存在しなければ次のセクションに移り、
        # 先行列車が見つかるまで繰り返す

        section = self.head_position.section
        target_junction = self.head_position.target_junction

        if self.head_position.target_junction == section.connected_junctions[SectionConnection.A]:
            distance = self.head_position.mileage
        elif self.head_position.target_junction == section.connected_junctions[SectionConnection.B]:
            distance = section.length - self.head_position.mileage
        else:
            raise

        while forward_train is None:
            next_section_and_junction = section.get_next_section_and_target_junction_strict(target_junction)

            if next_section_and_junction:
                section, target_junction = next_section_and_junction

                for other_train in self.control.trains.values():
                    if other_train.head_position.section == section:
                        # 端点A(target_junction)<---|other_train|-----<端点B
                        if target_junction == section.connected_junctions[SectionConnection.A]:
                            new_distance = distance + section.length - other_train.head_position.mileage
                        # 端点A>-----|other_train|--->端点B(target_junction)
                        elif target_junction == section.connected_junctions[SectionConnection.B]:
                            new_distance = distance + other_train.head_position.mileage
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
            return forward_train, forward_train_distance - forward_train.length
        else:
            return None

    def find_forward_stop(self) -> tuple[Stop, float] | None:
        """
        指定された列車が次にたどり着く停止位置とそこまでの距離を取得する。
        停止位置に到達できない場合は None を返す。
        NOTE: `find_forward_train` とほぼ同じアルゴリズム
        """

        section = self.head_position.section

        forward_stop: Stop | None = None
        forward_stop_distance: float = 99999999  # ありえない大きな値

        # 指定された列車と同一セクションに存在する、
        # 指定された列車の前方にある停止位置のうち、最も近いもの`forward_stop`を取得

        for stop in self.control.stops.values():
            if (
                stop.position.section == self.head_position.section
                and stop.position.target_junction == self.head_position.target_junction
            ):
                if (
                    # 端点A(target_junction)<---|stop|--train---<端点B
                    self.head_position.target_junction == section.connected_junctions[SectionConnection.A]
                    and stop.position.mileage <= self.head_position.mileage
                ) or (
                    # 端点A>---train--|stop|--->端点B(target_junction)
                    self.head_position.target_junction == section.connected_junctions[SectionConnection.B]
                    and self.head_position.mileage <= stop.position.mileage
                ):
                    distance = abs(self.head_position.mileage - stop.position.mileage)
                    if distance < forward_stop_distance:
                        forward_stop = stop
                        forward_stop_distance = distance

        # 指定された列車と同一セクションに停止位置が存在しなければ次のセクションに移り、
        # 停止位置が見つかるまで繰り返す

        section = self.head_position.section
        target_junction = self.head_position.target_junction

        if self.head_position.target_junction == section.connected_junctions[SectionConnection.A]:
            distance = self.head_position.mileage
        elif self.head_position.target_junction == section.connected_junctions[SectionConnection.B]:
            distance = section.length - self.head_position.mileage
        else:
            raise

        # 無限ループ検出用
        visited: set[tuple[Section, Junction]] = set()

        while forward_stop is None:
            next_section_and_junction = section.get_next_section_and_target_junction_strict(target_junction)

            if next_section_and_junction:
                # 無限ループを検出したら None を返す
                if next_section_and_junction in visited:
                    return None

                visited.add(next_section_and_junction)

                section, target_junction = next_section_and_junction

                for stop in self.control.stops.values():
                    if stop.position.section == section and stop.position.target_junction == target_junction:
                        # 端点A(target_junction)<---|stop|-----<端点B
                        if target_junction == section.connected_junctions[SectionConnection.A]:
                            new_distance = distance + section.length - stop.position.mileage
                        # 端点A>-----|stop|--->端点B(target_junction)
                        elif target_junction == section.connected_junctions[SectionConnection.B]:
                            new_distance = distance + stop.position.mileage
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
            return forward_stop, forward_stop_distance
        else:
            return None
