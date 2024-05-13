import logging

from . import gogatsusai2024
from .control.base import create_empty_logger
from .control.fixed_block import FixedBlockControl


def create_control(logger: logging.Logger | None = None) -> FixedBlockControl:
    if logger is None:
        logger = create_empty_logger()

    control = FixedBlockControl(logger=logger)

    gogatsusai2024.configure(control)

    control.verify()

    return control
