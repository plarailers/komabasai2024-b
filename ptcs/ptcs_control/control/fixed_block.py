import math
from collections import deque

from ..components.junction import JunctionConnection, PointDirection
from ..components.obstacle import Obstacle
from ..components.position import DirectedPosition, UndirectedPosition
from ..components.section import (
    Section,
    SectionConnection,
    compute_connected_components,
)
from ..components.train import Train, TrainType
from ..constants import STRAIGHT_RAIL
from .base import BaseControl
from .events import TrainSectionChanged


class FixedBlockControl(BaseControl):
    """
    固定閉塞システムの全体を管理する。
    """

    def update(self) -> None:
        """
        状態に変化が起こった後、すべてを再計算する。
        """

        self._calc_direction()
        self._calc_block()
        self._calc_stop()
        self._calc_speed()
        self.event_queue.clear()

    def _calc_direction(self) -> None:
        """
        ポイントをどちら向きにするかを計算する。
        """

        # 合流点に向かっている列車が1つ以上ある場合、
        # 最も近い列車のいるほうにポイントを切り替える。
        #
        # 分岐点は決め打ちで、
        # 急行線上の分岐点では特急を急行線に、
        # 緩行線上の分岐点では各駅停車を緩行線に保つ。
        for junction in self.junctions.values():
            nearest_train = junction.find_nearest_train()

            if not nearest_train:
                continue

            match junction.id:
                case "j100" | "j102" | "j103" | "j105" | "j106":  # 合流点
                    section_t = junction.connected_sections[JunctionConnection.THROUGH]
                    section_d = junction.connected_sections.get(JunctionConnection.DIVERGING)
                    if (
                        section_t == nearest_train.head_position.section
                        or section_t == nearest_train.head_position.get_advanced_position(1.0).section
                    ):
                        junction.manual_direction = PointDirection.STRAIGHT
                    elif (
                        section_d == nearest_train.head_position.section
                        or section_d == nearest_train.head_position.get_advanced_position(1.0).section
                    ):
                        junction.manual_direction = PointDirection.CURVE
                    else:
                        # 一応同じ閉塞区間の次の区間まで見る
                        current_section = nearest_train.head_position.section
                        current_target_junction = nearest_train.head_position.target_junction
                        while True:
                            if current_section.block_id != nearest_train.head_position.section.block_id:
                                break
                            next_section_and_target_junction = (
                                current_section.get_next_section_and_target_junction_strict(current_target_junction)
                            )
                            if next_section_and_target_junction is None:
                                break
                            next_section, next_target_junction = next_section_and_target_junction
                            if section_t == next_section:
                                junction.manual_direction = PointDirection.STRAIGHT
                                break
                            elif section_d == next_section:
                                junction.manual_direction = PointDirection.CURVE
                                break
                            current_section = next_section
                            current_target_junction = next_target_junction

                case "J30" | "j104":  # 固定
                    junction.manual_direction = PointDirection.CURVE

                case "J50":  # 急行線上の分岐点
                    match nearest_train.type:
                        case TrainType.LimitedExpress:
                            junction.manual_direction = PointDirection.STRAIGHT  # 急行線に保つ
                        case TrainType.Local:
                            junction.manual_direction = PointDirection.CURVE  # 緩行線に保つ
                        case TrainType.CommuterSemiExpress:
                            if junction.id == "J50":
                                junction.manual_direction = PointDirection.CURVE  # 駅に寄るため専用区間に移動
                            else:
                                junction.manual_direction = PointDirection.STRAIGHT  # 極力急行線に移動

                case "J26":  # 緩行線上の分岐点
                    match nearest_train.type:
                        case TrainType.LimitedExpress:
                            junction.manual_direction = PointDirection.CURVE  # 急行線に保つ
                        case TrainType.Local:
                            junction.manual_direction = PointDirection.STRAIGHT  # 緩行線に保つ
                        case TrainType.CommuterSemiExpress:
                            junction.manual_direction = PointDirection.CURVE  # 極力急行線に移動

            # 要求キューに入れる
            if junction.manual_direction is not None:
                if (junction.manual_direction, nearest_train) not in junction.request_queue:
                    junction.request_queue.append((junction.manual_direction, nearest_train))
                junction.manual_direction = None

        for junction in self.junctions.values():
            # 過ぎ去った列車を取り除く
            incoming_trains = junction.find_incoming_trains()
            junction.request_queue = deque((d, t) for (d, t) in junction.request_queue if t in incoming_trains)

        # 列車のセクション変更イベントを拾って通勤準急の行き先を判断する。
        for event in self.event_queue:
            match event:
                case TrainSectionChanged(t0, previous_section, current_section):  # 列車のセクションが変わったとき
                    self.logger.info(f"{t0} {previous_section} -> {current_section}")

                    if t0.type == TrainType.Local:  # 各駅停車のとき
                        # ダブルクロスの手前の閉塞区間に着いたなら、
                        # プラットホームの反対側に迫っている列車を取得
                        t1: Train | None = None
                        match current_section.block_id:
                            case "b00":  # 代々木上原 → 下北沢
                                t1 = self.junctions["c141"].find_nearest_train()
                            case "b12":  # 豪徳寺 → 経堂
                                t1 = self.junctions["c148"].find_nearest_train()
                            case "b30":  # 千歳船橋 ← 成城学園前
                                t1 = self.junctions["c123"].find_nearest_train()
                            case "b41":  # 豪徳寺 ← 経堂
                                t1 = self.junctions["j13"].find_nearest_train()

                        if t1 and t1.type == TrainType.CommuterSemiExpress:
                            # TODO
                            pass

        # ポイントの向きを適用する。
        for junction in self.junctions.values():
            if junction.request_queue:
                direction, _train = junction.request_queue[0]
                if not junction.is_toggle_prohibited():
                    junction.set_direction(direction)

    def _calc_block(self) -> None:
        r"""
        閉塞を計算する。
        基本的にセクションに割り振られている閉塞 ID を元にするが、
        並列する線路を同じ閉塞にするかどうかがポイントの開通状況によって変わるため、
        ポイントの向きの計算後に呼び出す。
        """

        blocks: dict[str, list["Section"]] = {}

        for section in self.sections.values():
            section.is_blocked = False
            if section.block_id is None:
                continue
            if section.block_id not in blocks:
                blocks[section.block_id] = []
            blocks[section.block_id].append(section)

        for train in self.trains.values():
            train.head_position.section.is_blocked = True
            train.compute_tail_position().section.is_blocked = True

        for block in blocks.values():
            connected_components = compute_connected_components(block)
            is_connected: dict[str, set[str]] = {}
            for component in connected_components:
                for section_id in component:
                    is_connected[section_id] = component

            for s in block:
                for t in block:
                    if t.id in is_connected[s.id]:
                        is_blocked = s.is_blocked | t.is_blocked
                        s.is_blocked |= is_blocked
                        t.is_blocked |= is_blocked

    def _calc_stop(self) -> None:
        """
        列車の現在あるべき停止目標を割り出し、列車の状態として格納する。
        この情報は列車の速度を計算するのに使われる。
        """

        STOPPAGE_TIME: int = 30  # 列車の停止時間[フレーム] NOTE: 将来的にはパラメータとして定義
        STOPPAGE_MERGIN: float = STRAIGHT_RAIL / 2  # 停止区間距離[cm]

        # 列車のセクション変更イベントを拾って停止駅を判断する
        for event in self.event_queue:
            match event:
                case TrainSectionChanged(t0, _, current_section):  # 列車のセクションが変わったとき
                    stops: list[str]
                    match t0.type:
                        case TrainType.LimitedExpress:
                            stops = []
                        case TrainType.Local:
                            stops = ["S60", "S25"]
                        case TrainType.CommuterSemiExpress:
                            stops = ["S37", "S25"]
                        case _:
                            stops = []

                    if current_section.id in stops:
                        t0.stop_distance = 0.0
                        t0.departure_time = self.current_time + STOPPAGE_TIME

        return

        for train in self.trains.values():
            # 列車より手前にある停止目標を取得する
            forward_stop, forward_stop_distance = train.find_forward_stop() or (None, 1e9)

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

    def _calc_speed(self) -> None:
        BREAK_ACCLT: float = 10  # ブレーキ減速度[cm/s/s]  NOTE:将来的には車両のパラメータとして定義
        NORMAL_ACCLT: float = 5  # 常用加減速度[cm/s/s]  NOTE:将来的には車両のパラメータとして定義
        MAX_SPEED: float = 40  # 最高速度[cm/s]  NOTE:将来的には車両のパラメータとしてとして定義
        MERGIN: float = 25  # 停止余裕距離[cm]

        for train in self.trains.values():
            current_section = train.head_position.section
            target_junction = train.head_position.target_junction
            while True:
                next_block_section, next_block_junction = current_section.get_next_section_and_target_junction(
                    target_junction
                )
                if next_block_section.block_id != current_section.block_id:
                    break
                current_section = next_block_section
                target_junction = next_block_junction

            if train.departure_time is not None and self.current_time < train.departure_time:
                train.speed_command = 0.0
            elif next_block_section.is_blocked:
                train.speed_command = 0.0
            elif next_block_section.get_next_section_and_target_junction_strict(next_block_junction) is None:
                # 次のセクションがブロックされていなくても、ポイントが自分の方に向いていなければブロックとみなす
                train.speed_command = 0.0
            else:
                train.speed_command = MAX_SPEED

            if train.departure_time is not None and self.current_time >= train.departure_time:
                train.departure_time = None

        return

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
                            distance += train.head_position.mileage - MERGIN
                        elif target_junction == current_section.connected_junctions[SectionConnection.B]:
                            distance += current_section.length - train.head_position.mileage - MERGIN
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
