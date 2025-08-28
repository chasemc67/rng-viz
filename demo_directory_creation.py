#!/usr/bin/env python3
"""Demo script showing the new automatic directory creation feature."""

from pathlib import Path

from rng_viz.cli import resolve_capture_path


def demo():
    print("🎯 Demo: Automatic Directory Creation for RNG Visualizer\n")

    print("Example 1: Non-existent ./captures/ directory")
    print("Command: rng-viz --live ./captures/")

    # Remove ./captures if it exists to show creation
    captures_dir = Path("./captures")
    if captures_dir.exists():
        import shutil

        shutil.rmtree(captures_dir)

    result = resolve_capture_path(captures_dir)
    print(f"Result: {result}")
    print(f"Directory created: {captures_dir.exists()}")
    print()

    print("Example 2: Nested directory structure")
    print("Command: rng-viz --live ./experiments/consciousness/session1/")

    # Clean up first
    exp_dir = Path("./experiments")
    if exp_dir.exists():
        import shutil

        shutil.rmtree(exp_dir)

    nested_dir = Path("./experiments/consciousness/session1")
    result = resolve_capture_path(nested_dir)
    print(f"Result: {result}")
    print(f"Full path created: {nested_dir.exists()}")
    print()

    print("Example 3: Specific file with auto-created parent")
    print("Command: rng-viz --live ./data/important_experiment.csv")

    # Clean up first
    data_dir = Path("./data")
    if data_dir.exists():
        import shutil

        shutil.rmtree(data_dir)

    specific_file = Path("./data/important_experiment.csv")
    result = resolve_capture_path(specific_file)
    print(f"Result: {result}")
    print(f"Parent directory created: {specific_file.parent.exists()}")
    print()

    print("✨ All directories created automatically without user confirmation!")
    print("\nGenerated files will have names like:")
    print("  rng_capture_2025-08-27_20-19-28-117.csv")
    print("\nTo clean up demo directories:")
    print("  rm -rf ./captures ./experiments ./data")


if __name__ == "__main__":
    demo()
