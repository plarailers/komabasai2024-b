import logging

from .components.junction import Junction, JunctionConnection
from .components.position import DirectedPosition
from .components.section import Section, SectionConnection
from .components.sensor_position import SensorPosition
from .components.station import Station
from .components.stop import Stop
from .components.train import Train
from .constants import (
    CURVE_RAIL,
    OUTER_CURVE_RAIL,
    STRAIGHT_1_2_RAIL,
    STRAIGHT_1_4_RAIL,
    STRAIGHT_RAIL,
    WATARI_RAIL_A,
    WATARI_RAIL_B,
    WATARI_RAIL_C,
)
from .control import Control, create_empty_logger


def create_control(logger: logging.Logger | None = None) -> Control:
    if logger is None:
        logger = create_empty_logger()

    control = Control(logger=logger)

    j0 = Junction(id="j0")
    j1 = Junction(id="j1")
    j2 = Junction(id="j2")
    j3 = Junction(id="j3")

    control.add_junction(j0)
    control.add_junction(j1)
    control.add_junction(j2)
    control.add_junction(j3)

    s0 = Section(
        id="s0",
        length=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL + CURVE_RAIL + STRAIGHT_RAIL + WATARI_RAIL_A,
    )
    s1 = Section(
        id="s1",
        length=WATARI_RAIL_B
        + STRAIGHT_RAIL * 4
        + CURVE_RAIL * 3
        + STRAIGHT_RAIL * 4
        + CURVE_RAIL
        + STRAIGHT_RAIL * 2
        + 3.67
        + CURVE_RAIL * 2
        + STRAIGHT_1_2_RAIL
        + WATARI_RAIL_B,
    )
    s2 = Section(
        id="s2",
        length=WATARI_RAIL_B + 4.70 + OUTER_CURVE_RAIL * 2 + WATARI_RAIL_B,
    )
    s3 = Section(
        id="s3",
        length=WATARI_RAIL_A
        + STRAIGHT_RAIL * 2
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL * 2
        + STRAIGHT_1_2_RAIL
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL * 3
        + OUTER_CURVE_RAIL * 2
        + 6.01
        + WATARI_RAIL_A,
    )
    s4 = Section(
        id="s4",
        length=WATARI_RAIL_C + WATARI_RAIL_C,
    )
    s5 = Section(
        id="s5",
        length=WATARI_RAIL_C,
    )

    control.add_section(s0)
    control.add_section(s1)
    control.add_section(s2)
    control.add_section(s3)
    control.add_section(s4)
    control.add_section(s5)

    A, B = SectionConnection.A, SectionConnection.B
    THROUGH, DIVERGING, CONVERGING = (
        JunctionConnection.THROUGH,
        JunctionConnection.DIVERGING,
        JunctionConnection.CONVERGING,
    )
    control.connect(s0, A, j0, THROUGH)
    control.connect(s0, B, j3, THROUGH)
    control.connect(s1, A, j3, CONVERGING)
    control.connect(s1, B, j0, CONVERGING)
    control.connect(s2, A, j1, CONVERGING)
    control.connect(s2, B, j2, CONVERGING)
    control.connect(s3, A, j2, THROUGH)
    control.connect(s3, B, j1, THROUGH)
    control.connect(s4, A, j0, DIVERGING)
    control.connect(s4, B, j1, DIVERGING)
    control.connect(s5, A, j2, DIVERGING)
    control.connect(s5, B, j3, DIVERGING)

    t0 = Train(
        id="t0",
        min_input=70,
        max_input=130,
        max_speed=40.0,
        delta_per_motor_rotation=0.2435 * 0.9,
        position=DirectedPosition(
            section=s0,
            target_junction=j3,
            mileage=STRAIGHT_RAIL * 4.5 + WATARI_RAIL_B + 1,  # 次駅探索の都合上、stopを1cm通り過ぎた場所にしておく
        ),
    )  # Dr
    t1 = Train(
        id="t1",
        min_input=90,
        max_input=130,
        max_speed=40.0,
        delta_per_motor_rotation=0.1919 * 1.1 * 0.9,
        position=DirectedPosition(
            section=s1,
            target_junction=j0,
            mileage=STRAIGHT_RAIL * 2.5 + WATARI_RAIL_B + 1,
        ),
    )  # E6
    # E5はAPS故障につきまだ運用しない

    control.add_train(t0)
    control.add_train(t1)

    stop_0 = Stop(
        id="stop_0",
        position=DirectedPosition(
            section=s0,
            target_junction=j1,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 4.5,
        ),
    )
    stop_1 = Stop(
        id="stop_1",
        position=DirectedPosition(
            section=s0,
            target_junction=j1,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 10.0 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
        ),
    )
    stop_2 = Stop(
        id="stop_2",
        position=DirectedPosition(
            section=s1,
            target_junction=j1,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 1.5,
        ),
    )
    stop_3 = Stop(
        id="stop_3",
        position=DirectedPosition(
            section=s1,
            target_junction=j3,
            mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 1.5,
        ),
    )
    stop_4 = Stop(
        id="stop_4",
        position=DirectedPosition(
            section=s3,
            target_junction=j0,
            mileage=WATARI_RAIL_A * 1 + STRAIGHT_RAIL * 1.5,
        ),
    )

    # control.add_stop(stop_0)
    # control.add_stop(stop_1)
    # control.add_stop(stop_2)
    # control.add_stop(stop_3)
    # control.add_stop(stop_4)

    station_0 = Station(id="station_0", stops=[stop_0, stop_1])
    station_1 = Station(id="station_1", stops=[stop_2, stop_3, stop_4])

    # control.add_station(station_0)
    # control.add_station(station_1)

    position_173 = SensorPosition(
        id="position_173",
        section=s0,
        target_junction=j1,
        mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 2.5,
    )
    position_138 = SensorPosition(
        id="position_138",
        section=s0,
        target_junction=j1,
        mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 9.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
    )
    position_80 = SensorPosition(
        id="position_80",
        section=s0,
        target_junction=j1,
        mileage=WATARI_RAIL_B * 1 + STRAIGHT_RAIL * 13.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
    )
    position_255 = SensorPosition(
        id="position_255",
        section=s2,
        target_junction=j2,
        mileage=WATARI_RAIL_A * 1 + STRAIGHT_RAIL * 5.5 + CURVE_RAIL * 8 + STRAIGHT_1_4_RAIL * 1,
    )

    # control.add_sensor_position(position_173)
    # control.add_sensor_position(position_138)
    # control.add_sensor_position(position_80)
    # control.add_sensor_position(position_255)

    control.verify()
    return control
