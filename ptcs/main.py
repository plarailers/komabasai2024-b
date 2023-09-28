import logging
import multiprocessing
import subprocess

import click
import webview

import ptcs_server.server


def start_server(*, bridge: bool, debug: bool):
    try:
        ptcs_server.server.serve(bridge=bridge, debug=debug)
    except KeyboardInterrupt:
        pass


def start_window(*, port: int, debug: bool):
    try:
        webview.create_window("Plarailers Train Control System", url=f"http://localhost:{port}/")
        webview.start(debug=debug)
    except KeyboardInterrupt:
        pass


def start_ui_dev_server():
    try:
        subprocess.run(args=["npm", "run", "dev"], cwd="ptcs_ui")
    except KeyboardInterrupt:
        pass


@click.command()
@click.option("--bridge", is_flag=True)
@click.option("--debug", is_flag=True)
def main(bridge: bool, debug: bool) -> None:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)-8s]  %(message)s"))
    logger.addHandler(handler)

    UI_DEV_SERVER_PORT = 5173
    port = UI_DEV_SERVER_PORT if debug else ptcs_server.server.DEFAULT_PORT

    server_process = multiprocessing.Process(
        target=start_server,
        kwargs={"bridge": bridge, "debug": debug},
        name="PTCS Server",
    )
    server_process.start()
    logger.info("Process %s [%s] started", server_process.name, server_process.pid)

    if debug:
        ui_dev_server_process = multiprocessing.Process(
            target=start_ui_dev_server,
            name="PTCS UI Dev Server",
        )
        ui_dev_server_process.start()
        logger.info("Process %s [%s] started", ui_dev_server_process.name, ui_dev_server_process.pid)
    else:
        ui_dev_server_process = None

    window_process = multiprocessing.Process(
        target=start_window,
        kwargs={"port": port, "debug": debug},
        name="PTCS Window",
    )
    window_process.start()
    logger.info("Process %s [%s] started", window_process.name, window_process.pid)

    window_process.join()
    logger.info("Process %s [%s] terminated", window_process.name, window_process.pid)

    if ui_dev_server_process:
        ui_dev_server_process.terminate()
        logger.info("Process %s [%s] terminated", ui_dev_server_process.name, ui_dev_server_process.pid)

    server_process.join()
    logger.info("Process %s [%s] terminated", server_process.name, server_process.pid)


if __name__ == "__main__":
    main()
