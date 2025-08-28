#!/usr/bin/env python3
"""Debug the real app startup flow."""

import asyncio
import traceback
from pathlib import Path


def debug_real_app():
    print("🔍 Debugging Real App Flow")
    print("=" * 40)

    try:
        print("1. Testing CLI imports...")
        from rng_viz.cli import resolve_capture_path
        from rng_viz.ui.app import RNGVisualizerApp

        print("✓ CLI imports successful")

        print("\n2. Testing path resolution...")
        test_path = Path("./test_debug")
        resolved_path = resolve_capture_path(test_path)
        print(f"✓ Path resolved: {resolved_path}")

        print("\n3. Creating app instance...")
        app = RNGVisualizerApp()
        print("✓ App instance created")

        print("\n4. Testing run_live_mode call (real flow)...")
        # This should exactly mirror what the CLI does

        # Add debug hooks to see what happens
        original_call_later = app.call_later

        def debug_call_later(coro):
            print(f"   📞 call_later called with: {coro}")
            return original_call_later(coro)

        app.call_later = debug_call_later

        original_run = app.run

        def debug_run():
            print("   🏃 app.run() called - starting Textual")
            try:
                return original_run()
            except Exception as e:
                print(f"   ❌ Error in app.run(): {e}")
                traceback.print_exc()
                raise

        app.run = debug_run

        print("   Calling run_live_mode with real device...")
        app.run_live_mode(resolved_path, device_path="/dev/ttyACM0")

        print("   ✓ run_live_mode returned (should have started app)")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()


def test_minimal_with_setup():
    """Test a minimal app that mimics our setup pattern."""
    print("\n🧪 Testing Minimal App with Setup Pattern")
    print("=" * 40)

    from textual.app import App
    from textual.widgets import Label

    class TestApp(App):
        def __init__(self):
            super().__init__()
            self.setup_complete = False

        def compose(self):
            yield Label("Test app with async setup")

        def on_mount(self):
            print("   📱 App mounted, scheduling setup...")
            self.call_later(self.async_setup)

        async def async_setup(self):
            print("   ⚙️  Running async setup...")
            try:
                # Simulate device connection
                await asyncio.sleep(0.1)
                print("   ✓ Async setup complete")
                self.setup_complete = True

                # Exit after successful setup
                self.exit()

            except Exception as e:
                print(f"   ❌ Setup error: {e}")
                traceback.print_exc()
                self.exit()

    try:
        print("   Creating minimal test app...")
        test_app = TestApp()
        print("   Starting test app...")
        test_app.run()
        print(f"   ✓ Test app completed, setup_complete: {test_app.setup_complete}")

    except Exception as e:
        print(f"   ❌ Test app error: {e}")
        traceback.print_exc()


def test_actual_cli():
    """Test the actual CLI call programmatically."""
    print("\n🖥️  Testing Actual CLI Call")
    print("=" * 40)

    try:
        print("   Importing main CLI function...")
        from rng_viz.cli import main

        print("   Simulating CLI call...")
        # Simulate sys.argv for the CLI
        import sys

        original_argv = sys.argv.copy()

        try:
            sys.argv = ["rng-viz", "--live", "./test_debug"]
            print(f"   CLI args: {sys.argv}")

            print("   Calling main()...")
            main()
            print("   ✓ CLI main() returned")

        finally:
            sys.argv = original_argv

    except SystemExit as e:
        print(f"   ℹ️  CLI exited with code: {e.code}")
    except Exception as e:
        print(f"   ❌ CLI error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    debug_real_app()
    test_minimal_with_setup()
    test_actual_cli()
