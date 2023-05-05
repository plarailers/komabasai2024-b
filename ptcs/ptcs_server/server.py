from typing import Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from usb_bt_bridge import Bridge
from .bridges import BridgeManager, BridgeTarget
from ptcs_control import Control
from ptcs_control.components import Train
import uvicorn
from .api import api_router


def create_app() -> FastAPI:
    control = Control()

    app = FastAPI(generate_unique_id_function=lambda route: route.name)
    app.state.control = control

    # `/api` 以下で API を呼び出す
    app.include_router(api_router, prefix="/api")

    # `/` 以下で静的ファイルを配信する
    app.mount("/", StaticFiles(directory="./ptcs_ui/dist", html=True), name="static")

    return app


def create_app_with_bridge() -> FastAPI:
    app = create_app()
    control: Control = app.state.control

    def handle_receive(target: BridgeTarget, data: Any) -> None:
        print(target, data)
        # TODO: インターフェイスを定めてコマンドを判別する
        if data["pID"]:
            control.move_train(target, data["wR"] / 100)

    bridges = BridgeManager(callback=handle_receive)

    # TODO: ソースコードの変更なしに COM ポートを指定できるようにする
    bridges.register(Train("t0"), Bridge("COM4"))

    bridges.start()

    app.state.bridges = bridges

    return app


def serve(*, bridge: bool = False) -> None:
    """
    列車制御システムを Web サーバーとして起動する。
    """
    if bridge:
        uvicorn.run("ptcs_server.server:create_app_with_bridge", port=5000, log_level="info", reload=True)
    else:
        uvicorn.run("ptcs_server.server:create_app", port=5000, log_level="info", reload=True)
