"""
Portable launcher for Work Clock.
Adds the local libs/ folder to sys.path so bundled packages are used
instead of (or in place of) system-installed ones.
Run this script instead of WC_App.py directly.
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LIBS_DIR = BASE_DIR / "libs"

# Check libs folder exists and has content
if not LIBS_DIR.exists() or not any(LIBS_DIR.iterdir()):
    print("Bundled packages not found.")
    print("Please run setup.py first:  python setup.py")
    sys.exit(1)

# Prepend libs/ so bundled packages take priority
sys.path.insert(0, str(LIBS_DIR))

# Now run the app
import WC_App  # noqa: F401  (imported for side-effects — starts mainloop)
