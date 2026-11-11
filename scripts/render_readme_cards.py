#!/usr/bin/env python3
"""
scripts/render_readme_cards.py
Generates premium, animated, editorial-style SVG cards for Arpit Tak's GitHub profile.
Supports STATIC=1 for disabling animations, embeds subsetted fonts when available,
and parses real GitHub contribution calendar data.
"""

import os
import json
import base64
import html
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "cards"
DATA_FILE = ROOT / "data" / "contributions.json"
FONTS_DIR = ROOT / "assets" / "fonts"

STATIC = os.getenv("STATIC") == "1"

# --- Editorial Brand Palette ---
# Deep Navy / Near-Black Backgrounds
BG_MAIN = "#080b14"
BG_PANEL = "#0e1526"
BG_PANEL_ALT = "#121b30"
BORDER = "#1e293b"
BORDER_ACCENT = "#334155"

# Brand Accents
VIOLET = "#8b5cf6"        # Electric Violet (Primary)
VIOLET_LIGHT = "#a78bfa"
VIOLET_GLOW = "rgba(139, 92, 246, 0.25)"
AQUA = "#22d3ee"          # Aqua / Cyan (Secondary)
AQUA_LIGHT = "#67e8f9"
AQUA_GLOW = "rgba(34, 211, 238, 0.25)"
BLUE = "#38bdf8"          # Accent Blue / Sky
SUCCESS = "#10b981"       # Emerald green
WARN = "#f59e0b"          # Amber
DANGER = "#ef4444"        # Red

# Typography Colors
TEXT_WHITE = "#f8fafc"    # Clean off-white
TEXT_MUTED = "#94a3b8"    # Clean slate gray
TEXT_DIM = "#64748b"      # Muted slate

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO_FAMILY = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace"


def esc(val):
    """Escape XML characters."""
    return html.escape(str(val) if val is not None else "", quote=True)


def get_font_css():
    """Returns @font-face CSS if subsetted font file exists."""
    woff2_path = FONTS_DIR / "Inter-subset.woff2"
    woff_path = FONTS_DIR / "Inter-subset.woff"
    
    target = None
    fmt = "woff2"
    if woff2_path.exists():
        target = woff2_path
        fmt = "woff2"
    elif woff_path.exists():
        target = woff_path
        fmt = "woff"
        
    if target:
        try:
            b64_font = base64.b64encode(target.read_bytes()).decode("ascii")
            return f"""
    @font-face {{
      font-family: 'Inter';
      font-style: normal;
      font-weight: 300 800;
      font-display: swap;
      src: url(data:font/{fmt};base64,{b64_font}) format('{fmt}');
    }}
"""
        except Exception as e:
            print(f"[WARN] Failed to read font file {target}: {e}")
            
    return ""


def get_base_css():
    """Generates CSS for typography, animations, and motion preferences."""
    font_face = get_font_css()
    
    if STATIC:
        anim_css = """
    .reveal, .reveal-d1, .reveal-d2, .reveal-d3, .reveal-d4, .reveal-d5 {
      opacity: 1 !important;
      transform: none !important;
      animation: none !important;
    }
    .sweep-beam { display: none !important; }
    .pulse-dot { opacity: 1 !important; transform: none !important; }
    .cursor-blink { opacity: 1 !important; }
    .arrow-glide { transform: none !important; }
    .bar-grow { transform: scaleY(1) !important; }
    .cell-stagger { opacity: 1 !important; transform: none !important; }
"""
    else:
        anim_css = """
    @keyframes riseFade {
      0% { opacity: 0; transform: translateY(12px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes sweepBeam {
      0% { transform: translateX(-100%); }
      50%, 100% { transform: translateX(200%); }
    }
    @keyframes pulseGlow {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.35; transform: scale(0.85); }
    }
    @keyframes cursorBlink {
      0%, 49% { opacity: 1; }
      50%, 100% { opacity: 0; }
    }
    @keyframes arrowGlide {
      0%, 100% { transform: translate(0, 0); }
      50% { transform: translate(3px, -3px); }
    }
    @keyframes barGrow {
      0% { transform: scaleY(0); }
      100% { transform: scaleY(1); }
    }
    @keyframes cellReveal {
      0% { opacity: 0; transform: scale(0.4); }
      100% { opacity: 1; transform: scale(1); }
    }

    .reveal { opacity: 0; animation: riseFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.05s forwards; }
    .reveal-d1 { opacity: 0; animation: riseFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.15s forwards; }
    .reveal-d2 { opacity: 0; animation: riseFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.28s forwards; }
    .reveal-d3 { opacity: 0; animation: riseFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.42s forwards; }
    .reveal-d4 { opacity: 0; animation: riseFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.55s forwards; }
    .reveal-d5 { opacity: 0; animation: riseFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.70s forwards; }

    .sweep-beam {
      animation: sweepBeam 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    }
    .pulse-dot {
      animation: pulseGlow 2.5s ease-in-out infinite;
      transform-origin: center;
    }
    .cursor-blink {
      animation: cursorBlink 1s infinite;
    }
    .arrow-glide {
      animation: arrowGlide 2.4s ease-in-out infinite;
    }
    .bar-grow {
      transform-origin: bottom;
      animation: barGrow 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
"""

    return f"""{font_face}
    text {{
      font-family: {FONT_FAMILY};
      text-rendering: geometricPrecision;
      -webkit-font-smoothing: antialiased;
    }}
    .mono {{
      font-family: {MONO_FAMILY};
    }}
    {anim_css}
    @media (prefers-reduced-motion: reduce) {{
      *, .reveal, .reveal-d1, .reveal-d2, .reveal-d3, .reveal-d4, .reveal-d5,
      .sweep-beam, .pulse-dot, .cursor-blink, .arrow-glide, .bar-grow, .cell-stagger {{
        animation: none !important;
        opacity: 1 !important;
        transform: none !important;
      }}
      .sweep-beam {{ display: none !important; }}
    }}
"""


