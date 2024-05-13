import pydantic
from fastapi import APIRouter, Request

from ptcs_control.components.junction import PointDirection
from ptcs_control.control.base import BaseControl

from .types.state import RailwayState, get_state_from_control

api_router = APIRouter()


@api_router.get("/hello")
def hello() -> dict:
    return {"message": "hello"}


@api_router.get("/state")
def get_state(request: Request) -> RailwayState:
    control: BaseControl = request.app.state.control
    return get_state_from_control(control)


class MoveTrainParams(pydantic.BaseModel):
    delta: float


@api_router.post("/state/trains/{train_id}/move")
def move_train(train_id: str, params: MoveTrainParams, request: Request) -> None:
    """
    指定された列車を距離 delta 分だけ進める。
    デバッグ用。
    """
    control: BaseControl = request.app.state.control
    train = control.trains[train_id]
    train.move_forward(params.delta)
    control.update()


class PutTrainParams(pydantic.BaseModel):
    position_id: str


@api_router.post("/state/trains/{train_id}/put")
def put_train(train_id: str, params: PutTrainParams, request: Request) -> None:
    """
    指定された列車の位置を修正する。
    デバッグ用。
    """
    control: BaseControl = request.app.state.control
    train = control.trains[train_id]
    position = control.sensor_positions[params.position_id]
    train.fix_position(position)
    control.update()


class UpdateJunctionParams(pydantic.BaseModel):
    direction: PointDirection


@api_router.post("/state/junctions/{junction_id}/update")
def update_junction(junction_id: str, params: UpdateJunctionParams, request: Request) -> None:
    """
    指定された分岐点の方向を更新する。
    デバッグ用。
    """
    control: BaseControl = request.app.state.control
    junction = control.junctions[junction_id]
    junction.manual_direction = params.direction
    control.update()


@api_router.post("/state/obstacles/{obstacle_id}/detect")
def detect_obstacle(obstacle_id: str, request: Request) -> None:
    """
    指定された障害物を発生させる。
    デバッグ用。
    """
    control: BaseControl = request.app.state.control
    obstacle = control.obstacles[obstacle_id]
    obstacle.is_detected = True
    control.update()


@api_router.post("/state/obstacles/{obstacle_id}/clear")
def clear_obstacle(obstacle_id: str, request: Request) -> None:
    """
    指定された障害物を撤去する。
    デバッグ用。
    """
    control: BaseControl = request.app.state.control
    obstacle = control.obstacles[obstacle_id]
    obstacle.is_detected = False
    control.update()


@api_router.post("/state/sections/{section_id}/block")
def block_section(section_id: str, request: Request) -> None:
    """
    指定された区間に障害物を発生させる。
    デバッグ用。
    """
    control: BaseControl = request.app.state.control
    section = control.sections[section_id]
    section.block()
    control.update()


@api_router.post("/state/sections/{section_id}/unblock")
def unblock_section(section_id: str, request: Request) -> None:
    """
    指定された区間の障害物を取り除く。
    デバッグ用。
    """
    control: BaseControl = request.app.state.control
    section = control.sections[section_id]
    section.unblock()
    control.update()
