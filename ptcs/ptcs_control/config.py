import logging

from . import gogatsusai2024
from .components.position import DirectedPosition
from .components.section import SectionConnection
from .components.train import Train, TrainType
from .control.base import create_empty_logger
from .control.fixed_block import FixedBlockControl


def create_control(logger: logging.Logger | None = None) -> FixedBlockControl:
    if logger is None:
        logger = create_empty_logger()

    control = FixedBlockControl(logger=logger)

    # 自動生成による設定
    gogatsusai2024.configure(control)

    # 手動による設定
    configure(control)

    control.verify()

    return control


def configure(control: FixedBlockControl) -> None:
    t0 = Train(
        id="t0",
        type=TrainType.LimitedExpress,
        min_input=190,
        max_input=240,
        max_speed=40.0,
        length=14.0,
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
        min_input=150,
        max_input=190,
        max_speed=40.0,
        length=14.0,
        delta_per_motor_rotation=0.4321,
        head_position=DirectedPosition(
            section=control.sections["S31"],
            target_junction=control.sections["S31"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t2 = Train(
        id="t2",
        type=TrainType.CommuterSemiExpress,
        min_input=180,
        max_input=230,
        max_speed=40.0,
        length=14.0,
        delta_per_motor_rotation=0.5048,
        head_position=DirectedPosition(
            section=control.sections["S22"],
            target_junction=control.sections["S22"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t3 = Train(
        id="t3",
        type=TrainType.CommuterSemiExpress,
        min_input=180,
        max_input=220,
        max_speed=40.0,
        length=14.0,
        delta_per_motor_rotation=0.4508,
        head_position=DirectedPosition(
            section=control.sections["S50"],
            target_junction=control.sections["S50"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )
    t4 = Train(
        id="t4",
        type=TrainType.Local,
        min_input=180,
        max_input=230,
        max_speed=40.0,
        length=40.0,
        delta_per_motor_rotation=0.4241,
        head_position=DirectedPosition(
            section=control.sections["S08"],
            target_junction=control.sections["S08"].connected_junctions[SectionConnection.B],
            mileage=1.0,
        ),
    )

    control.add_train(t0)
    control.add_train(t1)
    control.add_train(t2)
    control.add_train(t3)
    control.add_train(t4)
