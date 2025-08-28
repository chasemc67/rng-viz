"""Main Textual application for RNG Visualizer."""

import asyncio
import signal
import sys
import time
from pathlib import Path

from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Label, Static

from ..analysis.stats import RandomnessAnalyzer
from ..data.storage import (
    BitstreamReader,
    BitstreamRecord,
    BitstreamWriter,
    create_capture_metadata,
)
from ..device.truerng import TrueRNGDevice


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
    ]

    def __init__(self):
        super().__init__()
        self.device: TrueRNGDevice | None = None
        self.analyzer: RandomnessAnalyzer | None = None
        self.writer: BitstreamWriter | None = None
        self.reader: BitstreamReader | None = None
        self.is_live_mode = False
        self.is_paused = False
        self.capture_task: asyncio.Task | None = None
        self._shutting_down = False

        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()

        with Container(id="main_container"):
            with Vertical(id="left_panel"):
                yield BitstreamVisualizer(id="visualizer")

                with Container(id="controls"):
                    yield Label(
                        "[bold red]Press \\[Q] to Quit or Ctrl+C[/bold red] | \\[S]tatus | \\[P]ause | \\[R]esume",
                        markup=True,
                    )

            with Vertical(id="right_panel"):
                yield DeviceStatus(id="device_status")
                yield StatsDisplay(id="stats_display")

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

                # Start playback
                await self._playback_loop()

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
