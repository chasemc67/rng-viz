#!/usr/bin/env python3
"""Debug script to catch startup issues."""

import sys
import traceback
from pathlib import Path


def debug_startup():
    print("🐛 Debugging RNG Visualizer Startup")
    print("=" * 50)

    try:
        print("1. Testing imports...")
        from rng_viz.device.truerng import TrueRNGDevice
        from rng_viz.ui.app import RNGVisualizerApp

        print("✓ Imports successful")

        print("\n2. Testing device detection...")
        devices = TrueRNGDevice.find_devices()
        print(f"✓ Found {len(devices)} devices: {[d.port for d in devices]}")

        print("\n3. Testing device connection...")
        if devices:
            device = TrueRNGDevice(port=devices[0].port)
            try:
                connected = device.connect()
                print(f"✓ Device connection: {connected}")
                if connected:
                    status = device.get_status()
                    print(f"✓ Device status: {status}")
                    device.disconnect()
            except Exception as e:
                print(f"❌ Device connection error: {e}")
                traceback.print_exc()
        else:
            print("⚠️  No devices found for connection test")

        print("\n4. Testing app creation...")
        app = RNGVisualizerApp()
        print("✓ App created successfully")

        print("\n5. Testing run_live_mode setup...")
        # Test the setup without actually running the UI
        test_path = Path("./debug_test.csv")

        # Patch the app to avoid starting the actual UI
        original_run = app.run
        app.run = lambda: print("✓ App.run() would be called here")

        # This should trigger the setup_live coroutine
        print("   Calling run_live_mode...")
        app.run_live_mode(test_path, device_path="/dev/ttyACM0")

        print("✓ run_live_mode setup completed")

        print("\n6. Testing minimal Textual app...")
        from textual.app import App
        from textual.widgets import Label

        class MinimalApp(App):
            def compose(self):
                yield Label("Test app running!")

            def on_mount(self):
                print("✓ Minimal app mounted")
                self.exit()

        minimal_app = MinimalApp()
        print("   Starting minimal Textual app...")
        minimal_app.run()
        print("✓ Minimal Textual app completed")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during debug: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

        # Additional debugging info
        print(f"\nPython version: {sys.version}")
        print(f"Platform: {sys.platform}")

        # Check terminal info
        import os

        print(f"TERM: {os.environ.get('TERM', 'not set')}")
        print(f"SSH_CONNECTION: {os.environ.get('SSH_CONNECTION', 'not set')}")
        print(f"DISPLAY: {os.environ.get('DISPLAY', 'not set')}")


if __name__ == "__main__":
    debug_startup()
