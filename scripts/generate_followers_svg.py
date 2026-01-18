#!/usr/bin/env python3
"""
Gera .github/followers.svg com layout:
[ícone] 1557 followers
linha fina
avatares circulares pequenos sobrepostos

Config via env:
- USERNAME (default: Otto-Samuel)
- GITHUB_TOKEN (opcional, aumenta rate limit)
- MAX_AVATARS (default: 8)
- AVATAR_SIZE (default: 28)
"""
import os, sys, math, requests

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

USERNAME = os.getenv("USERNAME") or "Otto-Samuel"
TOKEN = os.getenv("GITHUB_TOKEN")
MAX_AVATARS = int(os.getenv("MAX_AVATARS", "8"))
AVATAR_SIZE = int(os.getenv("AVATAR_SIZE", "28"))

PER_PAGE = 100
headers = {"Accept": "application/vnd.github.v3+json"}
if TOKEN:
    headers["Authorization"] = f"token {TOKEN}"

# fetch followers with pagination
followers = []
page = 1
while True:
    resp = requests.get(f"https://api.github.com/users/{USERNAME}/followers",
                        params={"per_page": PER_PAGE, "page": page},
                        headers=headers)
    if resp.status_code != 200:
        print("Erro ao buscar seguidores:", resp.status_code, resp.text, file=sys.stderr)
        sys.exit(1)
    batch = resp.json()
    if not batch:
        break
    followers.extend(batch)
    if len(batch) < PER_PAGE:
        break
    page += 1

total = len(followers)
visible = followers[:min(len(followers), MAX_AVATARS)]
show = len(visible)

# layout
pad_x = 12
pad_y = 10
icon_size = 16
text_gap = 8
sep_gap_top = 8
sep_height = 1
avatars_gap_top = 8
overlap = int(AVATAR_SIZE * 0.35)  # quanto os avatares se sobrepõem
avatars_width = AVATAR_SIZE + (show - 1) * (AVATAR_SIZE - overlap) if show > 0 else 0

# compute svg size
content_width = max(240, avatars_width + pad_x*2 + 80)
title_height = max(icon_size, AVATAR_SIZE)
svg_width = content_width
svg_height = pad_y*2 + title_height + sep_gap_top + sep_height + avatars_gap_top + AVATAR_SIZE

# start svg
svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">')
svg.append(f'<rect rx="4" width="100%" height="100%" fill="#0d1117"/>')
svg.append('<style>')
svg.append('  .label{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; font-size:14px; fill:#9aa4ad; }')
svg.append('  .count{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; font-weight:600; font-size:15px; fill:#1e90ff; }')
svg.append('</style>')

# user/group icon (left)
icon_x = pad_x
icon_y = pad_y + (title_height - icon_size) / 2
svg.append(f'<g transform="translate({icon_x},{icon_y})" fill="#9aa4ad" opacity="0.9">')
svg.append('  <path d="M5.5 3.5a2 2 0 100 4 2 2 0 000-4zM2 5.5a3.5 3.5 0 115.898 2.549 5.507 5.507 0 013.034 4.084.75.75 0 11-1.482.235 4.001 4.001 0 00-7.9 0 .75.75 0 01-1.482-.236A5.507 5.507 0 013.102 8.05 3.49 3.49 0 012 5.5zM11 4a.75.75 0 100 1.5 1.5 1.5 0 01.666 2.844.75.75 0 00-.416.672v.352a.75.75 0 00.574.73c1.2.289 2.162 1.2 2.522 2.372a.75.75 0 101.434-.44 5.01 5.01 0 00-2.56-3.012A3 3 0 0011 4z"/>')
svg.append('</g>')

# text (count + label)
text_x = icon_x + icon_size + text_gap
text_y_pos = pad_y + (title_height/2) + 5
svg.append(f'<text x="{text_x}" y="{text_y_pos}" class="count">{total}</text>')
svg.append(f'<text x="{text_x + 38}" y="{text_y_pos}" class="label">followers</text>')

# separator line
sep_y = pad_y + title_height + sep_gap_top
svg.append(f'<rect x="{pad_x}" y="{sep_y}" width="{svg_width - pad_x*2}" height="{sep_height}" fill="#23272b" opacity="0.6"/>')

# avatars
avatars_start_x = pad_x
avatars_y = sep_y + sep_height + avatars_gap_top

svg.append('<defs>')
for i in range(show):
    cx = avatars_start_x + i * (AVATAR_SIZE - overlap) + AVATAR_SIZE/2
    cy = avatars_y + AVATAR_SIZE/2
    svg.append(f'<clipPath id="c{i}"><circle cx="{cx}" cy="{cy}" r="{AVATAR_SIZE/2}"/></clipPath>')
svg.append('</defs>')

for i, f in enumerate(visible):
    login = esc(f.get("login",""))
    avatar = f.get("avatar_url","")
    profile = f.get("html_url","")
    if not avatar:
        continue
    x = avatars_start_x + i * (AVATAR_SIZE - overlap)
    y = avatars_y
    sep = "&" if "?" in avatar else "?"
    avatar_url = f"{avatar}{sep}s={AVATAR_SIZE*2}"
    svg.append(f'<a href="{esc(profile)}" target="_blank" rel="noopener noreferrer">')
    svg.append(f'  <image x="{x}" y="{y}" width="{AVATAR_SIZE}" height="{AVATAR_SIZE}" href="{esc(avatar_url)}" clip-path="url(#c{i})" />')
    svg.append('</a>')
    cx = x + AVATAR_SIZE/2
    cy = y + AVATAR_SIZE/2
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{AVATAR_SIZE/2 - 0.8}" fill="none" stroke="#0d1117" stroke-width="2"/>')

svg.append('</svg>')

out_dir = ".github"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "followers.svg")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))

print(f"SVG gerado em {out_path} (followers: {total}, mostrando {show})")