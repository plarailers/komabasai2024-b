import logging
import threading
import time
from typing import Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from usb_bt_bridge import Bridge
from .bridges import BridgeManager, BridgeTarget
from .points import PointSwitcher, PointSwitcherManager
from .button import Button
from ptcs_control import Control
from ptcs_control.components import Position, Train, Junction, Section
import uvicorn
from .api import api_router


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)

    control = Control()

    # control 内部の時計を現実世界の時間において進める
    def run_clock() -> None:
        while True:
            time.sleep(1)
            control.tick()

    clock_thread = threading.Thread(target=run_clock, daemon=True)
    clock_thread.start()

    app = FastAPI(generate_unique_id_function=lambda route: route.name)
    app.state.control = control
    app.state.clock_thread = clock_thread

    # `/api` 以下で API を呼び出す
    app.include_router(api_router, prefix="/api")

    # `/` 以下で静的ファイルを配信する
    app.mount("/", StaticFiles(directory="./ptcs_ui/dist", html=True), name="static")

    return app


def create_app_with_bridge() -> FastAPI:
    app = create_app()
    control: Control = app.state.control

    # 列車からの信号
    def receive_from_train(train_id: BridgeTarget, data: Any) -> None:
        # モーター回転量
        if "mR" in data:
            control.move_train_mr(train_id, data["mR"])
        # APS 信号
        elif "pId" in data:
            control.put_train(train_id, bridges.get_position(data["pID"]))
        control.update()

    # 異常発生ボタンからの信号
    def receive_from_button(data: Any) -> None:
        s3 = Section("s3")
        if data["blocked"]:
            control.block_section(s3)
        else:
            control.unblock_section(s3)
        control.update()

    # すべての列車への信号
    def send_to_trains() -> None:
        for train_id, train_command in control.command.trains.items():
            train_config = control.config.trains[train_id]
            motor_input = train_config.calc_input(train_command.speed)
            bridges.send(train_id, {"mI": motor_input})

    # すべてのポイントへの信号
    def send_to_points() -> None:
        for junction_id, junction_state in control.state.junctions.items():
            point_switchers.send(junction_id, junction_state.direction)

    # TODO: ソースコードの変更なしに COM ポートを指定できるようにする

    # 列車
    bridges = BridgeManager(callback=receive_from_train)
    bridges.register(Train("t0"), Bridge("/dev/tty.usbserial-AC01UECP"))
    bridges.register_position(Position("position_0"), 173)
    bridges.register_position(Position("position_1"), 255)
    bridges.register_position(Position("position_2"), 80)
    bridges.start()
    app.state.bridges = bridges

    # ポイント
    point_switchers = PointSwitcherManager()
    point_switcher = PointSwitcher("/dev/tty.usbserial-1140")
    point_switchers.register(Junction("j0a"), point_switcher, 0)
    point_switchers.register(Junction("j0b"), point_switcher, 1)
    point_switchers.register(Junction("j1a"), point_switcher, 2)
    point_switchers.register(Junction("j1b"), point_switcher, 3)
    point_switchers.start()
    app.state.point_switchers = point_switchers

    # 異常発生ボタン
    button = Button("/dev/tty.usbserial-1130", callback=receive_from_button)
    button.start()
    app.state.button = button

    return app


def serve(*, bridge: bool = False) -> None:
    """
    列車制御システムを Web サーバーとして起動する。
    """
    if bridge:
        uvicorn.run("ptcs_server.server:create_app_with_bridge", port=5000, log_level="info", reload=True)
    else:
        uvicorn.run("ptcs_server.server:create_app", port=5000, log_level="info", reload=True)
