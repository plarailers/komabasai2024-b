from fastapi import APIRouter, Request
from ptcs_control import Control
from ptcs_control.components import Train
from ptcs_control.railway_config import RailwayConfig
from ptcs_control.railway_state import RailwayState
import pydantic


api_router = APIRouter()


@api_router.get("/hello")
def hello() -> dict:
    return {"message": "hello"}


@api_router.get("/config", response_model=RailwayConfig)
def get_config(request: Request) -> "RailwayConfig":
    control: Control = request.app.state.control
    return control.get_config()


@api_router.get("/state", response_model=RailwayState)
def get_state(request: Request) -> "RailwayState":
    control: Control = request.app.state.control
    return control.get_state()


class MoveTrainParams(pydantic.BaseModel):
    delta: float


@api_router.post("/state/trains/{train_id}/move")
def move_train(train_id: str, params: MoveTrainParams, request: Request) -> None:
    """
    指定された列車を距離 delta 分だけ進める。
    デバッグ用。
    """
    control: Control = request.app.state.control
    train = Train(train_id)
    control.move_train(train, params.delta)
