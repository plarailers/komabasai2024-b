import click
from . import server


@click.command()
def main() -> None:
    server.serve()


if __name__ == "__main__":
    main()
