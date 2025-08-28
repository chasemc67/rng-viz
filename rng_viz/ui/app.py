"""Main Textual application for RNG Visualizer."""

import asyncio
import random
import signal
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Label, Static

from ..analysis.stats import AnomalyResult, RandomnessAnalyzer
from ..data.storage import (
    BitstreamReader,
    BitstreamRecord,
    BitstreamWriter,
    create_capture_metadata,
)
from ..device.truerng import TrueRNGDevice


@dataclass
class BucketScores:
    """Scores for one turn's anomaly buckets."""

    red_up: int = 0  # *** + positive z_score
    orange_up: int = 0  # ** + positive z_score
    yellow_up: int = 0  # * + positive z_score
    red_down: int = 0  # *** + negative z_score
    orange_down: int = 0  # ** + negative z_score
    yellow_down: int = 0  # * + negative z_score

    def total_up(self) -> int:
        """Total up anomalies."""
        return self.red_up + self.orange_up + self.yellow_up

    def total_down(self) -> int:
        """Total down anomalies."""
        return self.red_down + self.orange_down + self.yellow_down

    def total(self) -> int:
        """Total anomalies."""
        return self.total_up() + self.total_down()


@dataclass
class GameTurn:
    """Represents one turn of the game."""

    instruction: str  # "Generate more 1's" or "Generate more 0's"
    duration: float  # Turn duration in seconds
    start_time: float = field(default_factory=time.time)
    scores: BucketScores = field(default_factory=BucketScores)

    def is_expired(self) -> bool:
        """Check if this turn has expired."""
        return time.time() - self.start_time >= self.duration

    def time_remaining(self) -> float:
        """Get time remaining in this turn."""
        return max(0, self.duration - (time.time() - self.start_time))


@dataclass
class GameState:
    """Manages the overall game state."""

    current_turn: GameTurn | None = None
    turn_history: list[GameTurn] = field(default_factory=list)
    is_finished: bool = False

    def start_new_turn(self) -> GameTurn:
        """Start a new game turn."""
        # Randomly choose instruction and duration
        instruction = random.choice(["Generate more 1's", "Generate more 0's"])
        duration = random.uniform(10.0, 30.0)

        # End current turn if exists
        if self.current_turn:
            self.turn_history.append(self.current_turn)

        # Start new turn
        self.current_turn = GameTurn(instruction=instruction, duration=duration)
        return self.current_turn

    def add_anomaly(self, anomaly: AnomalyResult) -> None:
        """Add an anomaly to the current turn's scores."""
        if not self.current_turn or self.is_finished:
            return

        scores = self.current_turn.scores

        # Determine direction based on z_score
        is_up = anomaly.z_score > 0

        # Categorize by significance level and direction
        if anomaly.significance_level == "***":
            if is_up:
                scores.red_up += 1
            else:
                scores.red_down += 1
        elif anomaly.significance_level == "**":
            if is_up:
                scores.orange_up += 1
            else:
                scores.orange_down += 1
        elif anomaly.significance_level == "*":
            if is_up:
                scores.yellow_up += 1
            else:
                scores.yellow_down += 1

    def finish_game(self) -> None:
        """Finish the game and add current turn to history."""
        if self.current_turn:
            self.turn_history.append(self.current_turn)
            self.current_turn = None
        self.is_finished = True

    def get_overall_stats(self) -> BucketScores:
        """Get combined statistics across all turns."""
        total = BucketScores()
        for turn in self.turn_history:
            total.red_up += turn.scores.red_up
            total.orange_up += turn.scores.orange_up
            total.yellow_up += turn.scores.yellow_up
            total.red_down += turn.scores.red_down
            total.orange_down += turn.scores.orange_down
            total.yellow_down += turn.scores.yellow_down
        return total


