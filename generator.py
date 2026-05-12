"""
generator.py  –  Reads all .txt files from posts/ and rebuilds index.html
"""

import os
import re
import markdown
from datetime import datetime
from pathlib import Path
from jinja2 import Template

POSTS_DIR = Path("posts")
OUTPUT_FILE = Path("docs/index.html")

# ── Jinja2 template (single-page, all posts) ────────────────────────────────
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{ site_title }}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --ink:       #1a1714;
      --paper:     #f5f0e8;
      --cream:     #ede7d9;
      --accent:    #8b3a2a;
      --accent2:   #c4762a;
      --muted:     #7a736a;
      --rule:      #c8bfb0;
    }

    html { scroll-behavior: smooth; }

    body {
      background: var(--paper);
      color: var(--ink);
      font-family: 'Source Serif 4', Georgia, serif;
      font-size: 18px;
      line-height: 1.75;
      min-height: 100vh;
    }

    /* ── Masthead ─────────────────────────────────── */
    header {
      background: var(--ink);
      color: var(--paper);
      padding: 3.5rem 2rem 3rem;
      text-align: center;
      position: relative;
      overflow: hidden;
    }
    header::before {
      content: '';
      position: absolute;
      inset: 0;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 39px,
        rgba(255,255,255,.04) 40px
      );
    }
    .site-title {
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(2.4rem, 6vw, 4rem);
      font-weight: 700;
      letter-spacing: .03em;
      position: relative;
    }
    .site-title span { color: var(--accent2); font-style: italic; }
    .site-tagline {
      margin-top: .5rem;
      font-size: .95rem;
      letter-spacing: .15em;
      text-transform: uppercase;
      opacity: .55;
      position: relative;
    }
    .header-rule {
      width: 80px;
      height: 2px;
      background: var(--accent2);
      margin: 1.4rem auto 0;
      position: relative;
    }

    /* ── Layout ───────────────────────────────────── */
    main {
      max-width: 740px;
      margin: 0 auto;
      padding: 3rem 1.5rem 6rem;
    }

    .post-count {
      text-align: right;
      font-size: .8rem;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 2.5rem;
    }

    /* ── Post card ────────────────────────────────── */
    article {
      border-top: 1px solid var(--rule);
      padding: 2.8rem 0 1rem;
      animation: fadeUp .5s ease both;
    }
    article:first-of-type { border-top: none; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(18px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .post-meta {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.1rem;
    }
    .post-date {
      font-size: .78rem;
      letter-spacing: .13em;
      text-transform: uppercase;
      color: var(--muted);
    }
    .post-tag {
      font-size: .72rem;
      letter-spacing: .1em;
      text-transform: uppercase;
      background: var(--accent);
      color: #fff;
      padding: .15em .7em;
      border-radius: 2px;
    }

    .post-title {
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(1.55rem, 4vw, 2rem);
      font-weight: 700;
      line-height: 1.25;
      margin-bottom: 1.1rem;
      color: var(--ink);
    }

    /* markdown body */
    .post-body { color: #2c2824; }
    .post-body h1, .post-body h2, .post-body h3 {
      font-family: 'Playfair Display', Georgia, serif;
      margin: 1.8rem 0 .7rem;
      line-height: 1.3;
      color: var(--ink);
    }
    .post-body h1 { font-size: 1.55rem; }
    .post-body h2 { font-size: 1.3rem; }
    .post-body h3 { font-size: 1.1rem; }
    .post-body p  { margin-bottom: 1rem; }
    .post-body strong { color: var(--ink); font-weight: 600; }
    .post-body em     { font-style: italic; color: var(--accent); }
    .post-body ul, .post-body ol {
      margin: .8rem 0 1rem 1.4rem;
    }
    .post-body li { margin-bottom: .3rem; }
    .post-body blockquote {
      border-left: 3px solid var(--accent2);
      padding-left: 1.2rem;
      margin: 1.2rem 0;
      color: var(--muted);
      font-style: italic;
    }
    .post-body code {
      font-family: 'Courier New', monospace;
      font-size: .88em;
      background: var(--cream);
      padding: .1em .35em;
      border-radius: 3px;
    }
    .post-body pre code {
      display: block;
      padding: 1rem;
      overflow-x: auto;
      border-left: 3px solid var(--accent);
    }
    .post-body a { color: var(--accent); }

    /* ornament between posts */
    .ornament {
      text-align: center;
      color: var(--rule);
      font-size: 1.3rem;
      padding: 1.5rem 0 0;
      user-select: none;
    }

    /* ── Empty state ──────────────────────────────── */
    .empty {
      text-align: center;
      padding: 5rem 1rem;
      color: var(--muted);
    }
    .empty h2 {
      font-family: 'Playfair Display', serif;
      font-size: 1.6rem;
      margin-bottom: .8rem;
    }
    .empty code {
      background: var(--cream);
      padding: .2em .5em;
      border-radius: 3px;
      font-size: .9rem;
    }

    /* ── Footer ───────────────────────────────────── */
    footer {
      text-align: center;
      padding: 2rem;
      font-size: .78rem;
      letter-spacing: .1em;
      text-transform: uppercase;
      color: var(--muted);
      border-top: 1px solid var(--rule);
    }

    /* ── Back to top ──────────────────────────────── */
    .back-top {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: var(--ink);
      color: var(--paper);
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      text-decoration: none;
      border-radius: 2px;
      opacity: 0;
      transition: opacity .3s;
    }
    .back-top.visible { opacity: 1; }
  </style>
</head>
<body>

<header>
  <h1 class="site-title">{{ site_title }}</h1>
  <p class="site-tagline">{{ site_tagline }}</p>
  <div class="header-rule"></div>
</header>

<main>

  {% if posts %}
  <p class="post-count">{{ posts|length }} post{% if posts|length != 1 %}s{% endif %}</p>

  {% for post in posts %}
  <article style="animation-delay: {{ loop.index0 * 0.07 }}s">
    <div class="post-meta">
      <span class="post-date">{{ post.date }}</span>
      <span class="post-tag">Post #{{ loop.index }}</span>
    </div>
    <h2 class="post-title">{{ post.title }}</h2>
    <div class="post-body">{{ post.html | safe }}</div>
    {% if not loop.last %}<div class="ornament">✦ ✦ ✦</div>{% endif %}
  </article>
  {% endfor %}

  {% else %}
  <div class="empty">
    <h2>No posts yet</h2>
    <p>Drop a <code>.txt</code> file into the <code>posts/</code> folder to get started.</p>
  </div>
  {% endif %}

</main>

<footer>
  Generated {{ generated_at }} &nbsp;·&nbsp; {{ posts|length }} post{% if posts|length != 1 %}s{% endif %}
</footer>

<a class="back-top" href="#" title="Back to top" id="backTop">↑</a>

<script>
  const btn = document.getElementById('backTop');
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  });
</script>

</body>
</html>
"""


def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", text)


def extract_title(content: str, filename: str) -> str:
    """Use first # heading, first line, or filename as title."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line:
            return line[:80]
    return Path(filename).stem.replace("-", " ").replace("_", " ").title()


def file_date(filepath: Path) -> str:
    ts = filepath.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime("%B %d, %Y")


def build_site(site_title="Utah Geospatial Opportunities", site_tagline="GIS, Remote Sensing and GeoAI"):
    POSTS_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    txt_files = sorted(POSTS_DIR.glob("*.txt"), key=lambda f: f.name, reverse=True)

    posts = []
    for f in txt_files:
        raw = f.read_text(encoding="utf-8")
        title = extract_title(raw, f.name)
        html = markdown.markdown(raw, extensions=["extra", "nl2br"])
        posts.append({
            "title": title,
            "html": html,
            "date": file_date(f),
            "slug": slugify(f.stem),
        })

    tmpl = Template(TEMPLATE)
    rendered = tmpl.render(
        site_title=site_title,
        site_tagline=site_tagline,
        posts=posts,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    OUTPUT_FILE.write_text(rendered, encoding="utf-8")
    print(f"[generator] Built — {len(posts)} post(s) → {OUTPUT_FILE}")


if __name__ == "__main__":
    build_site()
