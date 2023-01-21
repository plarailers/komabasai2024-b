from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from .api.router import router as api_router


app = FastAPI()

# `/api` 以下で API を呼び出す
api_app = FastAPI(title="API")
api_app.include_router(api_router)
app.mount("/api", api_app)

# `/` 以下で静的ファイルを配信する
app.mount("/", StaticFiles(directory="./ptcs_ui/dist", html=True), name="static")


def serve() -> None:
    """
    列車制御システムを Web サーバーとして起動する。
    """
    uvicorn.run("ptcs_server.server:app", port=5000, log_level="info", reload=True)
