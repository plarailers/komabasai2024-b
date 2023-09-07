import pydantic
from fastapi import APIRouter, Request

from ptcs_control import Control
from ptcs_control.components import Direction, Junction, Position, Section, Train
from ptcs_control.railway_command import RailwayCommand
from ptcs_control.railway_config import RailwayConfig
from ptcs_control.railway_state import RailwayState

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


@api_router.get("/command", response_model=RailwayCommand)
def get_command(request: Request) -> "RailwayCommand":
    control: Control = request.app.state.control
    return control.get_command()


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
    control.update()


class PutTrainParams(pydantic.BaseModel):
    position_id: str


@api_router.post("/state/trains/{train_id}/put")
def put_train(train_id: str, params: PutTrainParams, request: Request) -> None:
    """
    指定された列車の位置を修正する。
    デバッグ用。
    """
    control: Control = request.app.state.control
    train = Train(train_id)
    position = Position(params.position_id)
    control.put_train(train, position)
    control.update()


class UpdateJunctionParams(pydantic.BaseModel):
    direction: Direction


@api_router.post("/state/junctions/{junction_id}/update")
def update_junction(junction_id: str, params: UpdateJunctionParams, request: Request) -> None:
    """
    指定された分岐点の方向を更新する。
    デバッグ用。
    """
    control: Control = request.app.state.control
    junction = Junction(junction_id)
    control.update_junction(junction, params.direction)


@api_router.post("/state/sections/{section_id}/block")
def block_section(section_id: str, request: Request) -> None:
    """
    指定された区間に障害物を発生させる。
    デバッグ用。
    """
    control: Control = request.app.state.control
    section = Section(section_id)
    control.block_section(section)
    control.update()


@api_router.post("/state/sections/{section_id}/unblock")
def unblock_section(section_id: str, request: Request) -> None:
    """
    指定された区間の障害物を取り除く。
    デバッグ用。
    """
    control: Control = request.app.state.control
    section = Section(section_id)
    control.unblock_section(section)
    control.update()
