"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Driva Python Sdk."""


if __name__ == "__main__":
    main(prog_name="driva-python-sdk")  # pragma: no cover
