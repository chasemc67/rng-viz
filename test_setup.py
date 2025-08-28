#!/usr/bin/env python3
"""Quick test script to validate basic setup."""

import sys


def test_imports():
    """Test that all modules can be imported."""
    try:
        print("Testing imports...")

        # Test core modules
        from rng_viz import __version__

        print(f"✓ rng_viz version: {__version__}")

        from rng_viz.device.truerng import DeviceInfo, TrueRNGDevice

        print("✓ Device interface imports successful")

        from rng_viz.analysis.stats import AnomalyResult, RandomnessAnalyzer

        print("✓ Analysis module imports successful")

        from rng_viz.data.storage import BitstreamReader, BitstreamWriter

        print("✓ Data storage imports successful")

        print("\n✅ All core imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_device_detection():
    """Test device detection without connecting."""
    try:
        print("\nTesting device detection...")
        from rng_viz.device.truerng import TrueRNGDevice

        devices = TrueRNGDevice.find_devices()
        print(f"Found {len(devices)} potential devices:")

        for i, device in enumerate(devices):
            print(f"  {i + 1}. {device.port} - {device.description}")

        if devices:
            print("✓ Device detection working")
        else:
            print("ℹ️  No devices detected (this is normal if TrueRNG not connected)")

        return True

    except Exception as e:
        print(f"❌ Device detection error: {e}")
        return False


def test_analysis():
    """Test statistical analysis with dummy data."""
    try:
        print("\nTesting statistical analysis...")
        from rng_viz.analysis.stats import RandomnessAnalyzer

        analyzer = RandomnessAnalyzer(window_size=100, sensitivity=0.05)

        # Add some dummy data
        for i in range(150):
            # Add some biased data to trigger anomalies
            byte_val = 200 if i < 50 else 55  # Biased values
            anomalies = analyzer.add_byte(byte_val)

            if anomalies:
                print(f"✓ Anomaly detected at position {analyzer.position}")
                break

        stats = analyzer.get_summary_stats()
        if stats:
            print(f"✓ Analysis statistics: {stats['total_bits']} bits processed")

        print("✓ Statistical analysis working")
        return True

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 RNG Visualizer Setup Test\n")

    results = []
    results.append(test_imports())
    results.append(test_device_detection())
    results.append(test_analysis())

    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("🎉 Setup appears to be working correctly!")
        print("\nNext steps:")
        print("1. Connect your TrueRNG Pro V2 via USB")
        print("2. Run: uv run rng-viz --live")
        print("3. Check device connection and start capturing!")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
