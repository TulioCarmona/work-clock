"""
One-time setup: downloads and installs the required packages into libs/
so the app can run portably without touching your system Python.

Usage:
    python setup.py
"""
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "PyQt6",
    "Pillow",
]

LIBS_DIR = Path(__file__).resolve().parent / "libs"
LIBS_DIR.mkdir(exist_ok=True)

print(f"Installing packages into: {LIBS_DIR}\n")

for package in REQUIRED:
    print(f"  Installing {package}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package, "--target", str(LIBS_DIR), "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR installing {package}:\n{result.stderr}")
        sys.exit(1)
    else:
        print(f"  {package} OK")

print("\nSetup complete! You can now run the app with:  python run.py")
