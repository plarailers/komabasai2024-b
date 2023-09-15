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


@click.command()
@click.option("--bridge", is_flag=True)
@click.option("--debug", is_flag=True)
def main(bridge: bool, debug: bool) -> None:
    UI_DEV_SERVER_PORT = 5173
    port = UI_DEV_SERVER_PORT if debug else ptcs_server.server.DEFAULT_PORT

    server_process = multiprocessing.Process(
        target=start_server,
        kwargs={"bridge": bridge, "debug": debug},
        name="PTCS Server",
    )
    server_process.start()

    if debug:
        ui_dev_server_process = subprocess.Popen(
            args=["npm", "run", "dev"],
            cwd="ptcs_ui",
        )
    else:
        ui_dev_server_process = None

    window_process = multiprocessing.Process(
        target=start_window,
        kwargs={"port": port, "debug": debug},
        name="PTCS Window",
    )
    window_process.start()

    window_process.join()

    if ui_dev_server_process:
        ui_dev_server_process.wait()

    server_process.join()


if __name__ == "__main__":
    main()
