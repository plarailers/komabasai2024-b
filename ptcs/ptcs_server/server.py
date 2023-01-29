from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ptcs_control import Control
import uvicorn
from .api.router import router as api_router


control = Control()

app = FastAPI()
app.state.control = control

# `/api` 以下で API を呼び出す
app.include_router(api_router, prefix="/api")

# `/` 以下で静的ファイルを配信する
app.mount("/", StaticFiles(directory="./ptcs_ui/dist", html=True), name="static")


def serve() -> None:
    """
    列車制御システムを Web サーバーとして起動する。
    """
    uvicorn.run("ptcs_server.server:app", port=5000, log_level="info", reload=True)
