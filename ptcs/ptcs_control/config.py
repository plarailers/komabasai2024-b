import logging

from . import gogatsusai2024
from .control import Control, create_empty_logger


def create_control(logger: logging.Logger | None = None) -> Control:
    if logger is None:
        logger = create_empty_logger()

    control = Control(logger=logger)

    gogatsusai2024.configure(control)

    control.verify()

    return control
