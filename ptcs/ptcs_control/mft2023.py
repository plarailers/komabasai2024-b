import logging

from .components.junction import Junction, JunctionConnection
from .components.obstacle import Obstacle
from .components.position import DirectedPosition, UndirectedPosition
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
    STRAIGHT_1_6_RAIL,
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
        length=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL + CURVE_RAIL * 2 + STRAIGHT_RAIL + WATARI_RAIL_A,
    )
    s1 = Section(
        id="s1",
        length=WATARI_RAIL_B
        + STRAIGHT_RAIL * 3
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
        + STRAIGHT_RAIL
        + STRAIGHT_1_2_RAIL
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL * 3
        + OUTER_CURVE_RAIL * 2
        + 6.01
        + WATARI_RAIL_A,
    )
    s4 = Section(
        id="s4",
        length=WATARI_RAIL_C + 4.05 + WATARI_RAIL_C,
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
        min_input=200,
        max_input=250,
        max_speed=40.0,
        length=14.0,
        delta_per_motor_rotation=0.4553 * 0.9 * 0.9,
        head_position=DirectedPosition(
            section=s3,
            target_junction=j1,
            mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 0.5,
        ),
    )
    t1 = Train(
        id="t1",
        min_input=150,
        max_input=210,
        max_speed=40.0,
        length=14.0,
        delta_per_motor_rotation=0.4021,
        head_position=DirectedPosition(
            section=s3,
            target_junction=j1,
            mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2 + OUTER_CURVE_RAIL * 2 + STRAIGHT_RAIL,
        ),
    )
    t2 = Train(
        id="t2",
        min_input=150,
        max_input=230,
        max_speed=40.0,
        length=14.0,
        delta_per_motor_rotation=0.5048,
        head_position=DirectedPosition(
            section=s3,
            target_junction=j1,
            mileage=WATARI_RAIL_A
            + STRAIGHT_RAIL * 2
            + OUTER_CURVE_RAIL * 2
            + STRAIGHT_RAIL
            + STRAIGHT_1_2_RAIL
            + OUTER_CURVE_RAIL * 2
            + STRAIGHT_RAIL,
        ),
    )
    t3 = Train(
        id="t3",
        min_input=190,
        max_input=220,
        max_speed=40.0,
        length=14.0,
        delta_per_motor_rotation=0.4208,
        head_position=DirectedPosition(
            section=s3,
            target_junction=j1,
            mileage=WATARI_RAIL_A
            + STRAIGHT_RAIL * 2
            + OUTER_CURVE_RAIL * 2
            + STRAIGHT_RAIL
            + STRAIGHT_1_2_RAIL
            + OUTER_CURVE_RAIL * 2
            + STRAIGHT_RAIL * 3
            + OUTER_CURVE_RAIL * 2,
        ),
    )
    t4 = Train(
        id="t4",
        min_input=180,
        max_input=230,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241 * 2.2,
        head_position=DirectedPosition(
            section=s1,
            target_junction=j0,
            mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 4,
        ),
    )

    # control.add_train(t0)
    control.add_train(t1)
    control.add_train(t2)
    control.add_train(t3)
    # control.add_train(t4)

    stop_0 = Stop(
        id="stop_0",
        position=DirectedPosition(
            section=s3,
            target_junction=j1,
            mileage=WATARI_RAIL_A + STRAIGHT_RAIL - STRAIGHT_1_6_RAIL,
        ),
    )
    stop_1 = Stop(
        id="stop_1",
        position=DirectedPosition(
            section=s3,
            target_junction=j1,
            mileage=WATARI_RAIL_A
            + STRAIGHT_RAIL * 2
            + OUTER_CURVE_RAIL * 2
            + STRAIGHT_RAIL
            + STRAIGHT_1_2_RAIL
            + OUTER_CURVE_RAIL * 2
            + STRAIGHT_RAIL * 2
            - STRAIGHT_1_6_RAIL,
        ),
    )

    control.add_stop(stop_0)
    control.add_stop(stop_1)

    station_0 = Station(id="station_0", stops=[stop_0])
    station_1 = Station(id="station_1", stops=[stop_1])

    control.add_station(station_0)
    control.add_station(station_1)

    p1 = SensorPosition(
        id="position_0433ca30af6180",
        section=s3,
        target_junction=j1,
        mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 0.5,
    )
    p2 = SensorPosition(
        id="position_047c6731af6180",
        section=s3,
        target_junction=j1,
        mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2 + OUTER_CURVE_RAIL * 0.5,
    )
    p3 = SensorPosition(
        id="position_04117931af6180",
        section=s3,
        target_junction=j1,
        mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2 + OUTER_CURVE_RAIL * 2 + STRAIGHT_1_2_RAIL + STRAIGHT_RAIL * 0.5,
    )
    p4 = SensorPosition(
        id="position_0497d230af6180",
        section=s3,
        target_junction=j1,
        mileage=WATARI_RAIL_A
        + STRAIGHT_RAIL * 2
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL
        + STRAIGHT_1_2_RAIL
        + OUTER_CURVE_RAIL * 1.5,
    )
    p5 = SensorPosition(
        id="position_04d7932baf6180",
        section=s3,
        target_junction=j1,
        mileage=WATARI_RAIL_A
        + STRAIGHT_RAIL * 2
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL
        + STRAIGHT_1_2_RAIL
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL * 1.5,
    )
    p6 = SensorPosition(
        id="position_040e6f2daf6180",
        section=s3,
        target_junction=j1,
        mileage=WATARI_RAIL_A
        + STRAIGHT_RAIL * 2
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL
        + STRAIGHT_1_2_RAIL
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL * 3
        + OUTER_CURVE_RAIL * 0.5,
    )
    p7 = SensorPosition(
        id="position_04059229af6180",
        section=s3,
        target_junction=j1,
        mileage=WATARI_RAIL_A
        + STRAIGHT_RAIL * 2
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL
        + STRAIGHT_1_2_RAIL
        + OUTER_CURVE_RAIL * 2
        + STRAIGHT_RAIL * 3
        + OUTER_CURVE_RAIL * 1.5,
    )
    p8 = SensorPosition(
        id="position_04f1ac2baf6180",
        section=s2,
        target_junction=j2,
        mileage=WATARI_RAIL_B + 4.70 + OUTER_CURVE_RAIL * 0.5,
    )
    p9 = SensorPosition(
        id="position_0451002baf6180",
        section=s2,
        target_junction=j2,
        mileage=WATARI_RAIL_B + 4.70 + OUTER_CURVE_RAIL * 1.5,
    )
    p10 = SensorPosition(
        id="position_040a992aaf6181",
        section=s1,
        target_junction=j0,
        mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 0.5,
    )
    p11 = SensorPosition(
        id="position_0494a12baf6180",
        section=s1,
        target_junction=j0,
        mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 0.5,
    )
    p12 = SensorPosition(
        id="position_04299928af6180",
        section=s1,
        target_junction=j0,
        mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 2.5,
    )
    p13 = SensorPosition(
        id="position_047d8129af6180",
        section=s1,
        target_junction=j0,
        mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 3 + STRAIGHT_RAIL * 3,
    )
    p14 = SensorPosition(
        id="position_042d962baf6180",
        section=s1,
        target_junction=j0,
        mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 3 + STRAIGHT_RAIL * 4 + CURVE_RAIL * 0.5,
    )
    p15 = SensorPosition(
        id="position_0455b128af6180",
        section=s1,
        target_junction=j0,
        mileage=WATARI_RAIL_B
        + STRAIGHT_RAIL * 3
        + CURVE_RAIL * 3
        + STRAIGHT_RAIL * 4
        + CURVE_RAIL
        + STRAIGHT_RAIL * 2
        + 3.67
        + CURVE_RAIL * 0.5,
    )
    p16 = SensorPosition(
        id="position_04369a28af6180",
        section=s1,
        target_junction=j0,
        mileage=WATARI_RAIL_B
        + STRAIGHT_RAIL * 3
        + CURVE_RAIL * 3
        + STRAIGHT_RAIL * 4
        + CURVE_RAIL
        + STRAIGHT_RAIL * 2
        + 3.67
        + CURVE_RAIL * 1.5,
    )
    p17 = SensorPosition(
        id="position_04a96f28af6180",
        section=s0,
        target_junction=j3,
        mileage=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL * 0.5,
    )
    p18 = SensorPosition(
        id="position_044be628af6180",
        section=s0,
        target_junction=j3,
        mileage=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL + CURVE_RAIL * 1.5,
    )
    p19 = SensorPosition(
        id="position_0489e22caf6180",
        section=s0,
        target_junction=j3,
        mileage=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL + CURVE_RAIL * 2 + STRAIGHT_RAIL * 0.5,
    )

    control.add_sensor_position(p1)
    control.add_sensor_position(p2)
    control.add_sensor_position(p3)
    control.add_sensor_position(p4)
    control.add_sensor_position(p5)
    control.add_sensor_position(p6)
    control.add_sensor_position(p7)
    control.add_sensor_position(p8)
    control.add_sensor_position(p9)
    control.add_sensor_position(p10)
    control.add_sensor_position(p11)
    control.add_sensor_position(p12)
    control.add_sensor_position(p13)
    control.add_sensor_position(p14)
    control.add_sensor_position(p15)
    control.add_sensor_position(p16)
    control.add_sensor_position(p17)
    control.add_sensor_position(p18)
    control.add_sensor_position(p19)

    obstacle_0 = Obstacle(
        id="obstacle_0",
        position=UndirectedPosition(
            section=s3,
            mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2,
        ),
        is_detected=False,
    )

    control.add_obstacle(obstacle_0)

    control.verify()
    return control
