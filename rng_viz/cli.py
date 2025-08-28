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

    def is_directory_path(p: Path) -> bool:
        """Check if path is intended to be a directory."""
        # If it exists and is a directory, obviously yes
        if p.exists() and p.is_dir():
            return True

        # If it ends with a slash, it's a directory
        path_str = str(p)
        if path_str.endswith("/") or path_str.endswith("\\"):
            return True

        # If it has no file extension and the name doesn't look like a filename, assume directory
        # Common directory patterns: captures, data, experiments, etc.
        if not p.suffix and not p.name.startswith("."):
            return True

        return False

    def generate_timestamped_filename() -> str:
        """Generate a unique timestamped filename."""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        microseconds = now.strftime("%f")[
            :3
        ]  # First 3 digits of microseconds (milliseconds)
        return f"rng_capture_{timestamp}-{microseconds}.csv"

    if is_directory_path(path):
        # This is intended to be a directory - create it if needed
        if not path.exists():
            click.echo(f"Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)

        # Generate timestamped filename in the directory
        filename = generate_timestamped_filename()
        resolved_path = path / filename
        click.echo(f"Auto-generating filename: {resolved_path}")
        return resolved_path
    else:
        # This looks like a specific file path
        if path.suffix:
            # Has file extension - definitely a file
            # Create parent directory if it doesn't exist
            if not path.parent.exists():
                click.echo(f"Creating parent directory: {path.parent}")
                path.parent.mkdir(parents=True, exist_ok=True)
            return path
        elif path.parent.exists():
            # Parent exists and no extension - treat as file in existing directory
            return path
        else:
            # Ambiguous case - ask for clarification
            if click.confirm(
                f"Path '{path}' is ambiguous. Treat as directory and auto-generate filename?"
            ):
                path.mkdir(parents=True, exist_ok=True)
                filename = generate_timestamped_filename()
                resolved_path = path / filename
                click.echo(
                    f"Created directory and auto-generating filename: {resolved_path}"
                )
                return resolved_path
            else:
                # Treat as file path - create parent directory if needed
                if not path.parent.exists():
                    click.echo(f"Creating parent directory: {path.parent}")
                    path.parent.mkdir(parents=True, exist_ok=True)
                return path


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
        rng-viz --live /path/to/captures/       # Auto-generate timestamped file (creates directory)
        rng-viz --live ./experiments/session1/  # Creates nested directories automatically
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
