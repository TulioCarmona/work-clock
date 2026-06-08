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

def ensure_pip():
    # Ensure pip is available
    print("Checking for pip...")
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)

    if result.returncode == 0:
        print("pip already intalled\n")
        return
    
    print("pip not found. Intalling using ensurepip...\n")
    result = subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], capture_output=True, text=True)

    if result.returncode != 0:
        print(f" Error installing pip:\n{result.stderr}")
        sys.exit(1)

    print("pip installed successfully\n")

ensure_pip()

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