def svg_envelope(w, h, title, desc, inner_content):
    """Wraps inner content into an accessible, validated SVG container."""
    css = get_base_css()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(desc)}</desc>
  <defs>
    <linearGradient id="violetToAqua" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{VIOLET}" />
      <stop offset="100%" stop-color="{AQUA}" />
    </linearGradient>
    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{VIOLET}" stop-opacity="0" />
      <stop offset="50%" stop-color="{AQUA}" stop-opacity="1" />
      <stop offset="100%" stop-color="{VIOLET}" stop-opacity="0" />
    </linearGradient>
    <radialGradient id="heroGlow" cx="80%" cy="20%" r="60%">
      <stop offset="0%" stop-color="{VIOLET}" stop-opacity="0.16" />
      <stop offset="60%" stop-color="{AQUA}" stop-opacity="0.04" />
      <stop offset="100%" stop-color="{BG_MAIN}" stop-opacity="0" />
    </radialGradient>
    <clipPath id="cardClip">
      <rect width="{w}" height="{h}" rx="16" />
    </clipPath>
  </defs>
  <style>
{css}
  </style>
  <g clip-path="url(#cardClip)">
    <rect width="{w}" height="{h}" rx="16" fill="{BG_MAIN}" stroke="{BORDER}" stroke-width="1.5" />
{inner_content}
  </g>
