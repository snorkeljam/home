#!/usr/bin/env python3
"""Builds index.html from scripts/sites.json — only live GitHub Pages & external URLs."""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT   = Path(__file__).parent.parent
CONFIG = Path(__file__).parent / "sites.json"
INDEX  = ROOT / "index.html"

CSS = """
    :root {
      --bg: #0f1117; --surface: #1a1d27; --border: #2a2d3a;
      --accent: #6c63ff; --text: #e8eaf0; --muted: #8b90a0;
      --tag-bg: #232636; --radius: 12px; --gap: 18px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; min-height: 100vh; padding: 40px 24px 80px; }
    header { max-width: 1100px; margin: 0 auto 48px; }
    .logo { font-size: 11px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent); margin-bottom: 10px; }
    h1 { font-size: clamp(28px, 4vw, 44px); font-weight: 800; letter-spacing: -0.02em; line-height: 1.15; }
    .subtitle { margin-top: 10px; color: var(--muted); font-size: 15px; }
    .updated { display: inline-block; margin-top: 14px; padding: 4px 12px; background: var(--tag-bg); border: 1px solid var(--border); border-radius: 999px; font-size: 12px; color: var(--muted); }
    .grid { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--gap); }
    .section-label { max-width: 1100px; margin: 36px auto 14px; font-size: 11px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); padding-left: 2px; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 22px 22px 20px; text-decoration: none; display: flex; flex-direction: column; gap: 8px; transition: border-color .18s, transform .15s, box-shadow .18s; position: relative; overflow: hidden; }
    .card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--card-accent, var(--accent)); border-radius: var(--radius) var(--radius) 0 0; }
    .card:hover { border-color: var(--card-accent, var(--accent)); transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,.35); }
    .card-icon { font-size: 26px; line-height: 1; }
    .card-title { font-size: 16px; font-weight: 700; color: var(--text); line-height: 1.3; }
    .card-desc { font-size: 13px; color: var(--muted); line-height: 1.5; }
    .card-tag { display: inline-block; margin-top: 4px; padding: 3px 9px; background: var(--tag-bg); border-radius: 6px; font-size: 11px; color: var(--muted); font-weight: 500; border: 1px solid var(--border); align-self: flex-start; }
    hr.divider { max-width: 1100px; margin: 48px auto 0; border: none; border-top: 1px solid var(--border); }
    footer { max-width: 1100px; margin: 20px auto 0; font-size: 12px; color: var(--muted); }
"""

def pages_live(user: str, repo: str) -> bool:
    """Returns True if the repo has GitHub Pages enabled."""
    result = subprocess.run(
        ["gh", "api", f"repos/{user}/{repo}/pages"],
        capture_output=True, text=True
    )
    return result.returncode == 0

def pages_base(user: str, repo: str) -> str:
    return f"https://{user}.github.io/{repo}"

def card_html(url: str, name: str, icon: str, desc: str, tag: str, color: str) -> str:
    return f"""
  <a class="card" href="{url}" target="_blank" rel="noopener" style="--card-accent:{color};">
    <span class="card-icon">{icon}</span>
    <span class="card-title">{name}</span>
    <span class="card-desc">{desc}</span>
    <span class="card-tag">{tag}</span>
  </a>"""

def build_html(config: dict) -> str:
    user    = config["github_user"]
    today   = date.today().strftime("%B %-d, %Y")
    sections_html = []
    total_cards   = 0

    for section_name, section in config["sections"].items():
        color = section.get("color", "#6c63ff")
        cards = []

        # GitHub Pages repos
        for repo, repo_cfg in section.get("repos", {}).items():
            if not pages_live(user, repo):
                print(f"  skip {repo} — no live Pages", file=sys.stderr)
                continue
            base = pages_base(user, repo)
            for page in repo_cfg.get("pages", []):
                path = page["path"]
                url  = f"{base}/{path}" if path != "index.html" else f"{base}/"
                cards.append(card_html(url, page["name"], page["icon"], page["desc"], page["tag"], color))

        # External / Vercel URLs
        for ext in section.get("external", []):
            cards.append(card_html(ext["url"], ext["name"], ext["icon"], ext["desc"], ext["tag"], color))

        if not cards:
            continue

        total_cards += len(cards)
        sections_html.append(f'\n<p class="section-label">{section_name}</p>\n<div class="grid">{"".join(cards)}\n</div>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>WOL On The Go — Project Hub</title>
  <style>{CSS}</style>
</head>
<body>
<header>
  <div class="logo">WOL On The Go</div>
  <h1>Project Hub</h1>
  <p class="subtitle">All your living sites, prototypes, and tools — one click away.</p>
  <span class="updated">Last updated: {today}</span>
</header>
{"".join(sections_html)}
<hr class="divider" />
<footer>Auto-generated by scripts/generate-index.py — edit scripts/sites.json to add new projects.</footer>
</body>
</html>
"""

def main():
    config  = json.loads(CONFIG.read_text())
    html    = build_html(config)
    current = INDEX.read_text() if INDEX.exists() else ""
    if html != current:
        INDEX.write_text(html)
        print("index.html updated")
    else:
        print("index.html unchanged")

if __name__ == "__main__":
    main()
