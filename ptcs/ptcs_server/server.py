import asyncio
import logging
import os
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ptcs_bridge.master_controller_client import MasterControllerClient
from ptcs_bridge.point_client import PointClient
from ptcs_bridge.train_base import TrainBase
from ptcs_bridge.train_client import TrainClient
from ptcs_bridge.train_simulator import TrainSimulator
from ptcs_bridge.wire_pole_client import WirePoleClient
from ptcs_control.komabasai2024 import create_control

from .api import api_router
from .komabasai2024 import create_bridge

# NOTE: macOS では 5000 番ポートの使用を避ける
DEFAULT_PORT = 8000


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
    app = FastAPI(lifespan=lifespan, generate_unique_id_function=lambda route: route.name)
    return app


def handle_task_error(task: asyncio.Task):
    logger = logging.getLogger("uvicorn")
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Task failed with error: {e}")
        # KeyboardInterrupt にするとスタックトレースが出ないためここで表示
        traceback.print_exc()
        # サーバーを終了させるため KeyboardInterrupt として返す
        raise KeyboardInterrupt() from e


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger("uvicorn")

    args = get_server_args()
    logger.info("server args: %s", args)

    control = create_control(logger=logger)
    app.state.control = control

    # `/api` 以下で API を呼び出す
    app.include_router(api_router, prefix="/api")

    # `/` 以下で静的ファイルを配信する
    app.mount("/", StaticFiles(directory="./ptcs_ui/dist", html=True), name="static")

    bridge = create_bridge()
    app.state.bridge = bridge

    tasks: list[asyncio.Task] = []

    try:
        ready_queue: asyncio.Queue[None] = asyncio.Queue()  # 各タスクが ready になったら put
        ready_event = asyncio.Event()  # 全タスクが ready になったら notify

        async def control_loop():
            for _ in range(len(bridge.trains) + len(bridge.points)):
                await ready_queue.get()
            logger.info("All trains and points are ready")
            ready_event.set()

            while True:
                # control 内部の時計を現実世界の時間において進める
                await asyncio.sleep(0.1)
                control.tick()
                control.update()

        control_loop_task = asyncio.create_task(control_loop())
        control_loop_task.add_done_callback(handle_task_error)
        tasks.append(control_loop_task)

        async def train_loop(train_client: TrainBase):
            await train_client.connect()

            def handle_notify_position_uid(train_client: TrainBase, position_uid: str):
                train_control = control.trains.get(train_client.id)
                position = next(filter(lambda sp: sp.uid == position_uid, control.sensor_positions.values()), None)
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

            await train_client.start_notify_rotation(handle_notify_rotation)
            match train_client:
                case TrainClient():
                    await train_client.start_notify_position_uid(handle_notify_position_uid)
                    await train_client.start_notify_voltage(handle_notify_voltage)

            train_control = control.trains.get(train_client.id)
            if train_control is None:
                logger.warning(f"{train_client} has no corresponding train")
                return

            logger.info(f"{train_client} is ready")
            await ready_queue.put(None)
            await ready_event.wait()

            while True:
                await asyncio.sleep(0.2)
                match train_client:
                    case TrainSimulator():
                        await train_client.send_speed(train_control.speed_command)
                    case TrainClient():
                        motor_input = train_control.calc_input(train_control.speed_command)
                        await train_client.send_motor_input(motor_input)

        for train_id, train_client in bridge.trains.items():
            train_loop_task = asyncio.create_task(train_loop(train_client))
            train_loop_task.add_done_callback(handle_task_error)
            tasks.append(train_loop_task)

        async def point_loop(point_client: PointClient):
            await point_client.connect()

            junction_control = control.junctions.get(point_client.id)
            if junction_control is None:
                logger.warning(f"{point_client} has no corresponding junction")
                return

            logger.info(f"{point_client} is ready")
            await ready_queue.put(None)
            await ready_event.wait()

            while True:
                await asyncio.sleep(0.2)
                await point_client.send_direction(junction_control.current_direction)

        for point_id, point_client in bridge.points.items():
            point_loop_task = asyncio.create_task(point_loop(point_client))
            point_loop_task.add_done_callback(handle_task_error)
            tasks.append(point_loop_task)

        async def obstacle_loop(obstacle_client: WirePoleClient):
            await obstacle_client.connect()

            def handle_notify_collapse(obstacle_client: WirePoleClient, is_collapsed: bool):
                obstacle_control = control.obstacles.get(obstacle_client.id)
                if obstacle_control is None:
                    logger.warning(f"{obstacle_client} has no corresponding obstacle")
                    return
                obstacle_control.is_detected = is_collapsed

            await obstacle_client.start_notify_collapse(handle_notify_collapse)

        for obstacle_id, obstacle_client in bridge.obstacles.items():
            obstacle_loop_task = asyncio.create_task(obstacle_loop(obstacle_client))
            obstacle_loop_task.add_done_callback(handle_task_error)
            tasks.append(obstacle_loop_task)

        async def controller_loop(controller_client: MasterControllerClient):
            await controller_client.connect()

            def handle_notify_speed(controller_client: MasterControllerClient, speed: int):
                train_control = control.trains.get(controller_client.id)
                if train_control is None:
                    logger.warning(f"{controller_client} has no corresponding train")
                    return
                train_control.manual_speed = speed / 255 * train_control.max_speed

            await controller_client.start_notify_speed(handle_notify_speed)

        for controller_id, controller_client in bridge.controllers.items():
            controller_loop_task = asyncio.create_task(controller_loop(controller_client))
            controller_loop_task.add_done_callback(handle_task_error)
            tasks.append(controller_loop_task)

        # ここでサーバーのループが走る
        yield

    except asyncio.exceptions.CancelledError:
        pass

    finally:
        logger.info("Exiting...")

        for task in tasks:
            task.cancel()

        for train in bridge.trains.values():
            match train:
                case TrainSimulator():
                    await train.send_speed(0.0)
                case TrainClient():
                    if train.is_connected:
                        await train.send_motor_input(0)

        await bridge.disconnect_all()


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
