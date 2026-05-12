# Geospatial Job Oppotunities Blog — Setup & Usage

A zero-database, single-page blog that rebuilds itself whenever you drop a `.txt` file into the `posts/` folder.

---

## 1. Install Python dependencies (once)

```bash
pip install -r requirements.txt
```

---

## 2. Start the watcher

```bash
python watcher.py
```

Optional — customize your site title and tagline:

```bash
python watcher.py --title "Jane's Notes" --tagline "Ideas, half-formed & otherwise"
```

The site will do an **initial build** immediately, then watch for changes.

---

## 3. Write posts

Drop any `.txt` file into the `posts/` folder:

```
posts/
  2026-01-02.txt
  2026-02-02.txt
  2026-03-02.txt
```

The site rebuilds **automatically** — no command needed. The posts are built with the most recent uploaded. The filename is saved with the date to position the post in the blog. 

### Supported Markdown

| Syntax | Result |
|---|---|
| `# Heading` | Large heading (becomes post title) |
| `## Sub-heading` | Section heading |
| `**bold**` | **bold** |
| `*italic*` | *italic* |
| `- item` | Bullet list |
| `> quote` | Blockquote |
| `` `code` `` | Inline code |

> **Tip:** The first `# Heading` in your file becomes the post title on the site.  
> If there's no heading, the first line of text is used instead.

---

## 4. View the site

https://aish-chan.github.io/USU-Geospatial/

---

## File structure

```
blog_generator/
├── posts/              ← Drop .txt files here
│   ├── welcome.txt
│   └── on-plain-text.txt
├── docs/
│   └── index.html      ← The generated site (open this)
├── generator.py        ← Rebuilds the site
├── watcher.py          ← Watches posts/ and triggers rebuilds
├── requirements.txt
└── README.md
```

---

## Deploy (optional)

The entire site is the single file `output/index.html`.  
Upload it anywhere: GitHub Pages, Netlify, Vercel, or any web host.
