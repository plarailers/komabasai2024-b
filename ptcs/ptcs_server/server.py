import asyncio
import logging
import os
import threading
import time

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ptcs_bridge.master_controller_client import MasterControllerClient
from ptcs_bridge.train_base import TrainBase
from ptcs_bridge.train_client import TrainClient
from ptcs_bridge.train_simulator import TrainSimulator
from ptcs_bridge.wire_pole_client import WirePoleClient
from ptcs_control.control import Control
from ptcs_control.mft2023 import create_control

from .api import api_router
from .mft2023 import create_bridge
from .points import PointSwitcher, PointSwitcherManager

DEFAULT_PORT = 5000


class ServerArgs(BaseModel):
    port: int = DEFAULT_PORT
    bridge: bool = False
    debug: bool = False


def set_server_args(args: ServerArgs) -> None:
    """
    環境変数を通じてサーバーへの引数を渡す。
    """
    os.environ["PTCS_SERVER_ARGS"] = args.model_dump_json()


def get_server_args() -> ServerArgs:
    """
    環境変数を通じてサーバーへの引数を受け取る。
    """
    raw_args = os.environ.get("PTCS_SERVER_ARGS")
    args = ServerArgs.model_validate_json(raw_args) if raw_args else ServerArgs()
    return args


def create_app() -> FastAPI:
    logger = logging.getLogger("uvicorn")

    args = get_server_args()
    logger.info("server args: %s", args)

    if args.bridge:
        return create_app_with_bridge()
    else:
        return create_app_without_bridge()


def create_app_without_bridge() -> FastAPI:
    logger = logging.getLogger("uvicorn")

    app = FastAPI(generate_unique_id_function=lambda route: route.name)

    control = create_control(logger=logger)
    app.state.control = control

    # `/api` 以下で API を呼び出す
    app.include_router(api_router, prefix="/api")

    # `/` 以下で静的ファイルを配信する
    app.mount("/", StaticFiles(directory="./ptcs_ui/dist", html=True), name="static")

    bridge = create_bridge()
    app.state.bridge = bridge

    async def control_loop():
        while True:
            # control 内部の時計を現実世界の時間において進める
            await asyncio.sleep(0.1)
            control.tick()
            control.update()

    control_loop_task = asyncio.create_task(control_loop())
    app.state.control_loop_task = control_loop_task

    async def bridge_loop():
        await bridge.connect_all()

        async def send_motor_input():
            for train_id, train_control in control.trains.items():
                train_client = bridge.trains.get(train_id)
                if train_client is None:
                    continue
                match train_client:
                    case TrainSimulator():
                        await train_client.send_speed(train_control.speed_command)
                    case TrainClient():
                        motor_input = train_control.calc_input(train_control.speed_command)
                        await train_client.send_motor_input(motor_input)

        def handle_notify_position_id(train_client: TrainBase, position_id: int):
            train_control = control.trains.get(train_client.id)
            position = control.sensor_positions.get(f"position_{position_id}")
            if train_control is None or position is None:
                return
            train_control.fix_position(position)

        def handle_notify_rotation(train_client: TrainBase, _rotation: int):
            train_control = control.trains.get(train_client.id)
            if train_control is None:
                return
            train_control.move_forward_mr(1)

        def handle_notify_voltage(train_client: TrainBase, _voltage_mV: int):
            train_control = control.trains.get(train_client.id)
            if train_control is None:
                return
            train_control.voltage_mV = _voltage_mV

        for train in bridge.trains.values():
            match train:
                case TrainClient():
                    await train.start_notify_position_id(handle_notify_position_id)
                    await train.start_notify_voltage(handle_notify_voltage)
            await train.start_notify_rotation(handle_notify_rotation)

        def handle_notify_collapse(obstacle_client: WirePoleClient, is_collapsed: bool):
            obstacle_control = control.obstacles.get(obstacle_client.id)
            if obstacle_control is None:
                return
            obstacle_control.is_detected = is_collapsed

        for obstacle in bridge.obstacles.values():
            await obstacle.start_notify_collapse(handle_notify_collapse)

        def handle_notify_speed(controller_client: MasterControllerClient, speed: int):
            train_control = control.trains.get(controller_client.id)
            if train_control is None:
                return
            train_control.manual_speed = speed / 255 * train_control.max_speed

        for controller in bridge.controllers.values():
            await controller.start_notify_speed(handle_notify_speed)

        while True:
            await asyncio.sleep(0.5)
            await send_motor_input()

    bridge_loop_task = asyncio.create_task(bridge_loop())
    app.state.bridge_loop_task = bridge_loop_task

    @app.on_event("shutdown")
    async def on_shutdown():
        for train in bridge.trains.values():
            match train:
                case TrainSimulator():
                    await train.send_speed(0.0)
                case TrainClient():
                    if train.is_connected:
                        await train.send_motor_input(0)

        await bridge.disconnect_all()

    return app


def create_app_with_bridge() -> FastAPI:
    app = create_app_without_bridge()

    assert isinstance(app.state.control, Control)
    control = app.state.control

    # TODO: ソースコードの変更なしに COM ポートを指定できるようにする
    ENABLE_POINTS = True
    POINTS_PORT = "COM8"

    # すべてのポイントへの信号
    def send_to_points() -> None:
        for junction in control.junctions.values():
            point_switchers.send(junction.id, junction.current_direction)

    # ポイント
    if ENABLE_POINTS:
        point_switchers = PointSwitcherManager()
        point_switcher = PointSwitcher(POINTS_PORT)
        point_switchers.register("j0", point_switcher, 3)
        point_switchers.register("j1", point_switcher, 0)
        point_switchers.register("j2", point_switcher, 2)
        point_switchers.register("j3", point_switcher, 1)
        point_switchers.start()
        app.state.point_switchers = point_switchers

    def run_sender() -> None:
        while True:
            time.sleep(0.5)
            if ENABLE_POINTS:
                send_to_points()

    sender_thread = threading.Thread(target=run_sender, daemon=True)
    sender_thread.start()
    app.state.sender_thread = sender_thread

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        print("shutting down...")

    return app


def serve(*, port: int = DEFAULT_PORT, bridge: bool = False, debug: bool = False) -> None:
    """
    列車制御システムを Web サーバーとして起動する。
    `debug` を `True` にすると、ソースコードに変更があったときにリロードされる。
    """

    set_server_args(ServerArgs(port=port, bridge=bridge, debug=debug))

    if debug:
        uvicorn.run(
            "ptcs_server.server:create_app",
            factory=True,
            port=port,
            log_level="warning",
            reload=True,
            reload_dirs=["ptcs_bridge", "ptcs_control", "ptcs_server"],
        )
    else:
        uvicorn.run(
            "ptcs_server.server:create_app",
            factory=True,
            port=port,
            log_level="warning",
        )
