"""Command-line interface for RNG Visualizer."""

from pathlib import Path

import click


@click.command()
@click.option(
    "--live",
    type=click.Path(path_type=Path),
    help="Start live capture mode, optionally saving to specified file path",
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
        rng-viz --live /path/to/save.csv        # Start live capture, save to file
        rng-viz --open /path/to/existing.csv    # Open existing capture file
    """
    # Import here to avoid loading heavy dependencies for --help
    from .ui.app import RNGVisualizerApp

    app = RNGVisualizerApp()

    if open_file:
        # Open existing file mode
        app.run_file_mode(open_file)
    elif live is not None:
        # Live capture mode
        app.run_live_mode(live, device_path=device)
    else:
        # Interactive mode selection
        app.run_interactive_mode(device_path=device)


if __name__ == "__main__":
    main()
