import click
from . import server


@click.command()
@click.option("--bridge", is_flag=True)
def main(bridge: bool) -> None:
    server.serve(bridge=bridge)


if __name__ == "__main__":
    main()
