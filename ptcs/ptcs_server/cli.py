import click

from . import server


@click.command()
@click.option("--bridge", is_flag=True)
@click.option("--debug", is_flag=True)
def main(bridge: bool, debug: bool) -> None:
    server.serve(bridge=bridge, debug=debug)


if __name__ == "__main__":
    main()