</svg>
"""


def load_contributions():
    """
    Parses contribution calendar data from data/contributions.json.
    Supports GitHub GraphQL response format, jogruber format, or flat day lists.
    """
    metrics = {
        "total": 0,
        "active_days": 0,
        "monthly": [],
        "current_streak": 0,
        "longest_streak": 0,
        "start_date": "N/A",
        "end_date": "N/A"
    }

    if not DATA_FILE.exists():
        print(f"[INFO] Contribution file not found at {DATA_FILE}. Using fallback empty data.")
        return 0, [], [], metrics

    try:
        content = DATA_FILE.read_text(encoding="utf-8")
        data = json.loads(content)
    except Exception as e:
        print(f"[WARN] Error reading {DATA_FILE}: {e}")
        return 0, [], [], metrics

    # 1. GitHub GraphQL path: data.user.contributionsCollection.contributionCalendar
    cal = (
        data.get("data", {})
        .get("user", {})
        .get("contributionsCollection", {})
        .get("contributionCalendar", {})
    )
    if not cal and "contributionCalendar" in data:
        cal = data["contributionCalendar"]
        
    weeks = []
    days = []
    total = 0

    if cal and "weeks" in cal:
        total = int(cal.get("totalContributions", 0))
        weeks = cal.get("weeks", [])
        for w in weeks:
            for d in w.get("contributionDays", []):
                days.append({
                    "date": d.get("date"),
                    "count": int(d.get("contributionCount", 0)),
                    "color": d.get("color", "")
                })
    elif "contributions" in data:
        # jogruber format
        all_contribs = data.get("contributions", [])
        # Sort chronologically
        all_contribs.sort(key=lambda x: x.get("date", ""))
        # Filter trailing 365 days
        today = date.today()
        start = today - timedelta(days=364)
        for c in all_contribs:
            d_str = c.get("date", "")
            if d_str and d_str >= start.isoformat():
                cnt = int(c.get("count", 0))
                days.append({"date": d_str, "count": cnt})
                total += cnt
    elif "days" in data:
        days = data.get("days", [])
        total = int(data.get("totalContributions", sum(int(x.get("count", x.get("contributionCount", 0))) for x in days)))

    # Compute metrics
    days.sort(key=lambda x: x.get("date", ""))
    counts_by_date = {d["date"]: d["count"] for d in days if d.get("date")}
    
    active_days = sum(1 for d in days if d.get("count", 0) > 0)

    # Monthly aggregation
    monthly = defaultdict(int)
    for d in days:
        if d.get("date"):
            ym = d["date"][:7]
            monthly[ym] += d.get("count", 0)

    # Streak calculation
    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()
    
    # Current streak
    cur_streak = 0
    test_d = date.today()
    if counts_by_date.get(today_str, 0) == 0:
        test_d = date.today() - timedelta(days=1)
    while counts_by_date.get(test_d.isoformat(), 0) > 0:
        cur_streak += 1
        test_d -= timedelta(days=1)

    # Longest streak
    longest_streak = 0
    temp_streak = 0
    for d in days:
        if d.get("count", 0) > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    metrics = {
        "total": total,
        "active_days": active_days,
        "monthly": sorted(monthly.items()),
        "current_streak": cur_streak,
        "longest_streak": longest_streak,
        "start_date": days[0]["date"] if days else "N/A",
        "end_date": days[-1]["date"] if days else "N/A"
    }

    return total, days, weeks, metrics


# ==============================================================================
# CARD 1: Hero Card
# ==============================================================================
def render_hero_card():
    w, h = 960, 300
    title = "Arpit Tak — Developer Profile"
    desc = "Building software, exploring AI, and turning ideas into useful products."

    body = f"""
    <!-- Ambient Radial Light -->
    <rect width="{w}" height="{h}" fill="url(#heroGlow)" />
    
    <!-- Top Light Sweep Track & Beam -->
    <line x1="0" y1="1.5" x2="{w}" y2="1.5" stroke="{BORDER}" stroke-width="1.5" />
    <g class="sweep-beam">
      <rect x="0" y="0" width="280" height="2" fill="url(#beamGrad)" />
    </g>

    <!-- LEFT COLUMN: Editorial Profile Content -->
    <g transform="translate(48, 48)">
      <!-- System Status / Eyebrow -->
      <g class="reveal">
        <circle cx="5" cy="5" r="4" fill="{AQUA}" class="pulse-dot" />
        <circle cx="5" cy="5" r="7" fill="none" stroke="{AQUA}" stroke-width="1" opacity="0.4" />
        <text x="20" y="9" fill="{AQUA}" font-size="11" font-weight="700" letter-spacing="2.5" class="mono">SYSTEM // ONLINE · FULL-STACK &amp; AI AGENTS</text>
      </g>

      <!-- Main Name Heading -->
      <g class="reveal-d1" transform="translate(0, 68)">
        <text x="0" y="0" fill="{TEXT_WHITE}" font-size="52" font-weight="800" letter-spacing="-0.5">ARPIT TAK<tspan fill="{VIOLET}">.</tspan></text>
      </g>

      <!-- Introduction Subtitle -->
      <g class="reveal-d2" transform="translate(0, 104)">
        <text x="0" y="0" fill="{TEXT_MUTED}" font-size="15" font-weight="400">Building software, exploring AI, and turning ideas into useful products.</text>
      </g>

      <!-- Personal Tagline Pill -->
      <g class="reveal-d3" transform="translate(0, 134)">
        <rect x="0" y="0" width="295" height="34" rx="8" fill="{BG_PANEL}" stroke="{BORDER_ACCENT}" stroke-width="1" />
        <text x="14" y="21" fill="{AQUA}" font-size="13" font-weight="600" letter-spacing="0.4">“Less consuming. More building.”</text>
      </g>

      <!-- Technical Focus Keywords -->
      <g class="reveal-d4" transform="translate(0, 192)">
        <text x="0" y="0" fill="{TEXT_DIM}" font-size="11" font-weight="600" letter-spacing="1.5" class="mono">[ TYPESCRIPT ]   [ NEXT.JS ]   [ PYTHON ]   [ AGENTIC AI ]</text>
      </g>
    </g>

    <!-- RIGHT COLUMN: Abstract Editorial Terminal Visual -->
    <g class="reveal-d2" transform="translate(565, 42)">
      <!-- Terminal Window Container -->
      <rect width="348" height="216" rx="10" fill="{BG_PANEL}" stroke="{BORDER}" stroke-width="1.5" />
      
      <!-- Terminal Header Bar -->
      <rect width="348" height="32" rx="10" fill="{BG_PANEL_ALT}" />
      <path d="M 0 32 L 348 32" stroke="{BORDER}" stroke-width="1" />
      
      <!-- Terminal Window Controls -->
      <circle cx="18" cy="16" r="4.5" fill="{DANGER}" opacity="0.85" />
      <circle cx="32" cy="16" r="4.5" fill="{WARN}" opacity="0.85" />
      <circle cx="46" cy="16" r="4.5" fill="{SUCCESS}" opacity="0.85" />
      <text x="60" y="20" fill="{TEXT_DIM}" font-size="11" class="mono">arpit@terminal: ~/identity</text>

      <!-- Terminal Body Content -->
      <g transform="translate(18, 54)" class="mono" font-size="11">
        <text x="0" y="0" fill="{AQUA}">$ whoami</text>
        <text x="0" y="18" fill="{TEXT_WHITE}">&gt; arpit_tak <tspan fill="{VIOLET}">[software_engineer]</tspan></text>
        
        <text x="0" y="42" fill="{AQUA}">$ cat profile.json</text>
        <text x="0" y="60" fill="{TEXT_MUTED}">&#123;</text>
        <text x="14" y="76" fill="{TEXT_MUTED}">"mindset": <tspan fill="{AQUA}">"Less consuming. More building."</tspan>,</text>
        <text x="14" y="92" fill="{TEXT_MUTED}">"ship": <tspan fill="{VIOLET_LIGHT}">["Outpost", "Sur", "AI-Tools"]</tspan></text>
        <text x="0" y="108" fill="{TEXT_MUTED}">&#125;</text>

        <text x="0" y="132" fill="{AQUA}">$ system status --live</text>
        <text x="0" y="148" fill="{SUCCESS}">&gt; Ready for collaboration <tspan fill="{AQUA}" class="cursor-blink">█</tspan></text>
      </g>
    </g>
