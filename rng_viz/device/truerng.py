"""TrueRNG Pro V2 device interface."""

import time
from collections.abc import Generator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import serial
import serial.tools.list_ports


class TrueRNGMode(Enum):
    """TrueRNG Pro V2 operating modes."""

    NORMAL = "Normal Mode"  # Both generators combined, whitened
    NORMAL_RNG1 = "Normal, RNG1"  # Generator 1 only, whitened
    NORMAL_RNG2 = "Normal, RNG2"  # Generator 2 only, whitened
    POWER_DEBUG = "Power Supply Debug"  # Voltage in mV ASCII
    RNG_DEBUG = "RNG Debug"  # Outputs 0xRRR in ASCII
    RAW_BINARY = "RAW Binary"  # ADC values, non-whitened
    RAW_ASCII = "RAW ASCII"  # ADC values in ASCII


@dataclass
class DeviceInfo:
    """Information about detected TrueRNG device."""

    port: str
    description: str
    vid: int | None = None
    pid: int | None = None


class TrueRNGDevice:
    """Interface for TrueRNG Pro V2 random number generator."""

    # Common USB VID/PID for TrueRNG devices (may need adjustment)
    TRUERNG_VID = 0x04D8  # Microchip VID
    TRUERNG_PID = 0x0009  # Common PID for CDC devices

    def __init__(self, port: str | None = None, mode: TrueRNGMode = TrueRNGMode.NORMAL):
        """Initialize TrueRNG device connection.

        Args:
            port: Serial port path (auto-detect if None)
            mode: Operating mode for the device
        """
        self.port = port
        self.mode = mode
        self.serial_conn: serial.Serial | None = None
        self.is_connected = False

    @classmethod
    def find_devices(cls) -> list[DeviceInfo]:
        """Find all potential TrueRNG devices.

        Returns:
            List of detected device information
        """
        devices = []
        ports = serial.tools.list_ports.comports()

        for port in ports:
            # Look for CDC ACM devices (common for TrueRNG)
            if any(
                keyword in port.description.lower()
                for keyword in ["cdc", "acm", "truerng", "random"]
            ):
                devices.append(
                    DeviceInfo(
                        port=port.device,
                        description=port.description,
                        vid=port.vid,
                        pid=port.pid,
                    )
                )

        # Fallback: try common device paths on Linux
        common_paths = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"]
        for path in common_paths:
            if Path(path).exists() and not any(d.port == path for d in devices):
                devices.append(
                    DeviceInfo(port=path, description="Potential TrueRNG device")
                )

        return devices

    def connect(self, port: str | None = None) -> bool:
        """Connect to TrueRNG device.

        Args:
            port: Override the port to connect to

        Returns:
            True if connection successful
        """
        if port:
            self.port = port

        if not self.port:
            # Auto-detect
            devices = self.find_devices()
            if not devices:
                raise ConnectionError("No TrueRNG devices found")
            self.port = devices[0].port

        try:
            # TrueRNG Pro V2 typically uses these settings
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=115200,  # Common for CDC devices
                timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )

            # Give device time to initialize
            time.sleep(0.1)

            # Test connection by reading a small amount of data
            test_data = self.serial_conn.read(10)
            if len(test_data) > 0:
                self.is_connected = True
                return True
            else:
                self.serial_conn.close()
                return False

        except Exception as e:
            if self.serial_conn:
                self.serial_conn.close()
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")

    def disconnect(self) -> None:
        """Disconnect from device."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.is_connected = False

    def read_bytes(self, num_bytes: int = 1024) -> bytes:
        """Read raw bytes from device.

        Args:
            num_bytes: Number of bytes to read

        Returns:
            Raw bytes from device
        """
        if not self.is_connected or not self.serial_conn:
            raise RuntimeError("Device not connected")

        return self.serial_conn.read(num_bytes)

    def stream_bytes(self, chunk_size: int = 1024) -> Generator[bytes]:
        """Stream bytes from device.

        Args:
            chunk_size: Size of each chunk to read

        Yields:
            Chunks of raw bytes
        """
        if not self.is_connected:
            raise RuntimeError("Device not connected")

        try:
            while self.is_connected:
                chunk = self.read_bytes(chunk_size)
                if chunk:
                    yield chunk
                else:
                    # No data available, small delay to prevent busy waiting
                    time.sleep(0.001)
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect()

    def get_status(self) -> dict:
        """Get device status information.

        Returns:
            Dictionary with device status
        """
        return {
            "connected": self.is_connected,
            "port": self.port,
            "mode": self.mode.value,
            "serial_open": self.serial_conn.is_open if self.serial_conn else False,
        }

    def __enter__(self) -> "TrueRNGDevice":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()
