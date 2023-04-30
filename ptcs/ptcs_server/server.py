from typing import Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .bridges import BridgeManager, BridgeTarget
from ptcs_control import Control
import uvicorn
from .api import api_router


def handle_receive(target: BridgeTarget, data: Any) -> None:
    print(target, data)


def create_app() -> FastAPI:
    control = Control()
    bridges = BridgeManager(callback=handle_receive)

    bridges.start()

    app = FastAPI(generate_unique_id_function=lambda route: route.name)
    app.state.control = control
    app.state.bridges = bridges

    # `/api` 以下で API を呼び出す
    app.include_router(api_router, prefix="/api")

    # `/` 以下で静的ファイルを配信する
    app.mount("/", StaticFiles(directory="./ptcs_ui/dist", html=True), name="static")

    return app


def serve() -> None:
    """
    列車制御システムを Web サーバーとして起動する。
    """
    uvicorn.run("ptcs_server.server:create_app", port=5000, log_level="info", reload=True)