"""
    return svg_envelope(w, h, title, desc, body)


# ==============================================================================
# CARD 2: Three Interactive Link Tiles
# ==============================================================================
def render_link_tile(index, title_text, desc_text, url_text, accent_color, icon_type):
    w, h = 310, 140
    title = f"{title_text} — Arpit Tak"
    desc = f"{desc_text} ({url_text})"

    # Icons defined as minimal SVG paths
    if icon_type == "code":
        # Code brackets
        icon_path = '<path d="M 12 6 L 4 14 L 12 22 M 20 6 L 28 14 L 20 22" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    elif icon_type == "compass":
        # Compass / Diamond sparkle
        icon_path = '<path d="M 16 3 L 20 12 L 29 16 L 20 20 L 16 29 L 12 20 L 3 16 L 12 12 Z" fill="none" stroke="{accent}" stroke-width="2" stroke-linejoin="round"/>'
    else:
        # Network / Globe / Node
        icon_path = '<circle cx="16" cy="16" r="11" fill="none" stroke="{accent}" stroke-width="2"/><ellipse cx="16" cy="16" rx="5" ry="11" fill="none" stroke="{accent}" stroke-width="1.5"/><line x1="5" y1="16" x2="27" y2="16" stroke="{accent}" stroke-width="1.5"/>'

    icon_rendered = icon_path.replace("{accent}", accent_color)

    body = f"""
    <!-- Left Accent Stripe -->
    <rect x="0" y="14" width="3.5" height="112" rx="1.75" fill="{accent_color}" />

    <!-- Tile Inner Glow -->
    <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="15" fill="{BG_MAIN}" />

    <!-- Corner Decorative Icon Background -->
    <g transform="translate({w-56}, 16)" opacity="0.35">
      <svg width="32" height="32" viewBox="0 0 32 32">
        {icon_rendered}
      </svg>
    </g>

    <!-- Tile Content -->
    <g transform="translate(26, 32)">
      <!-- Eyebrow Tag -->
      <g class="reveal">
        <text x="0" y="0" fill="{accent_color}" font-size="10" font-weight="700" letter-spacing="2" class="mono">[ TILE 0{index} ]</text>
      </g>

      <!-- Tile Action Title -->
      <g class="reveal-d1" transform="translate(0, 32)">
        <text x="0" y="0" fill="{TEXT_WHITE}" font-size="24" font-weight="800" letter-spacing="-0.3">{esc(title_text)}</text>
      </g>

      <!-- Tile Description -->
      <g class="reveal-d2" transform="translate(0, 54)">
        <text x="0" y="0" fill="{TEXT_MUTED}" font-size="13" font-weight="400">{esc(desc_text)}</text>
      </g>

      <!-- URL Badge & Animated Arrow -->
      <g class="reveal-d3" transform="translate(0, 80)">
        <text x="0" y="0" fill="{accent_color}" font-size="11" font-weight="600" class="mono">{esc(url_text)}</text>
        <g transform="translate(236, -8)" class="arrow-glide">
          <text x="0" y="8" fill="{accent_color}" font-size="17" font-weight="700">↗</text>
        </g>
      </g>
    </g>
