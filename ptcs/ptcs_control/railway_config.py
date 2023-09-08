from __future__ import annotations

from pydantic import BaseModel


class RailwayConfig(BaseModel):
    """
    路線の設定
    """

    # NOTE: Junction などを "" で囲むと ForwardRef に関するエラーが起こる


RailwayConfig.update_forward_refs()


def init_config() -> RailwayConfig:
    config = RailwayConfig()

    return config
