import click
from . import server


@click.group()
def cli() -> None:
    pass


@cli.command()
def hello() -> None:
    click.echo("hello")


@cli.command()
def serve() -> None:
    server.serve()


if __name__ == "__main__":
    cli()
