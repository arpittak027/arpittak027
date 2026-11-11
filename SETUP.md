# Setup & Developer Guide

## Overview
This repository generates premium, editorial-style animated SVG cards for Arpit Tak's GitHub profile README.

## Architecture
- **Language**: Python 3.10+ (pure Python standard library for generation and validation)
- **Styling**: Inline CSS keyframes, SVG linear/radial gradients, and embedded subsetted Inter font
- **Motion**: Staggered text entrances, glowing accent sweep line, pulsing status dot, interactive arrow glides, and 52-week contribution heatmap reveal
- **Compatibility**: Tested for GitHub README `<img>` embed support with graceful `prefers-reduced-motion` and `STATIC=1` fallbacks

## Local Execution

### Normal Mode (Animated SVGs)
```bash
python scripts/render_readme_cards.py
```

### Static Mode (STATIC=1)
Disables CSS animations and renders the final visual state:
```bash
# Windows PowerShell:
$env:STATIC="1"
python scripts/render_readme_cards.py
Remove-Item Env:STATIC

# Bash / Linux / macOS:
STATIC=1 python scripts/render_readme_cards.py
```

### XML Validation
Verify all generated SVGs:
```bash
python -c "import glob, xml.etree.ElementTree as ET; [ET.parse(p) for p in glob.glob('cards/*.svg')]; print('All SVGs valid XML.')"
```

## GitHub Actions Automation
The `.github/workflows/profile-cards.yml` workflow:
1. Runs automatically every day at midnight (UTC `17 0 * * *`).
2. Supports manual triggering via the **Run workflow** button (`workflow_dispatch`).
3. Fetches live contribution calendar metrics from GitHub GraphQL API.
4. Generates updated SVGs with authentic metrics.
5. Commits and pushes back to `main`.