"""
    return svg_envelope(w, h, title, desc, body)


# ==============================================================================
# CARD 3: GitHub Activity Analytics
# ==============================================================================
def render_activity_card(total, days, metrics):
    w, h = 960, 300
    title = "GitHub Activity Analytics — Arpit Tak"
    desc = f"Total contributions: {total}, active days: {metrics.get('active_days', 0)}"

    active_days = metrics.get("active_days", 0)
    cur_streak = metrics.get("current_streak", 0)
    longest_streak = metrics.get("longest_streak", 0)
    monthly = metrics.get("monthly", [])
    
    # 12 trailing months
    last_12 = monthly[-12:] if monthly else []
    best_month_pair = max(last_12, key=lambda x: x[1]) if last_12 else ("N/A", 0)
    best_month_label = "N/A"
    best_month_count = best_month_pair[1]
    if best_month_pair[0] != "N/A":
        try:
            best_dt = datetime.strptime(best_month_pair[0], "%Y-%m")
            best_month_label = best_dt.strftime("%b %Y")
        except Exception:
            best_month_label = best_month_pair[0]

    # Date span label
    date_range_label = "Past 12 Months"
    start_d = metrics.get("start_date")
    end_d = metrics.get("end_date")
    if start_d and end_d and start_d != "N/A" and end_d != "N/A":
        try:
            s_dt = datetime.strptime(str(start_d), "%Y-%m-%d")
            e_dt = datetime.strptime(str(end_d), "%Y-%m-%d")
            date_range_label = f"{s_dt.strftime('%b %Y')} – {e_dt.strftime('%b %Y')}"
        except Exception:
            date_range_label = f"{start_d} to {end_d}"

    # Generate Monthly Bar Histogram
    bars_svg = []
    if last_12:
        max_val = max(1, max(v for _, v in last_12))
        bar_area_width = 864
        num_bars = len(last_12)
        bar_width = 38
        gap = (bar_area_width - (num_bars * bar_width)) / max(1, num_bars - 1)
        
        max_bar_h = 60
        base_y = 236

        for i, (ym, count) in enumerate(last_12):
            bx = 48 + i * (bar_width + gap)
            bh = max_bar_h * (count / max_val) if max_val > 0 else 0
            bh = max(3.0, bh) if count > 0 else 2.0
            by = base_y - bh
            
            is_peak = count == best_month_count and count > 0
            bar_color = AQUA if is_peak else VIOLET
            
            try:
                m_label = datetime.strptime(ym, "%Y-%m").strftime("%b")
            except Exception:
                m_label = ym[5:]
                
            delay = 0.2 + (i * 0.04)
            stagger_style = "" if STATIC else f'style="animation-delay: {delay:.2f}s;"'
            
            bar_markup = f"""
        <!-- Month Bar {ym} -->
        <g class="bar-grow" {stagger_style}>
          <rect x="{bx:.1f}" y="{by:.1f}" width="{bar_width}" height="{bh:.1f}" rx="4" fill="{bar_color}" opacity="{0.95 if is_peak else 0.8}">
            <title>{esc(ym)}: {count} contributions</title>
          </rect>
        </g>
        <!-- Bar Value -->
        <text x="{bx + bar_width/2:.1f}" y="{by - 6:.1f}" fill="{TEXT_MUTED}" font-size="10" font-weight="600" text-anchor="middle" class="mono">{count}</text>
        <!-- Month Name -->
        <text x="{bx + bar_width/2:.1f}" y="{base_y + 18:.1f}" fill="{TEXT_DIM}" font-size="10" font-weight="500" text-anchor="middle" class="mono">{m_label}</text>
"""
            bars_svg.append(bar_markup)
    else:
        bars_svg.append(f'<text x="480" y="210" fill="{TEXT_MUTED}" font-size="13" text-anchor="middle">No contribution calendar data currently cached. Run workflow to populate.</text>')

    bars_content = "".join(bars_svg)

    body = f"""
    <!-- Header -->
    <g transform="translate(48, 36)">
      <g class="reveal">
        <text x="0" y="0" fill="{VIOLET}" font-size="10" font-weight="700" letter-spacing="2" class="mono">[ REAL-TIME ANALYTICS ]</text>
        <text x="0" y="24" fill="{TEXT_WHITE}" font-size="22" font-weight="800" letter-spacing="-0.3">GITHUB CONTRIBUTION METRICS</text>
      </g>
      <g class="reveal-d1" transform="translate(864, 14)">
        <text x="0" y="0" fill="{TEXT_DIM}" font-size="11" font-weight="600" text-anchor="end" class="mono">{esc(date_range_label)}</text>
      </g>
    </g>

    <!-- 4 Metric KPI Cards -->
    <g transform="translate(48, 82)">
      <!-- KPI 1: Total Contributions -->
      <g class="reveal-d1" transform="translate(0, 0)">
        <rect width="204" height="66" rx="8" fill="{BG_PANEL}" stroke="{BORDER}" stroke-width="1" />
        <text x="16" y="32" fill="{AQUA}" font-size="26" font-weight="800" class="mono">{total:,}</text>
        <text x="16" y="50" fill="{TEXT_MUTED}" font-size="9" font-weight="700" letter-spacing="1.5">TOTAL CONTRIBUTIONS</text>
      </g>

      <!-- KPI 2: Active Days -->
      <g class="reveal-d2" transform="translate(220, 0)">
        <rect width="204" height="66" rx="8" fill="{BG_PANEL}" stroke="{BORDER}" stroke-width="1" />
        <text x="16" y="32" fill="{VIOLET_LIGHT}" font-size="26" font-weight="800" class="mono">{active_days:,}</text>
        <text x="16" y="50" fill="{TEXT_MUTED}" font-size="9" font-weight="700" letter-spacing="1.5">ACTIVE DAYS</text>
      </g>

      <!-- KPI 3: Peak Month -->
      <g class="reveal-d3" transform="translate(440, 0)">
        <rect width="204" height="66" rx="8" fill="{BG_PANEL}" stroke="{BORDER}" stroke-width="1" />
        <text x="16" y="30" fill="{TEXT_WHITE}" font-size="20" font-weight="700">{esc(best_month_label)}</text>
        <text x="16" y="50" fill="{TEXT_MUTED}" font-size="9" font-weight="700" letter-spacing="1.5">PEAK MONTH · {best_month_count} COMMITS</text>
      </g>

      <!-- KPI 4: Streaks -->
      <g class="reveal-d4" transform="translate(660, 0)">
        <rect width="204" height="66" rx="8" fill="{BG_PANEL}" stroke="{BORDER}" stroke-width="1" />
        <text x="16" y="30" fill="{BLUE}" font-size="18" font-weight="700" class="mono">{cur_streak}d cur <tspan fill="{TEXT_DIM}">/ {longest_streak}d max</tspan></text>
        <text x="16" y="50" fill="{TEXT_MUTED}" font-size="9" font-weight="700" letter-spacing="1.5">COMMIT STREAKS</text>
      </g>
    </g>

    <!-- Monthly Activity Chart Area -->
    <g class="reveal-d3">
      <!-- Background track panel for chart -->
      <rect x="48" y="160" width="864" height="112" rx="10" fill="{BG_PANEL}" stroke="{BORDER}" stroke-width="1" />
      <line x1="48" y1="236" x2="912" y2="236" stroke="{BORDER_ACCENT}" stroke-width="0.75" />
      {bars_content}
    </g>
