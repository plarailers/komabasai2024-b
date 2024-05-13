import math

from ..components.junction import JunctionConnection, PointDirection
from ..components.obstacle import Obstacle
from ..components.position import DirectedPosition, UndirectedPosition
from ..components.section import SectionConnection
from ..components.train import Train
from ..constants import STRAIGHT_RAIL
from .base import BaseControl


class MovingBlockControl(BaseControl):
    """
    移動閉塞システムの全体を管理する。
    """

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
                    else:
                        # TODO: 会場で書いたコードなので後でちゃんと書く。
                        if junction.id == "j3" and nearest_train.head_position.target_junction.id == "j2":
                            junction.manual_direction = PointDirection.CURVE
                            print(nearest_train.id, junction.id)

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
        MERGIN: float = 25  # 停止余裕距離[cm]

        objects: list[tuple[Train, DirectedPosition] | tuple[Obstacle, UndirectedPosition]] = [
            *((train, train.head_position) for train in self.trains.values()),
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

            # [マスコン]
            # 自動操縦ならATPとATO、
            # 手動操縦なら手動速度とATPのみに従う
            if train.manual_speed is None:
                train.speed_command = speed_command
            else:
                train.speed_command = min(train.manual_speed, speedlimit)

            # print(
            #     train.id,
            #     ", ATP StopDistance: ",
            #     distance,
            #     ", ATO StopDistance: ",
            #     stop_distance,
            #     ", speed: ",
            #     speed_command,
            # )

    def _calc_stop(self) -> None:
        """
        列車の現在あるべき停止目標を割り出し、列車の状態として格納する。
        この情報は列車の速度を計算するのに使われる。
        """

        STOPPAGE_TIME: int = 50  # 列車の停止時間[フレーム] NOTE: 将来的にはパラメータとして定義
        STOPPAGE_MERGIN: float = STRAIGHT_RAIL / 2  # 停止区間距離[cm]

        for train in self.trains.values():
            # 列車より手前にある停止目標を取得する
            forward_stop, forward_stop_distance = train.find_forward_stop() or (None, 0.0)

            if train.departure_time is None:
                # 「停止目標が変わらず、停止距離が区間外から区間内に変わる」のを検知することで駅の停止開始を判定する。
                # これにより、以下の場合は停止する。
                # - IPS により停止区間に踏み進んだ場合
                #   - 停止目標は変わらず、停止距離が区間外から区間内に変わるのを検知する
                #   - その後、同区間内の APS を踏んでも以下のどちらかになる
                #     - 区間内で APS を踏む。このとき停止距離が区間内のままであるため無視
                #     - APS により停止区間に踏み戻る。このとき無視
                # - APS により停止区間に踏み進んだ場合
                #   - 停止目標は変わらず、停止距離が区間外から区間内に変わるのを検知する
                # 逆に、以下の場合は停止しない。
                # - APS により停止区間に踏み戻った場合
                #   - 停止目標が変わるので無視
                #   - ただし、停止目標が次も同じになる (例: ループの中で駅がひとつしかない) ような路線ではないとする
                # - ポイントが切り替わって停止目標が再計算された場合
                #   - 停止目標が変わるような箇所はすべて区間外であるため無視
                if train.stop == forward_stop and forward_stop_distance <= STOPPAGE_MERGIN < train.stop_distance:
                    train.stop_distance = forward_stop_distance
                    train.departure_time = self.current_time + STOPPAGE_TIME
                else:
                    train.stop = forward_stop
                    train.stop_distance = forward_stop_distance
            else:
                # すでに停止が開始されているとき、
                # - まだ停止していてほしい場合
                #   - 停止点を超えていない場合、距離を詰めていく
                #   - 停止点を超えてしまった場合、強制停止
                # - もう発車してほしい場合
                #   - 停止点は超えていると仮定し、次の停止目標へ向かう
                if self.current_time < train.departure_time:
                    if train.stop == forward_stop:
                        train.stop_distance = forward_stop_distance
                    else:
                        train.stop_distance = 0
                else:
                    train.stop = forward_stop
                    train.stop_distance = forward_stop_distance
                    train.departure_time = None
