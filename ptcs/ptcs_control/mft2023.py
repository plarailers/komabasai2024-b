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

    j00 = Junction(id="j00")
    j01 = Junction(id="j01")
    j02 = Junction(id="j02")
    j03 = Junction(id="j03")
    j04 = Junction(id="j04")
    j05 = Junction(id="j05")
    j06 = Junction(id="j06")
    j07 = Junction(id="j07")
    j08 = Junction(id="j08")
    j09 = Junction(id="j09")
    j10 = Junction(id="j10")
    j11 = Junction(id="j11")
    j12 = Junction(id="j12")
    j13 = Junction(id="j13")
    j14 = Junction(id="j14")
    j15 = Junction(id="j15")

    control.add_junction(j00)
    control.add_junction(j01)
    control.add_junction(j02)
    control.add_junction(j03)
    control.add_junction(j04)
    control.add_junction(j05)
    control.add_junction(j06)
    control.add_junction(j07)
    control.add_junction(j08)
    control.add_junction(j09)
    control.add_junction(j10)
    control.add_junction(j11)
    control.add_junction(j12)
    control.add_junction(j13)
    control.add_junction(j14)
    control.add_junction(j15)

    s00 = Section(id="s00", length=1000.0)
    s01 = Section(id="s01", length=1000.0)
    s02 = Section(id="s02", length=1000.0)
    s03 = Section(id="s03", length=1000.0)
    s04 = Section(id="s04", length=1000.0)
    s05 = Section(id="s05", length=1000.0)
    s06 = Section(id="s06", length=1000.0)
    s07 = Section(id="s07", length=1000.0)
    s08 = Section(id="s08", length=1000.0)
    s09 = Section(id="s09", length=1000.0)
    s10 = Section(id="s10", length=1000.0)
    s11 = Section(id="s11", length=1000.0)
    s12 = Section(id="s12", length=1000.0)
    s13 = Section(id="s13", length=1000.0)
    s14 = Section(id="s14", length=1000.0)
    s15 = Section(id="s15", length=1000.0)
    s16 = Section(id="s16", length=1000.0)
    s17 = Section(id="s17", length=1000.0)
    s18 = Section(id="s18", length=1000.0)
    s19 = Section(id="s19", length=1000.0)
    s20 = Section(id="s20", length=1000.0)
    s21 = Section(id="s21", length=1000.0)
    s22 = Section(id="s22", length=1000.0)
    s23 = Section(id="s23", length=1000.0)

    control.add_section(s00)
    control.add_section(s01)
    control.add_section(s02)
    control.add_section(s03)
    control.add_section(s04)
    control.add_section(s05)
    control.add_section(s06)
    control.add_section(s07)
    control.add_section(s08)
    control.add_section(s09)
    control.add_section(s10)
    control.add_section(s11)
    control.add_section(s12)
    control.add_section(s13)
    control.add_section(s14)
    control.add_section(s15)
    control.add_section(s16)
    control.add_section(s17)
    control.add_section(s18)
    control.add_section(s19)
    control.add_section(s20)
    control.add_section(s21)
    control.add_section(s22)
    control.add_section(s23)

    A, B = SectionConnection.A, SectionConnection.B
    THROUGH, DIVERGING, CONVERGING = (
        JunctionConnection.THROUGH,
        JunctionConnection.DIVERGING,
        JunctionConnection.CONVERGING,
    )
    control.connect(s00, A, j00, DIVERGING)
    control.connect(s00, B, j01, DIVERGING)
    control.connect(s01, A, j00, THROUGH)
    control.connect(s01, B, j03, THROUGH)
    control.connect(s02, A, j01, CONVERGING)
    control.connect(s02, B, j02, CONVERGING)
    control.connect(s03, A, j02, DIVERGING)
    control.connect(s03, B, j03, DIVERGING)
    control.connect(s04, A, j02, THROUGH)
    control.connect(s04, B, j04, CONVERGING)
    control.connect(s05, A, j03, CONVERGING)
    control.connect(s05, B, j05, DIVERGING)
    control.connect(s06, A, j04, DIVERGING)
    control.connect(s06, B, j05, THROUGH)
    control.connect(s07, A, j04, THROUGH)
    control.connect(s07, B, j07, THROUGH)
    control.connect(s08, A, j05, CONVERGING)
    control.connect(s08, B, j06, CONVERGING)
    control.connect(s09, A, j06, DIVERGING)
    control.connect(s09, B, j07, DIVERGING)
    control.connect(s10, A, j06, THROUGH)
    control.connect(s10, B, j09, THROUGH)
    control.connect(s11, A, j07, CONVERGING)
    control.connect(s11, B, j08, CONVERGING)
    control.connect(s12, A, j08, DIVERGING)
    control.connect(s12, B, j09, DIVERGING)
    control.connect(s13, A, j08, THROUGH)
    control.connect(s13, B, j11, THROUGH)
    control.connect(s14, A, j09, CONVERGING)
    control.connect(s14, B, j10, CONVERGING)
    control.connect(s15, A, j10, DIVERGING)
    control.connect(s15, B, j11, DIVERGING)
    control.connect(s16, A, j10, THROUGH)
    control.connect(s16, B, j12, CONVERGING)
    control.connect(s17, A, j11, CONVERGING)
    control.connect(s17, B, j13, THROUGH)
    control.connect(s18, A, j12, DIVERGING)
    control.connect(s18, B, j13, DIVERGING)
    control.connect(s19, A, j12, THROUGH)
    control.connect(s19, B, j15, THROUGH)
    control.connect(s20, A, j13, CONVERGING)
    control.connect(s20, B, j14, CONVERGING)
    control.connect(s21, A, j14, DIVERGING)
    control.connect(s21, B, j15, DIVERGING)
    control.connect(s22, A, j14, THROUGH)
    control.connect(s22, B, j01, THROUGH)
    control.connect(s23, A, j15, CONVERGING)
    control.connect(s23, B, j00, CONVERGING)

    # t0 = Train(
    #     id="t0",
    #     min_input=190,
    #     max_input=240,
    #     max_speed=40.0,
    #     length=14.0,
    #     delta_per_motor_rotation=0.4553,
    #     head_position=DirectedPosition(
    #         section=s3,
    #         target_junction=j1,
    #         mileage=WATARI_RAIL_A + STRAIGHT_RAIL,
    #     ),
    # )
    # t1 = Train(
    #     id="t1",
    #     min_input=150,
    #     max_input=190,
    #     max_speed=40.0,
    #     length=14.0,
    #     delta_per_motor_rotation=0.4321,
    #     head_position=DirectedPosition(
    #         section=s3,
    #         target_junction=j1,
    #         mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2 + OUTER_CURVE_RAIL * 2 + STRAIGHT_RAIL,
    #     ),
    # )
    # t2 = Train(
    #     id="t2",
    #     min_input=180,
    #     max_input=230,
    #     max_speed=40.0,
    #     length=14.0,
    #     delta_per_motor_rotation=0.5048,
    #     head_position=DirectedPosition(
    #         section=s3,
    #         target_junction=j1,
    #         mileage=WATARI_RAIL_A
    #         + STRAIGHT_RAIL * 2
    #         + OUTER_CURVE_RAIL * 2
    #         + STRAIGHT_RAIL
    #         + STRAIGHT_1_2_RAIL
    #         + OUTER_CURVE_RAIL * 2
    #         + STRAIGHT_RAIL,
    #     ),
    # )
    # t3 = Train(
    #     id="t3",
    #     min_input=180,
    #     max_input=220,
    #     max_speed=40.0,
    #     length=14.0,
    #     delta_per_motor_rotation=0.4508,
    #     head_position=DirectedPosition(
    #         section=s3,
    #         target_junction=j1,
    #         mileage=WATARI_RAIL_A
    #         + STRAIGHT_RAIL * 2
    #         + OUTER_CURVE_RAIL * 2
    #         + STRAIGHT_RAIL
    #         + STRAIGHT_1_2_RAIL
    #         + OUTER_CURVE_RAIL * 2
    #         + STRAIGHT_RAIL * 3
    #         + OUTER_CURVE_RAIL * 2,
    #     ),
    # )
    # t4 = Train(
    #     id="t4",
    #     min_input=180,
    #     max_input=230,
    #     max_speed=40.0,
    #     length=40.0,
    #     delta_per_motor_rotation=0.4241,
    #     head_position=DirectedPosition(
    #         section=s1,
    #         target_junction=j0,
    #         mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 4,
    #     ),
    # )

    # control.add_train(t0)
    # control.add_train(t1)
    # control.add_train(t2)
    # control.add_train(t3)
    # control.add_train(t4)

    # stop_0 = Stop(
    #     id="stop_0",
    #     position=DirectedPosition(
    #         section=s3,
    #         target_junction=j1,
    #         mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 0.8,
    #     ),
    # )
    # stop_1 = Stop(
    #     id="stop_1",
    #     position=DirectedPosition(
    #         section=s3,
    #         target_junction=j1,
    #         mileage=WATARI_RAIL_A
    #         + STRAIGHT_RAIL * 2
    #         + OUTER_CURVE_RAIL * 2
    #         + STRAIGHT_RAIL
    #         + STRAIGHT_1_2_RAIL
    #         + OUTER_CURVE_RAIL * 2
    #         + STRAIGHT_RAIL * 1.8,
    #     ),
    # )

    # control.add_stop(stop_0)
    # control.add_stop(stop_1)

    # station_0 = Station(id="station_0", stops=[stop_0])
    # station_1 = Station(id="station_1", stops=[stop_1])

    # control.add_station(station_0)
    # control.add_station(station_1)

    # p1 = SensorPosition(
    #     id="position_0433ca30af6180",
    #     section=s3,
    #     target_junction=j1,
    #     mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 0.5,
    # )
    # p2 = SensorPosition(
    #     id="position_047c6731af6180",
    #     section=s3,
    #     target_junction=j1,
    #     mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2 + OUTER_CURVE_RAIL * 0.5,
    # )
    # p3 = SensorPosition(
    #     id="position_04117931af6180",
    #     section=s3,
    #     target_junction=j1,
    #     mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2 + OUTER_CURVE_RAIL * 2 + STRAIGHT_1_2_RAIL + STRAIGHT_RAIL * 0.5,
    # )
    # p4 = SensorPosition(
    #     id="position_0497d230af6180",
    #     section=s3,
    #     target_junction=j1,
    #     mileage=WATARI_RAIL_A
    #     + STRAIGHT_RAIL * 2
    #     + OUTER_CURVE_RAIL * 2
    #     + STRAIGHT_RAIL
    #     + STRAIGHT_1_2_RAIL
    #     + OUTER_CURVE_RAIL * 1.5,
    # )
    # p5 = SensorPosition(
    #     id="position_04d7932baf6180",
    #     section=s3,
    #     target_junction=j1,
    #     mileage=WATARI_RAIL_A
    #     + STRAIGHT_RAIL * 2
    #     + OUTER_CURVE_RAIL * 2
    #     + STRAIGHT_RAIL
    #     + STRAIGHT_1_2_RAIL
    #     + OUTER_CURVE_RAIL * 2
    #     + STRAIGHT_RAIL * 1.5,
    # )
    # p6 = SensorPosition(
    #     id="position_040e6f2daf6180",
    #     section=s3,
    #     target_junction=j1,
    #     mileage=WATARI_RAIL_A
    #     + STRAIGHT_RAIL * 2
    #     + OUTER_CURVE_RAIL * 2
    #     + STRAIGHT_RAIL
    #     + STRAIGHT_1_2_RAIL
    #     + OUTER_CURVE_RAIL * 2
    #     + STRAIGHT_RAIL * 3
    #     + OUTER_CURVE_RAIL * 0.5,
    # )
    # p7 = SensorPosition(
    #     id="position_04059229af6180",
    #     section=s3,
    #     target_junction=j1,
    #     mileage=WATARI_RAIL_A
    #     + STRAIGHT_RAIL * 2
    #     + OUTER_CURVE_RAIL * 2
    #     + STRAIGHT_RAIL
    #     + STRAIGHT_1_2_RAIL
    #     + OUTER_CURVE_RAIL * 2
    #     + STRAIGHT_RAIL * 3
    #     + OUTER_CURVE_RAIL * 1.5,
    # )
    # p8 = SensorPosition(
    #     id="position_04f1ac2baf6180",
    #     section=s2,
    #     target_junction=j2,
    #     mileage=WATARI_RAIL_B + 4.70 + OUTER_CURVE_RAIL * 0.5,
    # )
    # p9 = SensorPosition(
    #     id="position_0451002baf6180",
    #     section=s2,
    #     target_junction=j2,
    #     mileage=WATARI_RAIL_B + 4.70 + OUTER_CURVE_RAIL * 1.5,
    # )
    # p10 = SensorPosition(
    #     id="position_040a992aaf6181",
    #     section=s1,
    #     target_junction=j0,
    #     mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 0.5,
    # )
    # p11 = SensorPosition(
    #     id="position_0494a12baf6180",
    #     section=s1,
    #     target_junction=j0,
    #     mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 0.5,
    # )
    # p12 = SensorPosition(
    #     id="position_04299928af6180",
    #     section=s1,
    #     target_junction=j0,
    #     mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 2.5,
    # )
    # p13 = SensorPosition(
    #     id="position_047d8129af6180",
    #     section=s1,
    #     target_junction=j0,
    #     mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 3 + STRAIGHT_RAIL * 3,
    # )
    # p14 = SensorPosition(
    #     id="position_042d962baf6180",
    #     section=s1,
    #     target_junction=j0,
    #     mileage=WATARI_RAIL_B + STRAIGHT_RAIL * 3 + CURVE_RAIL * 3 + STRAIGHT_RAIL * 4 + CURVE_RAIL * 0.5,
    # )
    # p15 = SensorPosition(
    #     id="position_0455b128af6180",
    #     section=s1,
    #     target_junction=j0,
    #     mileage=WATARI_RAIL_B
    #     + STRAIGHT_RAIL * 3
    #     + CURVE_RAIL * 3
    #     + STRAIGHT_RAIL * 4
    #     + CURVE_RAIL
    #     + STRAIGHT_RAIL * 2
    #     + 3.67
    #     + CURVE_RAIL * 0.5,
    # )
    # p16 = SensorPosition(
    #     id="position_04369a28af6180",
    #     section=s1,
    #     target_junction=j0,
    #     mileage=WATARI_RAIL_B
    #     + STRAIGHT_RAIL * 3
    #     + CURVE_RAIL * 3
    #     + STRAIGHT_RAIL * 4
    #     + CURVE_RAIL
    #     + STRAIGHT_RAIL * 2
    #     + 3.67
    #     + CURVE_RAIL * 1.5,
    # )
    # p17 = SensorPosition(
    #     id="position_04a96f28af6180",
    #     section=s0,
    #     target_junction=j3,
    #     mileage=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL * 0.5,
    # )
    # p18 = SensorPosition(
    #     id="position_044be628af6180",
    #     section=s0,
    #     target_junction=j3,
    #     mileage=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL + CURVE_RAIL * 1.5,
    # )
    # p19 = SensorPosition(
    #     id="position_0489e22caf6180",
    #     section=s0,
    #     target_junction=j3,
    #     mileage=WATARI_RAIL_A + 7.03 + STRAIGHT_RAIL + CURVE_RAIL * 2 + STRAIGHT_RAIL * 0.5,
    # )

    # control.add_sensor_position(p1)
    # control.add_sensor_position(p2)
    # control.add_sensor_position(p3)
    # control.add_sensor_position(p4)
    # control.add_sensor_position(p5)
    # control.add_sensor_position(p6)
    # control.add_sensor_position(p7)
    # control.add_sensor_position(p8)
    # control.add_sensor_position(p9)
    # control.add_sensor_position(p10)
    # control.add_sensor_position(p11)
    # control.add_sensor_position(p12)
    # control.add_sensor_position(p13)
    # control.add_sensor_position(p14)
    # control.add_sensor_position(p15)
    # control.add_sensor_position(p16)
    # control.add_sensor_position(p17)
    # control.add_sensor_position(p18)
    # control.add_sensor_position(p19)

    # obstacle_0 = Obstacle(
    #     id="obstacle_0",
    #     position=UndirectedPosition(
    #         section=s3,
    #         mileage=WATARI_RAIL_A + STRAIGHT_RAIL * 2,
    #     ),
    #     is_detected=False,
    # )

    # control.add_obstacle(obstacle_0)

    control.verify()
    return control
