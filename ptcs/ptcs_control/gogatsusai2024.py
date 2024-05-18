import logging

from . import gogatsusai2024_generated
from .components.junction import JunctionConnection
from .components.position import DirectedPosition
from .components.section import SectionConnection
from .components.sensor_position import SensorPosition
from .components.train import Train, TrainType
from .control.base import create_empty_logger
from .control.fixed_block import FixedBlockControl


def create_control(logger: logging.Logger | None = None) -> FixedBlockControl:
    if logger is None:
        logger = create_empty_logger()

    control = FixedBlockControl(logger=logger)

    # 自動生成による設定
    gogatsusai2024_generated.configure(control)

    # 手動による設定
    configure(control)

    control.verify()

    return control


def configure(control: FixedBlockControl) -> None:
    t0 = Train(
        id="t0",
        type=TrainType.LimitedExpress,
        min_input=190,
        max_input=220,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4553,
        head_position=DirectedPosition(
            section=control.sections["S01"],
            target_junction=control.sections["S01"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t1 = Train(
        id="t1",
        type=TrainType.LimitedExpress,
        min_input=190,
        max_input=220,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4321,
        head_position=DirectedPosition(
            section=control.sections["S24"],
            target_junction=control.sections["S24"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t2 = Train(
        id="t2",
        type=TrainType.LimitedExpress,
        min_input=170,
        max_input=210,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.5048,
        head_position=DirectedPosition(
            section=control.sections["S42"],
            target_junction=control.sections["S42"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t3 = Train(
        id="t3",
        type=TrainType.CommuterSemiExpress,
        min_input=80,
        max_input=120,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4508,
        head_position=DirectedPosition(
            section=control.sections["S13"],
            target_junction=control.sections["S13"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t4 = Train(
        id="t4",
        type=TrainType.CommuterSemiExpress,
        min_input=10,
        max_input=220,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241,
        head_position=DirectedPosition(
            section=control.sections["S31"],
            target_junction=control.sections["S31"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t5 = Train(
        id="t5",
        type=TrainType.CommuterSemiExpress,
        min_input=180,
        max_input=220,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241,
        head_position=DirectedPosition(
            section=control.sections["S52"],
            target_junction=control.sections["S52"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t6 = Train(
        id="t6",
        type=TrainType.Local,
        min_input=100,
        max_input=150,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241,
        head_position=DirectedPosition(
            section=control.sections["S00"],
            target_junction=control.sections["S00"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t7 = Train(
        id="t7",
        type=TrainType.Local,
        min_input=190,
        max_input=220,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241,
        head_position=DirectedPosition(
            section=control.sections["S21"],
            target_junction=control.sections["S21"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t8 = Train(
        id="t8",
        type=TrainType.Local,
        min_input=180,
        max_input=210,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241,
        head_position=DirectedPosition(
            section=control.sections["S30"],
            target_junction=control.sections["S30"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t9 = Train(
        id="t9",
        type=TrainType.Local,
        min_input=190,
        max_input=220,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241,
        head_position=DirectedPosition(
            section=control.sections["S49"],
            target_junction=control.sections["S49"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )

    # control.add_train(t0)
    # control.add_train(t1)
    control.add_train(t2)
    # control.add_train(t3)
    # control.add_train(t4)
    control.add_train(t5)
    # control.add_train(t6)
    # control.add_train(t7)
    control.add_train(t8)
    # control.add_train(t9)

    for sensor_position_id, uid, junction_id in [
        # ("P01", "0433ca30af6180", ""),
        # ("P02", "047c6731af6180", ""),
        # ("P03", "04117931af6180", ""),
        # ("P04", "0497d230af6180", ""),
        # ("P05", "04d7932baf6180", ""),
        # ("P06", "040e6f2daf6180", ""),
        # ("P07", "04059229af6180", ""),
        # ("P08", "04f1ac2baf6180", ""),
        # ("P09", "0451002baf6180", ""),
        # ("P10", "040a992aaf6181", ""),
        # ("P11", "0494a12baf6180", ""),
        # ("P12", "04299928af6180", ""),
        # ("P13", "047d8129af6180", ""),
        # ("P14", "042d962baf6180", ""),
        # ("P15", "0455b128af6180", ""),
        # ("P16", "04369a28af6180", ""),
        # ("P17", "04a96f28af6180", ""),
        # ("P18", "044be628af6180", ""),
        # ("P19", "0489e22caf6180", ""),
        # ("P20", "044f62e1", ""),
        ("P21", "4402d7e2", "c121"),
        ("P22", "14ea36e1", "c122"),
        ("P23", "b4aa5ee1", "c123"),
        ("P24", "64175ae1", "c124"),
        ("P25", "943a69e1", "c125"),
        ("P26", "34d041e1", "c126"),
        ("P27", "b4345fe1", "c127"),
        ("P28", "04b966e1", "c128"),
        ("P29", "840b83e2", "c129"),
        ("P30", "f47992e2", "j15"),
        ("P31", "44c495e2", "c131"),
        ("P32", "84e8e3e2", "c132"),
        ("P33", "6448cee2", "c133"),
        ("P34", "74be8ee1", "c134"),
        ("P35", "14df82e2", "c135"),
        ("P36", "94e4e3e2", "c136"),
        ("P37", "44086de1", "c137"),
        ("P38", "c4225be1", "c138"),
        ("P39", "44086de1", "c139"),
        ("P40", "b49a5ee1", "c140"),
        ("P41", "446dd7e2", "c141"),
        ("P42", "74765ce1", "c142"),
        # ("P43", "84576be1", ""),
        ("P44", "24f992e2", "c144"),
        ("P45", "54c383e1", "c145"),
        ("P46", "d413dee2", "c146"),
        ("P47", "6467d7e2", "c147"),
        ("P48", "445dd9e2", "c148"),
        ("P49", "745935e1", "c149"),
        ("P50", "740876e1", "j07"),
        ("P51", "74f562e1", "c151"),
        ("P52", "448f81e2", "c152"),
        ("P53", "c42566e1", "c153"),
        ("P54", "f4ed6ae1", "c154"),
        # ("P55", "44e76ae1", ""),
        ("P56", "145667e1", "c156"),
        ("P57", "a4cac8e2", "c157"),
        ("P58", "f49b68e1", "c158"),
        ("P59", "048468e1", "c159"),
        ("P60", "145f63e1", "c160"),
        ("P61", "447f5de1", "c161"),
        ("P62", "64da62e1", "c162"),
        # ("P63", "f493dde2", ""),
        # ("P64", "947968e1", ""),
        # ("P65", "0477cee2", ""),
        # ("P66", "b46e63e1", ""),
        # ("P67", "84d07ae1", ""),
        # ("P68", "241157e1", ""),
        # ("P69", "e4c0e3e2", ""),
    ]:
        junction = control.junctions[junction_id]

        section_t = junction.connected_sections[JunctionConnection.THROUGH]
        section_d = junction.connected_sections.get(JunctionConnection.DIVERGING)
        section_c = junction.connected_sections[JunctionConnection.CONVERGING]

        # 2 セクションの接続（ID が `c` から始まる）の場合
        if section_d is None:
            # THROUGH セクションか CONVERGING セクションの始点が自ジャンクションなら始点付近に置く
            if section_t.connected_junctions[SectionConnection.A] == junction:
                sensor_position = SensorPosition(
                    id=sensor_position_id,
                    uid=uid,
                    section=section_t,
                    mileage=0.0,
                    target_junction=section_t.get_opposite_junction(junction),
                )
            elif section_c.connected_junctions[SectionConnection.A] == junction:
                sensor_position = SensorPosition(
                    id=sensor_position_id,
                    uid=uid,
                    section=section_c,
                    mileage=0.0,
                    target_junction=section_c.get_opposite_junction(junction),
                )
            else:
                raise Exception()

        # 3 セクションの接続（ID が `j` から始まる）の場合
        else:
            # CONVERGING セクションの始点が自ジャンクション（合流点）なら始点付近に置く
            # CONVERGING セクションの終点が自ジャンクション（分岐点）なら終点付近に置く
            if section_c.connected_junctions[SectionConnection.A] == junction:
                sensor_position = SensorPosition(
                    id=sensor_position_id,
                    uid=uid,
                    section=section_c,
                    mileage=0.0,
                    target_junction=section_c.get_opposite_junction(junction),
                )
            elif section_c.connected_junctions[SectionConnection.B] == junction:
                sensor_position = SensorPosition(
                    id=sensor_position_id,
                    uid=uid,
                    section=section_c,
                    mileage=section_c.length,
                    target_junction=junction,
                )
            else:
                raise Exception()

        control.add_sensor_position(sensor_position)