"""
    return svg_envelope(w, h, title, desc, body)


# ==============================================================================
# CARD 4: Featured Projects
# ==============================================================================
def render_project_card(index, name, tag, desc_text, tech_list, repo_url, accent_color, demo_url=""):
    w, h = 960, 200
    title = f"Featured Project 0{index}: {name} — Arpit Tak"
    desc = f"{name}: {desc_text}"

    # Build technology badges
    pills_markup = []
    px = 0
    for tech in tech_list:
        tw = len(tech) * 7.2 + 20
        pill = f"""
        <g transform="translate({px:.1f}, 0)">
          <rect width="{tw:.1f}" height="24" rx="6" fill="{BG_PANEL_ALT}" stroke="{BORDER_ACCENT}" stroke-width="0.75" />
          <text x="{tw/2:.1f}" y="15.5" fill="{TEXT_WHITE}" font-size="10.5" font-weight="600" text-anchor="middle">{esc(tech)}</text>
        </g>
"""
        pills_markup.append(pill)
        px += tw + 8

    tech_pills = "".join(pills_markup)
    action_text = f"github.com/{repo_url.replace('https://github.com/', '')} ↗"

    demo_markup = ""
    if demo_url:
        demo_clean = demo_url.replace("https://", "").replace("/", "")
        demo_markup = f'<text x="500" y="17" fill="{TEXT_DIM}" font-size="10.5" class="mono">LIVE: <tspan fill="{accent_color}">{esc(demo_clean)}</tspan></text>'

    body = f"""
    <!-- Subtle Watermark Background Index -->
    <text x="{w-54}" y="155" fill="{accent_color}" font-size="110" font-weight="900" text-anchor="end" opacity="0.05" class="mono">0{index}</text>

    <!-- Left Accent Border -->
    <rect x="0" y="20" width="4" height="160" rx="2" fill="{accent_color}" />

    <!-- Project Content -->
    <g transform="translate(48, 38)">
      <!-- Eyebrow & Category Tag -->
      <g class="reveal">
        <text x="0" y="0" fill="{accent_color}" font-size="10" font-weight="700" letter-spacing="2" class="mono">[ FEATURED PROJECT 0{index} ]</text>
        <rect x="180" y="-12" width="{len(tag)*6.8 + 16:.1f}" height="18" rx="4" fill="{accent_color}" fill-opacity="0.12" stroke="{accent_color}" stroke-opacity="0.3" stroke-width="0.75" />
        <text x="188" y="0.5" fill="{accent_color}" font-size="9.5" font-weight="700" letter-spacing="1" class="mono">{esc(tag)}</text>
      </g>

      <!-- Project Name Heading -->
      <g class="reveal-d1" transform="translate(0, 34)">
        <text x="0" y="0" fill="{TEXT_WHITE}" font-size="30" font-weight="800" letter-spacing="-0.3">{esc(name)}</text>
      </g>

      <!-- Project Description -->
      <g class="reveal-d2" transform="translate(0, 60)">
        <text x="0" y="0" fill="{TEXT_MUTED}" font-size="13.5" font-weight="400">{esc(desc_text)}</text>
      </g>

      <!-- Verified Tech Stack Pills -->
      <g class="reveal-d3" transform="translate(0, 84)">
        {tech_pills}
      </g>

      <!-- Action Footer Link / Repository -->
      <g class="reveal-d4" transform="translate(0, 126)">
        <rect width="260" height="26" rx="6" fill="{BG_PANEL}" stroke="{BORDER_ACCENT}" stroke-width="1" />
        <text x="12" y="17" fill="{accent_color}" font-size="11" font-weight="600" class="mono">{esc(action_text)}</text>
        {demo_markup}
      </g>
    </g>
