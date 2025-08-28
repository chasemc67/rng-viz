# Linux Setup Guide for RNG Visualizer

This guide walks you through setting up the RNG Visualizer on Linux, including running Ubuntu in a VM on macOS using UTM.

## Table of Contents

- [Option 1: Native Linux](#option-1-native-linux)
- [Option 2: Linux VM on macOS (UTM)](#option-2-linux-vm-on-macos-utm)
- [Python Development Environment](#python-development-environment)
- [TrueRNG Pro V2 Device Setup](#truerng-pro-v2-device-setup)
- [Final Testing](#final-testing)

---

## Option 1: Native Linux

If you're already running Linux natively, skip to [Python Development Environment](#python-development-environment).

---

## Option 2: Linux VM on macOS (UTM)

### Prerequisites

- macOS with Apple Silicon (M1/M2/M3) or Intel
- At least 8GB RAM (16GB recommended)
- 40GB free disk space

### Step 1: Install UTM

**Method A: From Website**

1. Download UTM from [getutm.app](https://getutm.app/)
2. Drag UTM.app to your Applications folder

**Method B: Via Homebrew**

```bash
brew install --cask utm
```

### Step 2: Download Ubuntu Desktop ARM ISO

1. **For Apple Silicon Macs (M1/M2/M3)**:

   - Go to [Ubuntu Desktop ARM64](https://ubuntu.com/download/desktop/arm)
   - Download the latest Ubuntu Desktop ARM64 ISO (e.g., `ubuntu-24.04-desktop-arm64.iso`)

2. **For Intel Macs**:
   - Go to [Ubuntu Desktop](https://ubuntu.com/download/desktop)
   - Download the standard x86_64 ISO

### Step 3: Create Ubuntu VM in UTM

1. **Open UTM** and click "Create a New Virtual Machine"

2. **Select "Virtualize"** (not Emulate)

3. **Choose Operating System**:

   - Select "Linux"

4. **VM Configuration**:

   - **ISO Image**: Browse and select your downloaded Ubuntu ISO
   - **Memory**: 4GB minimum, 8GB recommended
   - **CPU Cores**: 4 cores recommended
   - **Storage**: 40GB minimum, 60GB recommended

5. **Hardware Settings**:

   - **Enable USB**: ✅ Check this box (required for TrueRNG device)
   - **Enable clipboard sharing**: ✅ Recommended

6. **Create and Start VM**

### Step 4: Install Ubuntu

1. **Boot from ISO** and follow Ubuntu installation wizard
2. **Choose "Normal installation"**
3. **Enable "Install third-party software"** for better hardware support
4. **Create user account** (remember username/password)
5. **Complete installation** and restart

### Step 5: Post-Installation Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential development tools
sudo apt install -y curl wget git build-essential

# Install USB utilities (for device debugging)
sudo apt install -y usbutils

# Reboot to ensure all updates are applied
sudo reboot
```

---

## Python Development Environment

### Step 1: Install Python 3.13+

```bash
# Ubuntu 24.04+ usually has Python 3.13
python3 --version

# If Python 3.13+ is not available, add deadsnakes PPA
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# Install pip
sudo apt install -y python3-pip
```

### Step 2: Install uv Package Manager

```bash
# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell or add to PATH
source $HOME/.cargo/env

# Verify installation
uv --version
```

### Step 3: Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd rng-viz

# Install project dependencies
uv sync

# Test installation
uv run python test_setup.py
```

---

## TrueRNG Pro V2 Device Setup

### Step 1: Connect Device

1. **Physical Connection**:

   - Plug TrueRNG Pro V2 into USB port
   - **For VM users**: In UTM, go to VM settings → USB and add the TrueRNG device

2. **Verify Detection**:

   ```bash
   # Check if device is detected
   lsusb

   # Look for device in /dev/
   ls /dev/tty*
   # Should see /dev/ttyACM0 or similar
   ```

### Step 2: Fix Device Permissions

The device will be detected but require permission setup:

```bash
# Check current permissions
ls -la /dev/ttyACM0

# Method 1: Add user to dialout group (RECOMMENDED)
sudo usermod -a -G dialout $USER

# IMPORTANT: Logout and login again for group changes to take effect
exit
# SSH/login back in

# Verify group membership
groups
# Should show "dialout" in the list
```

**Alternative methods if dialout group doesn't work:**

```bash
# Method 2: Temporary permission fix
sudo chmod 666 /dev/ttyACM0

# Method 3: Permanent udev rule
echo 'KERNEL=="ttyACM*", ATTRS{idVendor}=="04d8", MODE="0666"' | sudo tee /etc/udev/rules.d/99-truerng.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Step 3: Test Device Connection

```bash
# Test device detection
uv run python test_setup.py

# Test actual device connection
uv run python -c "
from rng_viz.device.truerng import TrueRNGDevice
device = TrueRNGDevice(port='/dev/ttyACM0')
try:
    connected = device.connect()
    if connected:
        print('✅ Device connected successfully!')
        data = device.read_bytes(10)
        print(f'✅ Read data: {data.hex()}')
        device.disconnect()
    else:
        print('❌ Connection failed')
except Exception as e:
    print(f'❌ Error: {e}')
    if 'Permission denied' in str(e):
        print('💡 Fix: Make sure you are in the dialout group and have logged out/in')
"
```

**Expected successful output:**

```
✅ Device connected successfully!
✅ Read data: a1b2c3d4e5f6789a01b2
```

---

## Final Testing

### Step 1: Test the Application

```bash
# Test with auto-generated filename
uv run rng-viz --live ./test_captures/

# Test with specific filename
uv run rng-viz --live ./my_experiment.csv

# Test with explicit device path
uv run rng-viz --live ./captures/ --device /dev/ttyACM0
```

### Step 2: Expected UI

You should see:

- **Textual-based terminal UI** with scrolling bitstream visualization
- **Real-time statistics** panel showing analysis data
- **Device status** showing "🟢 Connected"
- **Control instructions** showing keyboard shortcuts

### Step 3: Keyboard Controls

- **`Q`** - Quit application (graceful shutdown)
- **`Ctrl+C`** - Emergency quit (also graceful)
- **`P`** - Pause data capture
- **`R`** - Resume data capture
- **`S`** - Save current session

---

## Troubleshooting

### Device Not Detected

```bash
# Check USB devices
lsusb

# Check if TrueRNG is listed as CDC/ACM device
dmesg | grep -i cdc
dmesg | grep -i acm

# For VM users: Ensure USB passthrough is enabled in UTM
```

### Permission Errors

```bash
# Verify group membership
groups | grep dialout

# If dialout not shown, re-run usermod and logout/login:
sudo usermod -a -G dialout $USER
exit  # Logout completely
# Login again
```

### App Exits Silently

```bash
# Run with verbose error reporting
uv run python -c "
from rng_viz.ui.app import RNGVisualizerApp
import traceback
try:
    app = RNGVisualizerApp()
    app.run_live_mode()
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
"
```

### Terminal Issues Over SSH

```bash
# Try different terminal settings
TERM=xterm-256color uv run rng-viz --live ./captures/

# Or force terminal compatibility
TERM=linux uv run rng-viz --live ./captures/
```

---

## Next Steps

Once your Linux environment is set up and the device is working:

1. **Read the [Main README](README.md)** for complete usage instructions
2. **Follow the statistical analysis examples**
3. **Learn about data capture formats and playback features**
4. **Explore the consciousness research applications**

## Hardware Notes

### TrueRNG Pro V2 Specifications

- **Output Rate**: >3.2 Mbits/second
- **Connection**: USB CDC (appears as `/dev/ttyACM0`)
- **Power**: USB powered (~100mA)
- **Compatibility**: Linux kernel 2.6+ (CDC driver included)

### VM Performance Tips

- **Allocate sufficient RAM**: 8GB recommended for smooth operation
- **Enable hardware acceleration**: Ensure virtualization is enabled
- **USB 3.0**: Use USB 3.0 ports for better performance
- **Close unnecessary apps**: VM + data analysis is CPU intensive

---

## Support

If you encounter issues:

1. **Check device permissions** using the steps above
2. **Verify USB connectivity** with `lsusb` and `dmesg`
3. **Test with the debug script** to isolate issues
4. **Review the main README** for additional troubleshooting

For hardware-specific issues, consult the [TrueRNG Pro V2 documentation](https://ubld.it/products/truerngprov2).
