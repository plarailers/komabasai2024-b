from __future__ import annotations

from pydantic import BaseModel


class RailwayState(BaseModel):
    """
    路線の状態
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる


RailwayState.update_forward_refs()


def init_state() -> RailwayState:
    state = RailwayState()

    return state
