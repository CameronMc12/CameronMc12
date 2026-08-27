#!/usr/bin/env python3
"""Render every asset, then shoot the baselines. One command after any change."""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["render_hero.py", "render_wordmark.py", "render_heatmap.py"]

for step in STEPS:
    print(f"— {step}")
    r = subprocess.run([sys.executable, os.path.join(HERE, step)])
    if r.returncode:
        sys.exit(r.returncode)

if "--no-shots" not in sys.argv:
    print("— shoot.py --readme")
    subprocess.run([sys.executable, os.path.join(HERE, "shoot.py"), "--readme"])
