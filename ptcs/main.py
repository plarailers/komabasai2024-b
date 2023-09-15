import multiprocessing

import click
import webview

import ptcs_server.server


def start_server(*, bridge: bool = False, debug: bool = False):
    try:
        ptcs_server.server.serve(bridge=bridge, debug=debug)
    except KeyboardInterrupt:
        pass


def start_window(debug: bool = False):
    try:
        webview.create_window("Plarailers Train Control System", url="http://localhost:5000/")
        webview.start(debug=debug)
    except KeyboardInterrupt:
        pass


@click.command()
@click.option("--bridge", is_flag=True)
@click.option("--debug", is_flag=True)
def main(bridge: bool, debug: bool) -> None:
    server_process = multiprocessing.Process(
        target=start_server,
        kwargs={"bridge": bridge, "debug": debug},
        name="PTCS Server",
    )
    window_process = multiprocessing.Process(
        target=start_window,
        kwargs={"debug": debug},
        name="PTCS Window",
    )

    server_process.start()
    window_process.start()

    window_process.join()
    server_process.join()


if __name__ == "__main__":
    main()
