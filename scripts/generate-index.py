#!/usr/bin/env python3
"""Scans WOL_ONTHEGO for HTML files and regenerates index.html."""

import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
INDEX = ROOT / "index.html"

SKIP_DIRS = {".git", ".claude", "node_modules", "worktrees", ".next", "scripts"}
SKIP_PATTERNS = [re.compile(p) for p in [
    r"\.claude/",
    r"node_modules/",
    r"worktrees/",
    r"\.next/",
]]

# ── Project metadata ──────────────────────────────────────────────────────────
# Maps folder name → (display name, hex color, emoji)
SECTION_META = {
    "ACR Roots":                    ("ACR Roots",                    "#f59e0b", "🌳"),
    "DurableSkillsintheAgeofAI":    ("Durable Skills in the Age of AI", "#6c63ff", "🧠"),
    "Soulful Synergy":              ("Soulful Synergy",              "#ec4899", "✨"),
    "Storytelling for Impact":      ("Storytelling for Impact",      "#f97316", "📖"),
    "WISE":                         ("WISE Scales",                  "#00c9a7", "🌍"),
    "Work Out Loud":                ("Work Out Loud",                "#3b82f6", "💬"),
}

# ── File-level display names / descriptions ───────────────────────────────────
FILE_META = {
    "index.html":                               ("Hub / Index",              "📋", "Main index or hub page."),
    "roots-prototype-standalone.html":          ("Roots Prototype (Standalone)", "🧪", "Self-contained prototype for the ACR Roots experience."),
    "roots-prototype.html":                     ("Roots Prototype",          "🔬", "Core prototype version of the ACR Roots platform."),
    "JLX_NYC_Summit_Brief.html":               ("JLX NYC Summit Brief",     "📋", "Summit brief for the JLX NYC Durable Skills event."),
    "jlx_venn_interactive_v3.html":            ("JLX Venn Interactive v3",  "⭕", "Interactive Venn diagram for the Durable Skills framework."),
    "soulful_meeting_client_facing.html":      ("Soulful Meeting (Client-Facing)", "✨", "Client-ready meeting facilitation tool."),
    "stfi-interactive-workbook.html":          ("STFI Interactive Workbook","📖", "Guided storytelling workbook for the STFI learning experience."),
    "WISE_Implementation_Map.html":            ("WISE Implementation Map",  "🗺️", "Detailed implementation map for WISE Scales deployments."),
    "WISE_Implementation_Map_FIXED.html":      ("WISE Implementation Map (Fixed)", "🗺️", "Fixed implementation map."),
    "wise-scales-decision-tree.html":          ("WISE Decision Tree",       "🌿", "Branching decision tool for WISE Scales pathways."),
    "wise_scoring_reference.html":             ("WISE Scoring Reference",   "📊", "Reference guide for WISE Scales scoring and assessment."),
    "jlx_outreach_tracker.html":              ("JLX Outreach Tracker",     "📡", "Track outreach contacts and status for the JLX Conference."),
    "MEIKE/index.html":                        ("MEIKE",                    "💡", "MEIKE project hub and learning experience."),
    "the-sensitivity-trap.html":               ("The Sensitivity Trap",     "🎯", "SixTheta module on navigating sensitive workplace dynamics."),
    "image-previews.html":                     ("Image Previews",           "🖼️", "SixTheta module image preview page."),
    "SHSAT_Irregularity_Guide_Prototype.html": ("SHSAT Irregularity Guide", "📝", "Prototype guide for SHSAT irregularity procedures."),
}

def should_skip(rel: str) -> bool:
    for pat in SKIP_PATTERNS:
        if pat.search(rel):
            return True
    return False

def find_html_files():
    """Returns {section_folder: [rel_path, ...]} skipping index.html itself."""
    sections = {}
    for html in sorted(ROOT.rglob("*.html")):
        rel = html.relative_to(ROOT)
        parts = rel.parts
        if parts[0] == "index.html" or should_skip(str(rel)):
            continue
        section = parts[0]
        if section not in SECTION_META:
            continue
        sections.setdefault(section, []).append(rel)
    return sections

def file_display(rel: Path):
    name = rel.name
    # Try exact filename match first
    meta = FILE_META.get(name)
    # Try with subfolder prefix (e.g. "MEIKE/index.html")
    if meta is None and len(rel.parts) >= 2:
        key = "/".join(rel.parts[-2:])
        meta = FILE_META.get(key)
    if meta:
        title, icon, desc = meta
    else:
        title = name.replace("-", " ").replace("_", " ").replace(".html", "").title()
        icon = "📄"
        desc = f"{rel}"
    return title, icon, desc

