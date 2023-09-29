import asyncio
import logging
import os
import threading
import time
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ptcs_bridge.bridge import Bridge
from ptcs_bridge.train_base import TrainBase
from ptcs_bridge.train_simulator import TrainSimulator
from ptcs_control.control import Control
from ptcs_control.mft2023 import create_control

from .api import api_router
from .bridges import BridgeManager, BridgeTarget
from .button import Button
from .points import PointSwitcher, PointSwitcherManager

DEFAULT_PORT = 5000


class ServerArgs(BaseModel):
    port: int = DEFAULT_PORT
    bridge: bool = False
    debug: bool = False


def create_app() -> FastAPI:
    logger = logging.getLogger("uvicorn")

    raw_args = os.environ.get("PTCS_SERVER_ARGS")
    logger.info("raw server args: %s", raw_args)

    args = ServerArgs.parse_raw(raw_args) if raw_args else ServerArgs()
    logger.info("parsed server args: %s", args)

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

    t0 = TrainSimulator("t0")
    t1 = TrainSimulator("t1")

    async def loop():
        await t0.connect()
        await t1.connect()

        def handle_notify_rotation(train: TrainBase, _rotation: int):
            match train.id:
                case "t0":
                    control.trains["t0"].move_forward_mr(1)
                case "t1":
                    control.trains["t1"].move_forward_mr(1)

        await t0.start_notify_rotation(handle_notify_rotation)
        await t1.start_notify_rotation(handle_notify_rotation)

        while True:
            # control 内部の時計を現実世界の時間において進める
            await asyncio.sleep(0.1)
            control.tick()
            control.update()

            for train_id, train in control.trains.items():
                match train_id:
                    case "t0":
                        await t0.send_speed(train.speed_command)
                    case "t1":
                        await t1.send_speed(train.speed_command)

    task = asyncio.create_task(loop())
    app.state.task = task

    return app


def create_app_with_bridge() -> FastAPI:
    app = create_app_without_bridge()

    assert isinstance(app.state.control, Control)
    control = app.state.control

    # TODO: ソースコードの変更なしに COM ポートを指定できるようにする
    ENABLE_TRAINS = True
    ENABLE_POINTS = True
    ENABLE_BUTTON = True
    TRAIN_PORTS = {"t0": "COM5", "t1": "COM3"}
    POINTS_PORT = "COM9"
    BUTTON_PORT = "COM6"

    # 列車からの信号
    def receive_from_train(train_id: BridgeTarget, data: Any) -> None:
        train = control.trains[train_id]
        # モーター回転量
        if "mR" in data:
            train.move_forward_mr(data["mR"])
        # APS 信号
        elif "pID" in data:
            position_id = bridges.get_position(data["pID"])
            if position_id is not None:
                train.fix_position(position_id)

    # 異常発生ボタンからの信号
    def receive_from_button(data: Any) -> None:
        s3 = control.sections["s3"]
        if data["blocked"]:
            s3.block()
        else:
            s3.unblock()

    # すべての列車への信号
    def send_to_trains() -> None:
        for train in control.trains.values():
            motor_input = train.calc_input(train.speed_command)
            bridges.send(train.id, {"mI": motor_input})

    # すべてのポイントへの信号
    def send_to_points() -> None:
        for junction in control.junctions.values():
            point_switchers.send(junction.id, junction.current_direction)

    # 列車
    if ENABLE_TRAINS:
        bridges = BridgeManager(callback=receive_from_train)
        bridges.print_ports()
        bridges.register("t0", Bridge(TRAIN_PORTS["t0"]))
        bridges.register("t1", Bridge(TRAIN_PORTS["t1"]))
        bridges.register_position(control.sensor_positions["position_80"], 80)
        bridges.register_position(control.sensor_positions["position_173"], 173)
        bridges.register_position(control.sensor_positions["position_138"], 138)
        bridges.register_position(control.sensor_positions["position_255"], 255)
        bridges.start()
        app.state.bridges = bridges

    # ポイント
    if ENABLE_POINTS:
        point_switchers = PointSwitcherManager()
        point_switcher = PointSwitcher(POINTS_PORT)
        point_switchers.register("j0", point_switcher, 0)
        point_switchers.register("j1", point_switcher, 1)
        point_switchers.register("j2", point_switcher, 2)
        point_switchers.register("j3", point_switcher, 3)
        point_switchers.start()
        app.state.point_switchers = point_switchers

    # 異常発生ボタン
    if ENABLE_BUTTON:
        button = Button(BUTTON_PORT, callback=receive_from_button)
        button.start()
        app.state.button = button

    def run_sender() -> None:
        while True:
            time.sleep(0.5)
            if ENABLE_TRAINS:
                send_to_trains()
            if ENABLE_POINTS:
                send_to_points()

    sender_thread = threading.Thread(target=run_sender, daemon=True)
    sender_thread.start()
    app.state.sender_thread = sender_thread

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        print("shutting down...")
        for train in control.trains.values():
            bridges.send(train.id, {"mI": 0})

    return app


def serve(*, port: int = DEFAULT_PORT, bridge: bool = False, debug: bool = False) -> None:
    """
    列車制御システムを Web サーバーとして起動する。
    `debug` を `True` にすると、ソースコードに変更があったときにリロードされる。
    """

    args = ServerArgs(port=port, bridge=bridge, debug=debug)

    os.environ["PTCS_SERVER_ARGS"] = args.json()

    if debug:
        uvicorn.run(
            "ptcs_server.server:create_app",
            factory=True,
            port=port,
            log_level="info",
            reload=True,
            reload_dirs=["ptcs_bridge", "ptcs_control", "ptcs_server"],
        )
    else:
        uvicorn.run(
            "ptcs_server.server:create_app",
            factory=True,
            port=port,
            log_level="info",
        )