"""
    return svg_envelope(w, h, title, desc, body)


# ==============================================================================
# CARD 5: Contribution Heatmap
# ==============================================================================
def render_contributions_heatmap(days, weeks):
    w, h = 960, 200
    title = "GitHub Contribution Heatmap — Arpit Tak"
    desc = f"52-week contribution calendar visualization ({len(days)} days recorded)."

    # Custom Heatmap Palette (Dark Editorial: Deep Slate -> Electric Violet -> Radiant Cyan)
    HEAT_PALETTE = [
        "#141c2e",  # Level 0: Empty cell (deep slate)
        "#3b2d71",  # Level 1: Low activity (deep violet)
        "#6d48d7",  # Level 2: Medium activity (electric violet)
        "#0ea5e9",  # Level 3: High activity (vivid cyan/blue)
        "#22d3ee",  # Level 4: Peak activity (radiant aqua)
    ]

    cell_size = 11.0
    cell_gap = 3.5
    step = cell_size + cell_gap
    start_x = 75.0
    start_y = 66.0

    cells_markup = []
    month_labels_markup = []

    # Map dates to counts
    date_map = {d["date"]: int(d.get("count", 0)) for d in days if d.get("date")}

    # Identify maximum count to compute level thresholds
    max_c = max(date_map.values()) if date_map else 0
    t1 = max(1, int(max_c * 0.2))
    t2 = max(2, int(max_c * 0.45))
    t3 = max(3, int(max_c * 0.75))

    # Render up to 53 weeks
    if weeks:
        render_weeks = weeks[-53:]
    else:
        # Construct synthetic 53 weeks from days if weeks structure missing
        render_weeks = []
        cur_w = []
        for d in days[-371:]:
            cur_w.append(d)
            if len(cur_w) == 7:
                render_weeks.append({"contributionDays": cur_w})
                cur_w = []
        if cur_w:
            render_weeks.append({"contributionDays": cur_w})

    seen_months = set()
    total_weeks = len(render_weeks)

    for col_idx, week in enumerate(render_weeks):
        week_days = week.get("contributionDays", [])
        col_x = start_x + (col_idx * step)

        # Check for month transition label
        for d in week_days:
            d_str = d.get("date", "")
            if d_str and len(d_str) >= 7:
                ym = d_str[:7]
                if ym not in seen_months and col_idx < total_weeks - 2:
                    seen_months.add(ym)
                    try:
                        m_name = datetime.strptime(ym, "%Y-%m").strftime("%b")
                        month_labels_markup.append(
                            f'<text x="{col_x:.1f}" y="{start_y - 8:.1f}" fill="{TEXT_MUTED}" font-size="10" font-weight="600" class="mono">{m_name}</text>'
                        )
                    except Exception:
                        pass
                break

        # Render 7 days in column
        for row_idx, day_obj in enumerate(week_days[:7]):
            cnt = int(day_obj.get("contributionCount", day_obj.get("count", 0)))
            d_date = day_obj.get("date", "")
            
            if cnt == 0:
                level = 0
            elif cnt <= t1:
                level = 1
            elif cnt <= t2:
                level = 2
            elif cnt <= t3:
                level = 3
            else:
                level = 4

            fill_color = HEAT_PALETTE[level]
            cell_y = start_y + (row_idx * step)

            # Staggered animation delay across columns
            delay = 0.05 + (col_idx * 0.012)
            stagger_style = "" if STATIC else f'style="animation: cellReveal 0.4s cubic-bezier(0.16, 1, 0.3, 1) {delay:.3f}s forwards; opacity: 0;"'

            cell_markup = f"""
        <rect x="{col_x:.1f}" y="{cell_y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{fill_color}" {stagger_style}>
          <title>{esc(d_date)}: {cnt} contributions</title>
        </rect>
"""
            cells_markup.append(cell_markup)

    all_cells = "".join(cells_markup)
    all_months = "".join(month_labels_markup)

    # Day of week labels (Mon, Wed, Fri)
    day_labels = f"""
      <text x="{start_x - 12:.1f}" y="{start_y + (1 * step) + 9:.1f}" fill="{TEXT_DIM}" font-size="9" font-weight="600" text-anchor="end" class="mono">Mon</text>
      <text x="{start_x - 12:.1f}" y="{start_y + (3 * step) + 9:.1f}" fill="{TEXT_DIM}" font-size="9" font-weight="600" text-anchor="end" class="mono">Wed</text>
      <text x="{start_x - 12:.1f}" y="{start_y + (5 * step) + 9:.1f}" fill="{TEXT_DIM}" font-size="9" font-weight="600" text-anchor="end" class="mono">Fri</text>
