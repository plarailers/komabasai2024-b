from __future__ import annotations

from pydantic import BaseModel


class RailwayCommand(BaseModel):
    """
    指令値
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる


RailwayCommand.update_forward_refs()


def init_command() -> RailwayCommand:
    command = RailwayCommand()

    return command
