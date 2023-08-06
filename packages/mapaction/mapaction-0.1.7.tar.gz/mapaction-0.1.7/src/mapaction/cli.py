from typing import Optional

import pkg_resources
import typer

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(pkg_resources.get_distribution("mapaction"))
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


def run() -> None:
    """Run commands."""
    print("--- test ---")
    app()
