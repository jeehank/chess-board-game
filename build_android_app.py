"""
build_android_app.py
====================
Runs the unified build script to generate the Android HTML installer and assets,
keeping all platforms synchronized.
"""

import subprocess
import sys
import os

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    res = subprocess.run([sys.executable, "build_game_and_installer.py"], cwd=root)
    sys.exit(res.returncode)
