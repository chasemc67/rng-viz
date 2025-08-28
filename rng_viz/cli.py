"""Command-line interface for RNG Visualizer."""

from datetime import datetime
from pathlib import Path

import click


def resolve_capture_path(path: Path) -> Path:
    """Resolve the capture file path, auto-generating filename if directory provided.

    Args:
        path: Input path (file or directory)

    Returns:
        Resolved file path with timestamp if directory was provided

    Raises:
        click.ClickException: If path issues are encountered
    """
    if path.is_dir():
        # Generate timestamped filename in the directory
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        microseconds = now.strftime("%f")[
            :3
        ]  # First 3 digits of microseconds (milliseconds)
        filename = f"rng_capture_{timestamp}-{microseconds}.csv"
        resolved_path = path / filename
        click.echo(f"Auto-generating filename: {resolved_path}")
        return resolved_path
    elif path.parent.exists() or path.suffix:
        # Either parent directory exists, or it has a file extension (assume it's a file)
        return path
    else:
        # Path doesn't exist and no extension - could be intended as directory
        if click.confirm(
            f"Directory '{path}' doesn't exist. Create it and use auto-generated filename?"
        ):
            path.mkdir(parents=True, exist_ok=True)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            microseconds = now.strftime("%f")[
                :3
            ]  # First 3 digits of microseconds (milliseconds)
            filename = f"rng_capture_{timestamp}-{microseconds}.csv"
            resolved_path = path / filename
            click.echo(
                f"Created directory and auto-generating filename: {resolved_path}"
            )
            return resolved_path
        else:
            raise click.ClickException(f"Cannot resolve path: {path}")


@click.command()
@click.option(
    "--live",
    type=click.Path(path_type=Path),
    help="Start live capture mode, optionally saving to specified file or directory path",
)
@click.option(
    "--open",
    "open_file",
    type=click.Path(exists=True, path_type=Path),
    help="Open existing capture file for analysis",
)
@click.option(
    "--device",
    type=str,
    default=None,
    help="TrueRNG device path (auto-detect if not specified)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    live: Path | None,
    open_file: Path | None,
    device: str | None,
    verbose: bool,
) -> None:
    """TrueRNG Pro V2 bitstream analyzer and visualizer.

    Inspired by the Global Consciousness Project, this tool captures and analyzes
    random number streams to detect statistical deviations that may indicate
    consciousness-related anomalies.

    Examples:
        rng-viz --live                          # Start live capture with interactive mode selection
        rng-viz --live /path/to/save.csv        # Start live capture, save to specific file
        rng-viz --live /path/to/captures/       # Start live capture, auto-generate timestamped file
        rng-viz --open /path/to/existing.csv    # Open existing capture file
    """
    # Import here to avoid loading heavy dependencies for --help
    from .ui.app import RNGVisualizerApp

    app = RNGVisualizerApp()

    if open_file:
        # Open existing file mode
        app.run_file_mode(open_file)
    elif live is not None:
        # Live capture mode - resolve the path if provided
        resolved_live_path = None
        if live:  # If a path was provided (not just --live flag)
            resolved_live_path = resolve_capture_path(live)
        app.run_live_mode(resolved_live_path, device_path=device)
    else:
        # Interactive mode selection
        app.run_interactive_mode(device_path=device)


if __name__ == "__main__":
    main()