"""

    # Legend at bottom right
    legend_markup = []
    leg_x = 816.0
    leg_y = 176.0
    legend_markup.append(f'<text x="{leg_x - 8:.1f}" y="{leg_y + 9:.1f}" fill="{TEXT_DIM}" font-size="9.5" text-anchor="end" class="mono">Less</text>')
    for idx, c in enumerate(HEAT_PALETTE):
        legend_markup.append(f'<rect x="{leg_x + (idx * 14):.1f}" y="{leg_y:.1f}" width="10" height="10" rx="2" fill="{c}"/>')
    legend_markup.append(f'<text x="{leg_x + 5 * 14 + 6:.1f}" y="{leg_y + 9:.1f}" fill="{TEXT_DIM}" font-size="9.5" class="mono">More</text>')
    legend_content = "".join(legend_markup)

    body = f"""
    <!-- Header -->
    <g transform="translate(48, 34)">
      <g class="reveal">
        <text x="0" y="0" fill="{AQUA}" font-size="10" font-weight="700" letter-spacing="2" class="mono">[ CONTRIBUTION CALENDAR ]</text>
        <text x="0" y="18" fill="{TEXT_WHITE}" font-size="18" font-weight="800" letter-spacing="-0.2">52-WEEK ACTIVITY HEATMAP</text>
      </g>
    </g>

    <!-- Month Labels -->
    <g class="reveal-d1">
      {all_months}
    </g>

    <!-- Day Labels -->
    <g class="reveal-d1">
      {day_labels}
    </g>

    <!-- Heatmap Cells Grid -->
    <g>
      {all_cells}
    </g>

    <!-- Legend Footer -->
    <g class="reveal-d2">
      <text x="48" y="{leg_y + 9:.1f}" fill="{TEXT_DIM}" font-size="10" class="mono">Source: GitHub Contributions API · Electric Violet &amp; Aqua Spectrum</text>
      {legend_content}
    </g>
"""
    return svg_envelope(w, h, title, desc, body)


# ==============================================================================
# Main Generation & XML Validation Pipeline
# ==============================================================================
def save_and_validate(filename, svg_content):
    """Saves SVG to cards/ directory and asserts valid XML."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / filename
    out_path.write_text(svg_content, encoding="utf-8")
    
    # XML Validation Check
    try:
        ET.parse(out_path)
    except ET.ParseError as pe:
        print(f"[FATAL ERROR] Generated SVG {filename} failed XML validation: {pe}")
        raise


def main():
    print(f"=== Generating GitHub Profile SVG Cards (STATIC={STATIC}) ===")
    
    # Load contribution calendar data
    total, days, weeks, metrics = load_contributions()
    print(f"[DATA] Loaded {len(days)} days, {total} total contributions, {metrics.get('active_days', 0)} active days.")

    # 1. Hero Card
    hero_svg = render_hero_card()
    save_and_validate("01-hero.svg", hero_svg)
    print("  [OK] cards/01-hero.svg")

    # 2. Three Interactive Link Tiles
    link1 = render_link_tile(1, "BUILD", "Projects and experiments", "github.com/arpittak027", VIOLET, "code")
    save_and_validate("02-link-1.svg", link1)
    print("  [OK] cards/02-link-1.svg")

    link2 = render_link_tile(2, "EXPLORE", "My portfolio", "arpittak.netlify.app", AQUA, "compass")
    save_and_validate("02-link-2.svg", link2)
    print("  [OK] cards/02-link-2.svg")

    link3 = render_link_tile(3, "CONNECT", "Professional network", "linkedin.com/in/arpit-tak", BLUE, "network")
    save_and_validate("02-link-3.svg", link3)
    print("  [OK] cards/02-link-3.svg")

    # 3. GitHub Activity Card
    activity_svg = render_activity_card(total, days, metrics)
    save_and_validate("03-activity.svg", activity_svg)
    print("  [OK] cards/03-activity.svg")

    # 4. Featured Project 1: Outpost
    outpost_stack = ["Next.js", "TypeScript", "Gemini AI", "tldraw", "BlockNote", "Prisma", "PostgreSQL"]
    project1_svg = render_project_card(
        index=1,
        name="Outpost",
        tag="AGENTIC WORKSPACE",
        desc_text="AI-powered collaborative workspace with an infinite canvas and real-time collaboration.",
        tech_list=outpost_stack,
        repo_url="https://github.com/arpittak027/OUTPOST",
        accent_color=VIOLET,
        demo_url="https://outpost-arpit.netlify.app"
    )
    save_and_validate("04-project-1.svg", project1_svg)
    print("  [OK] cards/04-project-1.svg")

    # 5. Featured Project 2: Sur
    sur_stack = ["JavaScript", "Matter.js 2D", "Tweakpane", "HTML5 Canvas", "Glassmorphism UI"]
    project2_svg = render_project_card(
        index=2,
        name="Sur",
        tag="PHYSICS SIMULATION",
        desc_text="Interactive physics-based chime simulation with customized global roof architecture and glassmorphism UI.",
        tech_list=sur_stack,
        repo_url="https://github.com/arpittak027/Sur",
        accent_color=AQUA,
        demo_url="https://arpit-sur.netlify.app"
    )
    save_and_validate("04-project-2.svg", project2_svg)
    print("  [OK] cards/04-project-2.svg")

    # 6. Contribution Heatmap
    heatmap_svg = render_contributions_heatmap(days, weeks)
    save_and_validate("99-contributions.svg", heatmap_svg)
    print("  [OK] cards/99-contributions.svg")

    print("All 8 animated SVG cards successfully rendered and XML-validated.")


if __name__ == "__main__":
    main()