def card(rel: Path, color: str) -> str:
    title, icon, desc = file_display(rel)
    href = str(rel).replace("\\", "/")
    tag = rel.parts[1] if len(rel.parts) > 2 else rel.parent.name if rel.parent != Path(".") else "page"
    tag = tag.lower()
    return f"""
  <a class="card" href="{href}" style="--card-accent:{color};">
    <span class="card-icon">{icon}</span>
    <span class="card-title">{title}</span>
    <span class="card-desc">{desc}</span>
    <span class="card-tag">{tag}</span>
  </a>"""

def build_html(sections: dict) -> str:
    today = date.today().strftime("%B %-d, %Y")
    body_parts = []
    for folder, files in sections.items():
        display, color, _ = SECTION_META[folder]
        body_parts.append(f'\n<p class="section-label">{display}</p>\n<div class="grid">')
        for rel in files:
            body_parts.append(card(rel, color))
        body_parts.append("</div>")
    sections_html = "\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>WOL On The Go — Project Hub</title>
  <style>
    :root {{
      --bg: #0f1117; --surface: #1a1d27; --border: #2a2d3a;
      --accent: #6c63ff; --text: #e8eaf0; --muted: #8b90a0;
      --tag-bg: #232636; --radius: 12px; --gap: 18px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; min-height: 100vh; padding: 40px 24px 80px; }}
    header {{ max-width: 1100px; margin: 0 auto 48px; }}
    .logo {{ font-size: 11px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent); margin-bottom: 10px; }}
    h1 {{ font-size: clamp(28px, 4vw, 44px); font-weight: 800; letter-spacing: -0.02em; line-height: 1.15; }}
    .subtitle {{ margin-top: 10px; color: var(--muted); font-size: 15px; }}
    .updated {{ display: inline-block; margin-top: 14px; padding: 4px 12px; background: var(--tag-bg); border: 1px solid var(--border); border-radius: 999px; font-size: 12px; color: var(--muted); }}
    .grid {{ max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--gap); }}
    .section-label {{ max-width: 1100px; margin: 36px auto 14px; font-size: 11px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); padding-left: 2px; }}
    .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 22px 22px 20px; text-decoration: none; display: flex; flex-direction: column; gap: 8px; transition: border-color .18s, transform .15s, box-shadow .18s; position: relative; overflow: hidden; }}
    .card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--card-accent, var(--accent)); border-radius: var(--radius) var(--radius) 0 0; }}
    .card:hover {{ border-color: var(--card-accent, var(--accent)); transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,.35); }}
    .card-icon {{ font-size: 26px; line-height: 1; }}
    .card-title {{ font-size: 16px; font-weight: 700; color: var(--text); line-height: 1.3; }}
    .card-desc {{ font-size: 13px; color: var(--muted); line-height: 1.5; }}
    .card-tag {{ display: inline-block; margin-top: 4px; padding: 3px 9px; background: var(--tag-bg); border-radius: 6px; font-size: 11px; color: var(--muted); font-weight: 500; border: 1px solid var(--border); align-self: flex-start; }}
    hr.divider {{ max-width: 1100px; margin: 48px auto 0; border: none; border-top: 1px solid var(--border); }}
    footer {{ max-width: 1100px; margin: 20px auto 0; font-size: 12px; color: var(--muted); }}
  </style>
</head>
<body>
<header>
  <div class="logo">WOL On The Go</div>
  <h1>Project Hub</h1>
  <p class="subtitle">All your living sites, prototypes, and tools — one click away.</p>
  <span class="updated">Last updated: {today}</span>
</header>
{sections_html}
<hr class="divider" />
<footer>Auto-generated by scripts/generate-index.py — runs on every git commit.</footer>
</body>
</html>
"""

def main():
    sections = find_html_files()
    html = build_html(sections)
    current = INDEX.read_text() if INDEX.exists() else ""
    if html != current:
        INDEX.write_text(html)
        print(f"index.html updated ({sum(len(v) for v in sections.values())} files across {len(sections)} sections)")
    else:
        print("index.html unchanged")

if __name__ == "__main__":
    main()
