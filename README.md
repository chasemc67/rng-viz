# RNG Visualizer

A Python application for capturing, analyzing, and visualizing bitstreams from the TrueRNG Pro V2 hardware random number generator. Inspired by the Global Consciousness Project, this tool detects statistical anomalies that may indicate consciousness-related deviations in random data.

<img width="3454" height="2124" alt="Screenshot 2025-08-27 at 10 24 10 PM" src="https://github.com/user-attachments/assets/d6696f51-a051-40a1-a87b-7f80ed6d09f2" />


## Features

- **Live Capture**: Real-time visualization of random bitstreams with anomaly detection
- **File Playback**: Analyze previously captured data files
- **Game Mode**: Interactive consciousness experiment with turn-based anomaly tracking
- **Statistical Analysis**: Multiple tests including frequency analysis, runs tests, and chi-square tests
- **Modern Terminal UI**: Clean, responsive interface built with Textual
- **Data Recording**: Save captures for later analysis in CSV format
- **Anomaly Highlighting**: Visual indicators for statistically significant deviations

## Hardware Requirements

- **TrueRNG Pro V2** random number generator ([ubld.it](https://ubld.it/products/truerngprov2))
- USB connection to host system
- Compatible with Linux, macOS, and Windows

**📋 Linux Users**: See [LINUX_SETUP.md](LINUX_SETUP.md) for complete setup instructions including VM setup on macOS.

## Installation

### Prerequisites

- Python 3.13 or later
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd rng-viz
   ```

2. **Install dependencies using uv**:

   ```bash
   uv sync
   ```

3. **Install for development** (optional):

   ```bash
   uv sync --group dev
   ```

4. **Test installation**:

   ```bash
   uv run python test_setup.py
   ```

   This will verify that all components can be imported and basic functionality works.

   **Note**: This test checks software installation but does NOT test actual device connection. Device connection requires proper permissions (see Device Setup below).

### Device Setup

1. **Connect your TrueRNG Pro V2** via USB
2. **On Linux**, ensure proper permissions:

   ```bash
   # Add user to dialout group (may require logout/login)
   sudo usermod -a -G dialout $USER

   # Or create udev rules for the device
   echo 'KERNEL=="ttyACM*", ATTRS{idVendor}=="04d8", MODE="0666"' | sudo tee /etc/udev/rules.d/99-truerng.rules
   sudo udevadm control --reload-rules
   ```

3. **Verify device connection**:
   ```bash
   # Device typically appears as /dev/ttyACM0 or /dev/ttyUSB0
   ls /dev/tty*
   ```

## Usage

### Command Line Interface

```bash
# Interactive mode (choose between live capture or file viewing)
rng-viz

# Start live capture with automatic saving to specific file
rng-viz --live /path/to/save/capture.csv

# Start live capture with auto-generated timestamped filename in directory
rng-viz --live /path/to/captures/              # Creates directory if needed

# Start live capture without saving
rng-viz --live

# Open existing capture file
rng-viz --open /path/to/existing/capture.csv

# Start game mode (consciousness interaction experiment)
rng-viz --game

# Start game mode with automatic saving to specific file
rng-viz --game /path/to/save/game.csv

# Start game mode with auto-generated timestamped filename
rng-viz --game /path/to/games/                 # Creates directory if needed

# Replay existing game session
rng-viz --open-game /path/to/existing/game.csv

# Specify device path manually
rng-viz --live --device /dev/ttyACM0
```

### Live Capture Mode

In live capture mode, you'll see:

- **Bitstream Visualization**: Horizontal scrolling wave showing data flow
- **Anomaly Detection**: Statistical deviations marked with symbols:
  - `▲`/`▼` - Significant anomalies
  - Red (`***`) - 99.9% confidence level
  - Yellow (`**`) - 99% confidence level
  - Light yellow (`*`) - 95% confidence level
- **Real-time Statistics**: Current analysis window statistics
- **Device Status**: Connection and operational status

### Game Mode

Game mode provides an interactive consciousness experiment interface where you attempt to influence the random number generator through focused intention. The interface includes:

**Game Flow:**

- **Randomized Instructions**: The system randomly tells you to "Generate more 1's" or "Generate more 0's"
- **Timed Turns**: Each turn lasts between 10-30 seconds (randomly chosen)
- **Anomaly Tracking**: All statistical deviations are categorized into 6 buckets:
  - **Red ▲/▼**: 99.9% confidence anomalies (\*\*\* significance) pointing up/down
  - **Orange ▲/▼**: 99% confidence anomalies (\*\* significance) pointing up/down
  - **Yellow ▲/▼**: 95% confidence anomalies (\* significance) pointing up/down

**Game Interface:**

- **Instruction Panel**: Shows current goal ("Generate more 1's" / "Generate more 0's") and countdown timer
- **Current Turn Bucket**: Real-time scoring for the active turn (displayed prominently)
- **Turn History**: Summary of all completed turns showing instruction and results
- **Overall Statistics**: Combined results across all turns (shown when game is finished)

**Game Controls:**

- All standard controls (Q, S, P, R) work the same as live mode
- **F** - Finish Game: End the session and display overall statistics

**Hypothesis Testing:**
The game allows you to test whether focused intention can bias the random number generator. Ideally:

- When asked to "Generate more 1's", you should see more upward anomalies (▲) than downward (▼)
- When asked to "Generate more 0's", you should see more downward anomalies (▼) than upward (▲)

### Keyboard Controls

- `Q` - Quit application (graceful shutdown with file save)
- `Ctrl+C` - Emergency quit (also performs graceful shutdown)
- `S` - Show status (file info, save progress, record counts)
- `P` - Pause data capture/playback
- `R` - Resume data capture/playback
- `F` - Finish Game (game mode only - end session and show overall statistics)

**Important**: Both `Q` and `Ctrl+C` will properly close any open capture files to prevent data corruption. The application will show shutdown progress and confirm when data has been saved safely.

### Automatic Directory Creation

The application intelligently handles directory paths and creates them automatically:

**Directory Paths** (auto-generates timestamped filenames):

```bash
rng-viz --live ./captures/                    # Creates ./captures/ if needed
rng-viz --live /data/experiments/session1/    # Creates full nested path
rng-viz --live ~/consciousness_data/          # Works with home directory
```

**Generated filenames** follow the pattern: `rng_capture_YYYY-MM-DD_HH-MM-SS-mmm.csv`

Example: `rng_capture_2025-08-27_20-19-57-574.csv`

**Specific File Paths** (uses exact filename):

```bash
rng-viz --live ./my_experiment.csv            # Creates ./my_experiment.csv
rng-viz --live /data/important.csv            # Creates /data/ directory if needed
```

**Smart Detection**:

- Paths ending with `/` or common directory names → treated as directories
- Paths with file extensions (`.csv`, `.txt`) → treated as specific files
- Non-existent parent directories are created automatically
- No user confirmation required for standard patterns

### File Format

Captured data is saved in CSV format with metadata:

```csv
# {"timestamp": "2024-01-01T12:00:00", "device_info": {...}, ...}
position,timestamp,byte_value,anomaly_type,z_score,p_value,significance
1,1704110400.123,142,,,,
2,1704110400.124,87,frequency,3.14,0.002,**
...
```

## Statistical Analysis

The application performs real-time statistical analysis using a sliding window approach:

### Tests Performed

1. **Frequency Test**: Detects bias toward 0s or 1s in the bit sequence
2. **Runs Test**: Identifies unusual patterns in consecutive identical bits
3. **Chi-Square Test**: Tests uniformity of byte value distribution

### Significance Levels

- `***` - 99.9% confidence (p < 0.001)
- `**` - 99% confidence (p < 0.01)
- `*` - 95% confidence (p < 0.05)

### Configuration

Default settings:

- **Window Size**: 1000 bytes (8000 bits)
- **Sensitivity**: p < 0.01 (99% confidence threshold)
- **Update Rate**: ~100 Hz for smooth visualization

## Development

### Project Structure

```
rng-viz/
├── rng_viz/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── device/
│   │   ├── __init__.py
│   │   └── truerng.py      # TrueRNG device interface
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py          # Textual application
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── stats.py        # Statistical analysis
│   └── data/
│       ├── __init__.py
│       └── storage.py      # Data storage/loading
├── pyproject.toml
├── README.md
└── PRD.md
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
uv run ruff check .
```

### Type Checking

```bash
uv run mypy rng_viz/
```

## Troubleshooting

### Testing and Diagnosis

1. **Test software installation**:

   ```bash
   uv run python test_setup.py
   ```

   This verifies imports and basic functionality work.

2. **Test device connection separately**:

   ```bash
   uv run python -c "
   from rng_viz.device.truerng import TrueRNGDevice
   device = TrueRNGDevice()
   try:
       if device.connect():
           print('✅ Device connected successfully!')
           data = device.read_bytes(10)
           print(f'✅ Read data: {data.hex()}')
           device.disconnect()
       else:
           print('❌ Connection failed')
   except Exception as e:
       print(f'❌ Error: {e}')
   "
   ```

3. **For comprehensive Linux setup help**:
   See [LINUX_SETUP.md](LINUX_SETUP.md) for detailed troubleshooting and VM setup instructions.

### Device Connection Issues

1. **Device not found**:

   - Check USB connection
   - Verify device appears in `/dev/` (Linux) or Device Manager (Windows)
   - Try different USB ports
   - Check permissions (Linux)

2. **Permission denied**:

   ```bash
   # Linux: Add user to dialout group
   sudo usermod -a -G dialout $USER
   # Then logout and login again
   ```

3. **Data stream issues**:
   - Verify device is not in use by another application
   - Check device mode settings
   - Try restarting the application

### Performance Issues

1. **Slow visualization**:

   - Reduce window size in configuration
   - Lower the update rate
   - Check system resources

2. **High CPU usage**:
   - The application is CPU-intensive due to real-time analysis
   - Consider running on dedicated hardware for long captures

## References

- [TrueRNG Pro V2 Documentation](https://ubld.it/products/truerngprov2)
- [Global Consciousness Project](https://noosphere.princeton.edu/)
- [Textual Documentation](https://textual.textualize.io/)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