class BitstreamVisualizer(Static):
    """Widget for visualizing the bitstream as a scrolling wave."""

    def __init__(self, width: int = 80, height: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.data_points: list[float] = [0.0] * width
        self.anomaly_points: list[str | None] = [None] * width
        self.position = 0

    def add_data_point(self, value: float, anomaly: str | None = None) -> None:
        """Add a new data point to the visualization.

        Args:
            value: Normalized value (-1 to 1, where 0 is baseline)
            anomaly: Anomaly significance marker if present
        """
        self.data_points.append(value)
        self.anomaly_points.append(anomaly)

        # Keep only the latest width points
        if len(self.data_points) > self.width:
            self.data_points.pop(0)
            self.anomaly_points.pop(0)

        self.position += 1
        self.refresh()

    def render(self) -> Panel:
        """Render the bitstream visualization."""
        lines = []

        # Create the wave visualization
        mid_line = self.height // 2

        for row in range(self.height):
            line_chars = []

            for col, (value, anomaly) in enumerate(
                zip(self.data_points, self.anomaly_points, strict=False)
            ):
                # Convert value (-1 to 1) to row position
                value_row = mid_line - int(value * mid_line)

                if row == value_row:
                    if anomaly:
                        # Use different characters for different significance levels
                        char = "▲" if value > 0 else "▼"
                        if anomaly == "***":
                            char = f"[bold red]{char}[/bold red]"
                        elif anomaly == "**":
                            char = f"[bold yellow]{char}[/bold yellow]"
                        elif anomaly == "*":
                            char = f"[yellow]{char}[/yellow]"
                    else:
                        char = "━"
                elif row == mid_line:
                    char = "─"  # Baseline
                else:
                    char = " "

                line_chars.append(char)

            lines.append("".join(line_chars))

        content = "\n".join(lines)
        return Panel(
            content,
            title="RNG Bitstream Visualization",
            subtitle=f"Position: {self.position}",
        )


class StatsDisplay(Static):
    """Widget for displaying statistical information."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = {}

    def update_stats(self, stats: dict) -> None:
        """Update displayed statistics."""
        self.stats = stats
        self.refresh()

    def render(self) -> Panel:
        """Render the statistics display."""
        if not self.stats:
            content = "Waiting for data..."
        else:
            lines = [
                f"Total Bits: {self.stats.get('total_bits', 0):,}",
                f"Ones Ratio: {self.stats.get('ones_ratio', 0):.4f}",
                f"Byte Mean: {self.stats.get('byte_mean', 0):.2f}",
                f"Byte Std: {self.stats.get('byte_std', 0):.2f}",
                f"Anomalies: {self.stats.get('total_anomalies', 0)}",
                f"Position: {self.stats.get('current_position', 0):,}",
            ]
            content = "\n".join(lines)

        return Panel(content, title="Statistics")


class DeviceStatus(Static):
    """Widget for displaying device status."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device_info = {}

    def update_device_info(self, device_info: dict) -> None:
        """Update device information."""
        self.device_info = device_info
        self.refresh()

    def render(self) -> Panel:
        """Render device status."""
        if not self.device_info:
            content = "No device connected"
        else:
            status = (
                "🟢 Connected"
                if self.device_info.get("connected")
                else "🔴 Disconnected"
            )
            lines = [
                f"Status: {status}",
                f"Port: {self.device_info.get('port', 'Unknown')}",
                f"Mode: {self.device_info.get('mode', 'Unknown')}",
            ]
            content = "\n".join(lines)

        return Panel(content, title="Device Status")


class GameInstructionDisplay(Static):
    """Widget for displaying current game instruction and timer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state: GameState | None = None

    def update_game_state(self, game_state: GameState) -> None:
        """Update game state."""
        self.game_state = game_state
        self.refresh()

    def render(self) -> Panel:
        """Render game instruction and timer."""
        if not self.game_state or not self.game_state.current_turn:
            if self.game_state and self.game_state.is_finished:
                content = "[bold green]🎯 Game Finished![/bold green]\n\nPress F to view final results"
            else:
                content = "Game starting..."
        else:
            turn = self.game_state.current_turn
            time_left = turn.time_remaining()

            # Color-code the instruction
            if "1's" in turn.instruction:
                instruction_color = "[bold cyan]"
            else:
                instruction_color = "[bold magenta]"

            content = f"{instruction_color}{turn.instruction}[/{instruction_color.split('[')[1]}]\n"
            content += f"⏰ Time left: {time_left:.1f}s"

        return Panel(content, title="🎯 Game Instructions")


class CurrentBucketDisplay(Static):
    """Widget for displaying current turn's bucket scores."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state: GameState | None = None

    def update_game_state(self, game_state: GameState) -> None:
        """Update game state."""
        self.game_state = game_state
        self.refresh()

    def render(self) -> Panel:
        """Render current bucket scores."""
        if not self.game_state or not self.game_state.current_turn:
            content = "No active turn"
        else:
            scores = self.game_state.current_turn.scores
            lines = [
                f"[bold red]Red ▲: {scores.red_up}    Red ▼: {scores.red_down}[/bold red]",
                f"[bold yellow]Org ▲: {scores.orange_up}    Org ▼: {scores.orange_down}[/bold yellow]",
                f"[yellow]Yel ▲: {scores.yellow_up}    Yel ▼: {scores.yellow_down}[/yellow]",
                "",
                f"Total ▲: {scores.total_up()}  Total ▼: {scores.total_down()}",
                f"[bold]Total: {scores.total()}[/bold]",
            ]
            content = "\n".join(lines)

        return Panel(content, title="📊 Current Turn", style="bold")


class GameHistoryDisplay(Static):
    """Widget for displaying game turn history."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state: GameState | None = None

    def update_game_state(self, game_state: GameState) -> None:
        """Update game state."""
        self.game_state = game_state
        self.refresh()

    def render(self) -> Panel:
        """Render turn history."""
        if not self.game_state or not self.game_state.turn_history:
            content = "No completed turns yet"
        else:
            lines = []
            for i, turn in enumerate(
                self.game_state.turn_history[-10:], 1
            ):  # Show last 10 turns
                scores = turn.scores
                instruction_short = "1's" if "1's" in turn.instruction else "0's"
                lines.append(
                    f"Turn {i}: {instruction_short} → "
                    f"▲{scores.total_up()} ▼{scores.total_down()}"
                )

            if len(self.game_state.turn_history) > 10:
                lines.insert(
                    0, f"(Showing last 10 of {len(self.game_state.turn_history)} turns)"
                )

            content = "\n".join(lines)

        return Panel(content, title="📈 Turn History")


class GameOverallStats(Static):
    """Widget for displaying overall game statistics."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state: GameState | None = None

    def update_game_state(self, game_state: GameState) -> None:
        """Update game state."""
        self.game_state = game_state
        self.refresh()

    def render(self) -> Panel:
        """Render overall statistics."""
        if not self.game_state:
            content = "No game data"
        else:
            total_stats = self.game_state.get_overall_stats()
            total_turns = len(self.game_state.turn_history)

            lines = [
                f"[bold]Total Turns: {total_turns}[/bold]",
                "",
                f"[bold red]Red ▲: {total_stats.red_up}    Red ▼: {total_stats.red_down}[/bold red]",
                f"[bold yellow]Org ▲: {total_stats.orange_up}    Org ▼: {total_stats.orange_down}[/bold yellow]",
                f"[yellow]Yel ▲: {total_stats.yellow_up}    Yel ▼: {total_stats.yellow_down}[/yellow]",
                "",
                f"[bold]Total ▲: {total_stats.total_up()}[/bold]",
                f"[bold]Total ▼: {total_stats.total_down()}[/bold]",
                f"[bold green]Grand Total: {total_stats.total()}[/bold green]",
            ]

            # Add some analysis
            if total_stats.total() > 0:
                up_percentage = (total_stats.total_up() / total_stats.total()) * 100
                lines.extend(["", f"Up bias: {up_percentage:.1f}%"])

            content = "\n".join(lines)

        return Panel(content, title="🏆 Overall Results")


class RNGVisualizerApp(App):
    """Main application for RNG visualization."""

    CSS = """
    Screen {
        layout: vertical;
    }
    
    #main_container {
        layout: horizontal;
        height: 1fr;
    }
    
    #left_panel {
        width: 1fr;
        layout: vertical;
    }
    
    #right_panel {
        width: 30;
        layout: vertical;
    }
    
    #visualizer {
        height: 15;
    }
    
    #controls {
        height: 10;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save"),
        ("p", "pause", "Pause"),
        ("r", "resume", "Resume"),
        ("f", "finish_game", "Finish Game"),
    ]

    def __init__(self):
        super().__init__()
        self.device: TrueRNGDevice | None = None
        self.analyzer: RandomnessAnalyzer | None = None
        self.writer: BitstreamWriter | None = None
        self.reader: BitstreamReader | None = None
        self.is_live_mode = False
        self.is_game_mode = False
        self.is_paused = False
        self.capture_task: asyncio.Task | None = None
        self._shutting_down = False

        # Game state
        self.game_state: GameState | None = None
        self.game_timer_task: asyncio.Task | None = None

        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()

        with Container(id="main_container"):
            with Vertical(id="left_panel"):
                yield BitstreamVisualizer(id="visualizer")

                with Container(id="controls"):
                    if self.is_game_mode:
                        yield Label(
                            "[bold red]Press \\[Q] to Quit or Ctrl+C[/bold red] | \\[S]tatus | \\[P]ause | \\[R]esume | \\[F]inish Game",
                            markup=True,
                        )
                    else:
                        yield Label(
                            "[bold red]Press \\[Q] to Quit or Ctrl+C[/bold red] | \\[S]tatus | \\[P]ause | \\[R]esume",
                            markup=True,
                        )

            with Vertical(id="right_panel"):
                yield DeviceStatus(id="device_status")
                yield StatsDisplay(id="stats_display")

                # Game-specific components
                if self.is_game_mode:
                    yield GameInstructionDisplay(id="game_instruction")
                    yield CurrentBucketDisplay(id="current_bucket")
                    yield GameHistoryDisplay(id="game_history")

        yield Footer()

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            """Handle shutdown signals."""
            if not self._shutting_down:
                # Schedule the cleanup in the event loop
                if hasattr(self, "_loop") and self._loop and not self._loop.is_closed():
                    asyncio.create_task(self._graceful_shutdown())
                else:
                    # Fallback for immediate shutdown
                    self._emergency_cleanup()
                    sys.exit(0)

        # Set up signal handlers for Ctrl+C and other termination signals
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.title = "RNG Visualizer"
        self.sub_title = "TrueRNG Pro V2 Bitstream Analyzer"
        # Store reference to event loop for signal handling
        self._loop = asyncio.get_event_loop()

    async def action_quit(self) -> None:
        """Quit the application."""
        await self._graceful_shutdown()

    async def _graceful_shutdown(self) -> None:
        """Perform graceful shutdown with status updates."""
        if self._shutting_down:
            return  # Already shutting down

        self._shutting_down = True
        self.notify("Shutting down... Please wait.", title="Stopping Capture")

        try:
            await self.cleanup()
            self.notify(
                "Shutdown complete. Data saved safely.", title="Shutdown Complete"
            )
        except Exception as e:
            self.notify(f"Error during shutdown: {e}", severity="warning")
        finally:
            self.exit()

    async def action_save(self) -> None:
        """Show current save status and file information."""
        if self.writer:
            try:
                stats = self.analyzer.get_summary_stats() if self.analyzer else {}
                records_written = getattr(self.writer, "records_written", 0)
                filename = self.writer.filepath.name

                message = f"File: {filename}\nRecords: {records_written:,}\nPosition: {stats.get('current_position', 0):,}"
                self.notify(message, title="💾 Save Status - Auto-saving Active")
            except Exception:
                self.notify("Auto-saving active to file", title="💾 Save Status")
        else:
            if self.is_live_mode:
                self.notify(
                    "No file saving - restart with: rng-viz --live ./path/",
                    severity="warning",
                    title="💾 Save Status",
                )
            else:
                self.notify(
                    "File playback mode - no saving needed", title="💾 Save Status"
                )

    async def action_pause(self) -> None:
        """Pause data capture or playback."""
        self.is_paused = True
        mode_text = "playback" if not self.is_live_mode else "data capture"
        self.notify(f"{mode_text.title()} paused - press R to resume", title="⏸️ Paused")

    async def action_resume(self) -> None:
        """Resume data capture or playback."""
        self.is_paused = False
        mode_text = "playback" if not self.is_live_mode else "data capture"
        self.notify(f"{mode_text.title()} resumed", title="▶️ Resumed")

    async def action_finish_game(self) -> None:
        """Finish the current game and show overall statistics."""
        if not self.is_game_mode or not self.game_state:
            self.notify("Not in game mode", severity="warning")
            return

        # Finish the game
        self.game_state.finish_game()

        # Update all game widgets
        self._update_game_widgets()

        # Show completion notification
        self.notify(
            "Game finished! Overall statistics displayed.", title="🏆 Game Complete"
        )

    def run_live_mode(
        self, save_path: Path | None = None, device_path: str | None = None
    ) -> None:
        """Run in live capture mode."""
        self.is_live_mode = True

        async def setup_live():
            try:
                # Initialize device
                self.device = TrueRNGDevice(port=device_path)
                await asyncio.get_event_loop().run_in_executor(
                    None, self.device.connect
                )

                # Initialize analyzer
                self.analyzer = RandomnessAnalyzer(window_size=1000, sensitivity=0.01)

                # Initialize writer if save path provided
                if save_path:
                    metadata = create_capture_metadata(
                        device_info=self.device.get_status(),
                        window_size=1000,
                        sensitivity=0.01,
                    )
                    self.writer = BitstreamWriter(save_path, metadata)
                    self.writer.__enter__()

                # Update device status
                device_status = self.query_one("#device_status", DeviceStatus)
                device_status.update_device_info(self.device.get_status())

                # Start capture task
                self.capture_task = asyncio.create_task(self._capture_loop())

            except Exception as e:
                error_msg = f"Error setting up live mode: {e}"
                print(f"❌ {error_msg}")  # Always print to console

                # Also try to notify through UI if available
                try:
                    self.notify(error_msg, severity="error")
                except:
                    pass  # UI might not be ready yet

                # Keep the app running to show the error
                if "Permission denied" in str(e):
                    print("\n💡 Fix: Add your user to the dialout group:")
                    print("   sudo usermod -a -G dialout $USER")
                    print("   Then logout and login again")
                    print("\nOr try: sudo chmod 666 /dev/ttyACM0")

        # Schedule the setup
        self.call_later(setup_live)

        # Start the Textual application
        self.run()

    def run_file_mode(self, file_path: Path) -> None:
        """Run in file viewing mode."""
        self.is_live_mode = False

        async def setup_file():
            try:
                self.reader = BitstreamReader(file_path)
                metadata = self.reader.load_metadata()

                # Show file info
                self.notify(f"Loaded file: {file_path.name}")

                # Start playback task (similar to capture task in live mode)
                self.capture_task = asyncio.create_task(self._playback_loop())

            except Exception as e:
                error_msg = f"Error loading file: {e}"
                print(f"❌ {error_msg}")  # Always print to console

                # Also try to notify through UI if available
                try:
                    self.notify(error_msg, severity="error")
                except:
                    pass  # UI might not be ready yet

        self.call_later(setup_file)

        # Start the Textual application
        self.run()

    def run_game_mode(
        self, save_path: Path | None = None, device_path: str | None = None
    ) -> None:
        """Run in game mode."""
        self.is_live_mode = True
        self.is_game_mode = True
        self.game_state = GameState()

        async def setup_game():
            try:
                # Initialize device (same as live mode)
                self.device = TrueRNGDevice(port=device_path)
                await asyncio.get_event_loop().run_in_executor(
                    None, self.device.connect
                )

                # Initialize analyzer
                self.analyzer = RandomnessAnalyzer(window_size=1000, sensitivity=0.01)

                # Initialize writer if save path provided
                if save_path:
                    metadata = create_capture_metadata(
                        device_info=self.device.get_status(),
                        window_size=1000,
                        sensitivity=0.01,
                    )
                    self.writer = BitstreamWriter(save_path, metadata)
                    self.writer.__enter__()

                # Update device status
                device_status = self.query_one("#device_status", DeviceStatus)
                device_status.update_device_info(self.device.get_status())

                # Start first game turn
                self.game_state.start_new_turn()

                # Start game timer task
                self.game_timer_task = asyncio.create_task(self._game_timer_loop())

                # Start capture task
                self.capture_task = asyncio.create_task(self._game_capture_loop())

            except Exception as e:
                error_msg = f"Error setting up game mode: {e}"
                print(f"❌ {error_msg}")  # Always print to console

                # Also try to notify through UI if available
                try:
                    self.notify(error_msg, severity="error")
                except:
                    pass  # UI might not be ready yet

                # Keep the app running to show the error
                if "Permission denied" in str(e):
                    print("\n💡 Fix: Add your user to the dialout group:")
                    print("   sudo usermod -a -G dialout $USER")
                    print("   Then logout and login again")
                    print("\nOr try: sudo chmod 666 /dev/ttyACM0")

        # Schedule the setup
        self.call_later(setup_game)

        # Start the Textual application
        self.run()

    def run_game_file_mode(self, file_path: Path) -> None:
        """Run in game file replay mode."""
        self.is_live_mode = False
        self.is_game_mode = True
        self.game_state = GameState()

        async def setup_game_file():
            try:
                self.reader = BitstreamReader(file_path)
                metadata = self.reader.load_metadata()

                # Show file info
                self.notify(f"Loaded game file: {file_path.name}")

                # Start playback task
                self.capture_task = asyncio.create_task(self._game_playback_loop())

            except Exception as e:
                error_msg = f"Error loading game file: {e}"
                print(f"❌ {error_msg}")  # Always print to console

                # Also try to notify through UI if available
                try:
                    self.notify(error_msg, severity="error")
                except:
                    pass  # UI might not be ready yet

        self.call_later(setup_game_file)

        # Start the Textual application
        self.run()

    def run_interactive_mode(self, device_path: str | None = None) -> None:
        """Run in interactive mode selection."""
        # For now, default to live mode
        # In a full implementation, this would show a selection screen
        self.run_live_mode(device_path=device_path)

    async def _capture_loop(self) -> None:
        """Main capture loop for live mode."""
        if not self.device or not self.analyzer:
            return

        visualizer = self.query_one("#visualizer", BitstreamVisualizer)
        stats_display = self.query_one("#stats_display", StatsDisplay)

        # Counter to throttle visualization updates
        viz_update_counter = 0
        viz_update_frequency = (
            10  # Only update visualization every 10th byte (2x slower)
        )

        try:
            for chunk in self.device.stream_bytes(chunk_size=10):  # Smaller chunks
                # Check for shutdown or pause
                if self._shutting_down:
                    break
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue

                for byte_val in chunk:
                    # Analyze byte for anomalies
                    anomalies = self.analyzer.add_byte(byte_val)

                    # Calculate visualization value
                    # Convert byte value to normalized range (-1 to 1)
                    viz_value = (byte_val - 127.5) / 127.5

                    # Check for anomalies
                    anomaly_marker = None
                    if anomalies:
                        # Use the most significant anomaly
                        strongest = max(anomalies, key=lambda a: abs(a.z_score))
                        anomaly_marker = strongest.significance_level
                        viz_value = (
                            strongest.z_score / 5.0
                        )  # Scale z-score for visualization
                        viz_value = max(-1, min(1, viz_value))  # Clamp to [-1, 1]

                    # Only update visualization every few bytes to slow down scrolling
                    viz_update_counter += 1
                    if viz_update_counter >= viz_update_frequency:
                        # Update visualization
                        visualizer.add_data_point(viz_value, anomaly_marker)

                        # Update statistics less frequently too
                        stats = self.analyzer.get_summary_stats()
                        stats_display.update_stats(stats)

                        viz_update_counter = 0  # Reset counter

                    # Save to file if writer available
                    if self.writer:
                        record = BitstreamRecord(
                            position=self.analyzer.position,
                            timestamp=time.time(),
                            byte_value=byte_val,
                            anomaly_type=anomalies[0].test_type if anomalies else None,
                            z_score=anomalies[0].z_score if anomalies else None,
                            p_value=anomalies[0].p_value if anomalies else None,
                            significance=anomalies[0].significance_level
                            if anomalies
                            else None,
                        )
                        self.writer.write_record(record)

                # Small delay to control update rate (more frequent but shorter delays)
                await asyncio.sleep(
                    0.02
                )  # Shorter delay since we're processing smaller chunks

        except Exception as e:
            self.notify(f"Capture error: {e}", severity="error")

    async def _playback_loop(self) -> None:
        """Playback loop for file mode."""
        if not self.reader:
            return

        visualizer = self.query_one("#visualizer", BitstreamVisualizer)
        stats_display = self.query_one("#stats_display", StatsDisplay)

        # Counter to throttle visualization updates (same as live mode)
        viz_update_counter = 0
        viz_update_frequency = 10  # Same throttling as live mode

        try:
            position = 0
            for record in self.reader.iter_records():
                # Check for shutdown or pause
                if self._shutting_down:
                    break
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue

                # Calculate visualization value
                viz_value = (record.byte_value - 127.5) / 127.5

                # Use recorded anomaly data
                anomaly_marker = record.significance
                if record.z_score is not None:
                    viz_value = record.z_score / 5.0
                    viz_value = max(-1, min(1, viz_value))

                # Only update visualization every few records to match live mode speed
                viz_update_counter += 1
                if viz_update_counter >= viz_update_frequency:
                    # Update visualization
                    visualizer.add_data_point(viz_value, anomaly_marker)

                    # Create stats display
                    position += 1
                    stats = {
                        "current_position": position,
                        "total_bits": position * 8,
                        "ones_ratio": 0.5,  # Would calculate from data
                        "byte_mean": record.byte_value,
                        "byte_std": 0.0,
                        "total_anomalies": 1 if record.anomaly_type else 0,
                    }
                    stats_display.update_stats(stats)

                    viz_update_counter = 0  # Reset counter

                # Control playback speed (match live mode timing)
                await asyncio.sleep(0.02)  # Same timing as live mode

        except Exception as e:
            self.notify(f"Playback error: {e}", severity="error")

    async def cleanup(self) -> None:
        """Clean up resources with detailed status updates."""
        cleanup_steps = []

        if self.capture_task and not self.capture_task.done():
            cleanup_steps.append("Stopping data capture...")
            self.capture_task.cancel()
            try:
                await asyncio.wait_for(self.capture_task, timeout=2.0)
            except (TimeoutError, asyncio.CancelledError):
                pass  # Expected when cancelling

        if self.game_timer_task and not self.game_timer_task.done():
            cleanup_steps.append("Stopping game timer...")
            self.game_timer_task.cancel()
            try:
                await asyncio.wait_for(self.game_timer_task, timeout=1.0)
            except (TimeoutError, asyncio.CancelledError):
                pass  # Expected when cancelling

        if self.device and self.device.is_connected:
            cleanup_steps.append("Disconnecting from device...")
            self.device.disconnect()

        if self.writer:
            cleanup_steps.append("Closing capture file...")
            try:
                self.writer.__exit__(None, None, None)
                cleanup_steps.append("✓ Capture file saved successfully")
            except Exception as e:
                cleanup_steps.append(f"⚠ Error closing file: {e}")

        # Show cleanup progress if we have UI
        if hasattr(self, "notify") and cleanup_steps:
            for step in cleanup_steps:
                if step.startswith("✓") or step.startswith("⚠"):
                    self.notify(step)

    def _emergency_cleanup(self) -> None:
        """Emergency cleanup for immediate shutdown (no async)."""
        try:
            if self.device and self.device.is_connected:
                self.device.disconnect()
        except:
            pass

        try:
            if self.writer:
                self.writer.__exit__(None, None, None)
        except:
            pass

    def _update_game_widgets(self) -> None:
        """Update all game-related widgets with current state."""
        if not self.game_state:
            return

        try:
            # Update instruction display
            instruction_display = self.query_one(
                "#game_instruction", GameInstructionDisplay
            )
            instruction_display.update_game_state(self.game_state)

            # Update current bucket display
            bucket_display = self.query_one("#current_bucket", CurrentBucketDisplay)
            bucket_display.update_game_state(self.game_state)

            # Update history display
            history_display = self.query_one("#game_history", GameHistoryDisplay)
            history_display.update_game_state(self.game_state)
        except Exception:
            # Widgets might not be initialized yet
            pass

    async def _game_timer_loop(self) -> None:
        """Timer loop for managing game turns."""
        while (
            not self._shutting_down
            and self.game_state
            and not self.game_state.is_finished
        ):
            if self.is_paused:
                await asyncio.sleep(0.1)
                continue

            current_turn = self.game_state.current_turn
            if current_turn and current_turn.is_expired():
                # Start new turn
                self.game_state.start_new_turn()
                self._update_game_widgets()

            # Update UI frequently to show countdown
            self._update_game_widgets()
            await asyncio.sleep(0.1)  # Update 10 times per second

    async def _game_capture_loop(self) -> None:
        """Game capture loop - same as normal capture but with game logic."""
        if not self.device or not self.analyzer:
            return

        visualizer = self.query_one("#visualizer", BitstreamVisualizer)
        stats_display = self.query_one("#stats_display", StatsDisplay)

        # Counter to throttle visualization updates
        viz_update_counter = 0
        viz_update_frequency = 10  # Same as normal mode

        try:
            for chunk in self.device.stream_bytes(chunk_size=10):
                # Check for shutdown or pause
                if self._shutting_down:
                    break
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue

                for byte_val in chunk:
                    # Analyze byte for anomalies
                    anomalies = self.analyzer.add_byte(byte_val)

                    # Add anomalies to game state
                    for anomaly in anomalies:
                        if self.game_state:
                            self.game_state.add_anomaly(anomaly)

                    # Calculate visualization value (same as normal mode)
                    viz_value = (byte_val - 127.5) / 127.5

                    # Check for anomalies
                    anomaly_marker = None
                    if anomalies:
                        strongest = max(anomalies, key=lambda a: abs(a.z_score))
                        anomaly_marker = strongest.significance_level
                        viz_value = strongest.z_score / 5.0
                        viz_value = max(-1, min(1, viz_value))

                    # Only update visualization every few bytes
                    viz_update_counter += 1
                    if viz_update_counter >= viz_update_frequency:
                        # Update visualization
                        visualizer.add_data_point(viz_value, anomaly_marker)

                        # Update statistics
                        stats = self.analyzer.get_summary_stats()
                        stats_display.update_stats(stats)

                        # Update game widgets
                        self._update_game_widgets()

                        viz_update_counter = 0

                    # Save to file if writer available
                    if self.writer:
                        record = BitstreamRecord(
                            position=self.analyzer.position,
                            timestamp=time.time(),
                            byte_value=byte_val,
                            anomaly_type=anomalies[0].test_type if anomalies else None,
                            z_score=anomalies[0].z_score if anomalies else None,
                            p_value=anomalies[0].p_value if anomalies else None,
                            significance=anomalies[0].significance_level
                            if anomalies
                            else None,
                        )
                        self.writer.write_record(record)

                # Small delay to control update rate
                await asyncio.sleep(0.02)

        except Exception as e:
            self.notify(f"Game capture error: {e}", severity="error")

    async def _game_playback_loop(self) -> None:
        """Game playback loop for replaying game files."""
        if not self.reader:
            return

        visualizer = self.query_one("#visualizer", BitstreamVisualizer)
        stats_display = self.query_one("#stats_display", StatsDisplay)

        # Initialize analyzer for game replay
        self.analyzer = RandomnessAnalyzer(window_size=1000, sensitivity=0.01)

        # Counter to throttle visualization updates
        viz_update_counter = 0
        viz_update_frequency = 10

        try:
            position = 0
            for record in self.reader.iter_records():
                # Check for shutdown or pause
                if self._shutting_down:
                    break
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue

                # Re-analyze the byte to trigger game logic
                anomalies = self.analyzer.add_byte(record.byte_value)

                # Add anomalies to game state for replay
                for anomaly in anomalies:
                    if self.game_state:
                        self.game_state.add_anomaly(anomaly)

                # Calculate visualization value
                viz_value = (record.byte_value - 127.5) / 127.5

                # Use recorded anomaly data for visualization
                anomaly_marker = record.significance
                if record.z_score is not None:
                    viz_value = record.z_score / 5.0
                    viz_value = max(-1, min(1, viz_value))

                # Update visualization and stats
                viz_update_counter += 1
                if viz_update_counter >= viz_update_frequency:
                    visualizer.add_data_point(viz_value, anomaly_marker)

                    position += 1
                    stats = {
                        "current_position": position,
                        "total_bits": position * 8,
                        "ones_ratio": 0.5,
                        "byte_mean": record.byte_value,
                        "byte_std": 0.0,
                        "total_anomalies": 1 if record.anomaly_type else 0,
                    }
                    stats_display.update_stats(stats)

                    # Update game widgets
                    self._update_game_widgets()

                    viz_update_counter = 0

                # Control playback speed
                await asyncio.sleep(0.02)

        except Exception as e:
            self.notify(f"Game playback error: {e}", severity="error")
