#!/usr/bin/env python3
"""Render every section, then shoot the baselines. One command after any change."""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    "render_hero.py",       # 01
    "render_about.py",      # 02
    "render_projects.py",   # 03
    "render_heatmap.py",    # 04
    "render_stack.py",      # 05
    "render_momentum.py",   # 06
    "render_hours.py",      # 07
    "render_week.py",       # 08
    "render_shipped.py",    # 09
    "render_contact.py",    # 10 + 12
    "render_buttons.py",    # btn-*
]

for step in STEPS:
    r = subprocess.run([sys.executable, os.path.join(HERE, step)])
    if r.returncode:
        sys.exit(r.returncode)

if "--no-shots" not in sys.argv:
    subprocess.run([sys.executable, os.path.join(HERE, "shoot.py")])
