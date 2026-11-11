#!/usr/bin/env python3
"""Convenience entry point forwarding to scripts/render_readme_cards.py."""
import sys
from pathlib import Path

# Add scripts directory to path and execute main
scripts_dir = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from render_readme_cards import main

if __name__ == "__main__":
    main()
