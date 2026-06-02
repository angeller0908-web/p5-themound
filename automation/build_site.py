#!/usr/bin/env python3
"""
The Mound fan-wiki — static article generator (Plan B).

Turns a Markdown file (with YAML-ish frontmatter) into a full HTML article that
matches the hand-built pages, then (optionally) inserts a card into the News hub
and a <url> into sitemap.xml. Designed to be the "publish" target for an
automated content pipeline (RSS -> LLM -> Markdown -> THIS -> HTML -> git push).

Usage:
    python3 build_site.py content/my-article.md            # build + index
    python3 build_site.py content/my-article.md --dry-run  # print, change nothing
    python3 build_site.py --all                            # build every .md in content/

Frontmatter keys (between the first pair of --- lines):
    title:        (required) full article title
    slug:         (optional) output filename; default = markdown filename
    description:  (required) meta description / OG description
    keywords:     (optional) comma-separated
    image:        (optional) filename in images/ (e.g. article_release_platforms.png)
    image_alt:    (optional)
    hero_title:   (optional) big H1 shown in hero; default = title
    crumb:        (optional) short breadcrumb label; default = title
    date:         (optional) YYYY-MM-DD published; default = today (UTC)
    date_modified:(optional) YYYY-MM-DD; default = today (UTC)
    read_time:    (optional) integer minutes; default = computed from word count
    quick_facts:  (optional) list of "Label | Value" strings -> the teal summary box
    faq:          (optional) list of {q, a} -> visible FAQ + FAQPage JSON-LD

Body: standard Markdown after the frontmatter (## / ### / paragraphs / lists /
links / **bold** / tables / raw HTML all allowed).
"""

import argparse
import datetime as _dt
import html
import json
import re
import sys
from pathlib import Path

# ---- paths -----------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                       # p5-themound/
ARTICLES_DIR = ROOT / "pages" / "articles"
HUB_FILE = ARTICLES_DIR / "index.html"
SITEMAP_FILE = ROOT / "sitemap.xml"
CONTENT_DIR = HERE / "content"

SITE = "https://themound.online"
GA_ID = "G-XV21PXX090"


# ---- tiny frontmatter + markdown -------------------------------------------
def parse_frontmatter(text):
    """Return (meta: dict, body: str). Supports a minimal YAML subset:
    scalars, `key:` followed by `- ` list items, and `- q:/a:` blocks for faq."""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    meta, key, lines = {}, None, raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        # list item under current key
        m_item = re.match(r"^\s*-\s+(.*)$", line)
        if m_item and key:
            meta.setdefault(key, [])
            # faq block: "- q: ..." then following indented "a: ..."
            mq = re.match(r"^q:\s*(.*)$", m_item.group(1).strip())
            if mq:
                entry = {"q": _unquote(mq.group(1))}
                j = i + 1
                while j < len(lines) and re.match(r"^\s+\S", lines[j]) and not re.match(r"^\s*-\s", lines[j]):
                    ma = re.match(r"^\s*a:\s*(.*)$", lines[j])
                    if ma:
                        entry["a"] = _unquote(ma.group(1))
                    j += 1
                meta[key].append(entry)
                i = j
                continue
            meta[key].append(_unquote(m_item.group(1).strip()))
            i += 1
            continue
        # key: value
        m_kv = re.match(r"^([A-Za-z_]\w*):\s*(.*)$", line)
        if m_kv:
            key = m_kv.group(1)
            val = m_kv.group(2).strip()
            meta[key] = _unquote(val) if val else []
        i += 1
    return meta, body


def _unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def markdown_to_html(md):
    """Use python-markdown if available; else a small built-in converter."""
    try:
        import markdown  # type: ignore
        return markdown.markdown(md, extensions=["tables", "attr_list", "sane_lists"])
    except Exception:
        return _mini_markdown(md)


def _mini_markdown(md):
    out, lines, i = [], md.splitlines(), 0
    def inline(t):
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
        return t
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.lstrip().startswith("<"):           # raw HTML passthrough
            out.append(line); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1)); out.append(f"<h{lvl}>{inline(m.group(2).strip())}</h{lvl}>"); i += 1; continue
        if re.match(r"^\s*[-*]\s+", line):
            out.append("<ul>")
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                out.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i]).strip()) + "</li>"); i += 1
            out.append("</ul>"); continue
        para = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|\s*[-*]\s|<)", lines[i]):
            para.append(lines[i]); i += 1
        out.append("<p>" + inline(" ".join(p.strip() for p in para)) + "</p>")
    return "\n".join(out)


# ---- rendering -------------------------------------------------------------
def esc(s):
    return html.escape(str(s), quote=True)


def build_jsonld(meta, slug):
    url = f"{SITE}/pages/articles/{slug}.html"
    img = f"{SITE}/images/{meta.get('image', 'hero-banner.png')}"
    graph = [
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "News & Guides", "item": f"{SITE}/pages/articles/index.html"},
                {"@type": "ListItem", "position": 3, "name": meta.get("crumb", meta["title"]), "item": url},
            ],
        },
        {
            "@type": "Article",
            "headline": meta["title"],
            "description": meta.get("description", ""),
            "image": img,
            "datePublished": meta["_date"],
            "dateModified": meta["_date_mod"],
            "inLanguage": "en",
            "author": {"@type": "Organization", "name": "The Mound Fan Wiki"},
            "publisher": {"@type": "Organization", "name": "The Mound Fan Wiki"},
            "about": {"@type": "VideoGame", "name": "The Mound: Omen of Cthulhu"},
        },
    ]
    faq = meta.get("faq") or []
    if faq:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f.get("q", ""),
                 "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", f.get("a", ""))}}
                for f in faq
            ],
        })
    doc = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(doc, ensure_ascii=False, indent=2)


def render_quick_facts(meta):
    qf = meta.get("quick_facts") or []
    if not qf:
        return ""
    rows = []
    for item in qf:
        if "|" in item:
            label, value = item.split("|", 1)
        else:
            label, value = item, ""
        rows.append(f"            <tr><td>{esc(label.strip())}</td><td>{value.strip()}</td></tr>")
    title = meta.get("quick_facts_title", "The Quick Answer")
    return (
        '        <div class="key-facts">\n'
        f"          <h2>{esc(title)}</h2>\n"
        "          <table>\n" + "\n".join(rows) + "\n          </table>\n"
        "        </div>\n"
    )


def render_faq(meta):
    faq = meta.get("faq") or []
    if not faq:
        return ""
    parts = ['        <div class="faq">', "          <h2>FAQ</h2>"]
    for f in faq:
        parts.append(f"          <h3>{esc(f.get('q',''))}</h3>")
        parts.append(f"          <p>{f.get('a','')}</p>")
    parts.append("        </div>")
    return "\n".join(parts) + "\n"


def render_article(meta, body_md):
    slug = meta["slug"]
    body_html = markdown_to_html(body_md).strip()
    # indent body for readability
    body_html = "\n".join("        " + ln for ln in body_html.splitlines())
    img = meta.get("image", "hero-banner.png")
    img_alt = meta.get("image_alt", meta["title"])
    crumb = meta.get("crumb", meta["title"])
    return TEMPLATE.replace("{{TITLE}}", esc(meta["title"])) \
        .replace("{{DESCRIPTION}}", esc(meta.get("description", ""))) \
        .replace("{{KEYWORDS}}", esc(meta.get("keywords", ""))) \
        .replace("{{SLUG}}", slug) \
        .replace("{{OG_IMAGE}}", f"{SITE}/images/{img}") \
        .replace("{{IMAGE_LOCAL}}", f"../../images/{img}") \
        .replace("{{IMAGE_ALT}}", esc(img_alt)) \
        .replace("{{HERO_TITLE}}", esc(meta.get("hero_title", meta["title"]))) \
        .replace("{{CRUMB}}", esc(crumb)) \
        .replace("{{DATE}}", esc(meta["_date_disp"])) \
        .replace("{{DATE_MOD}}", esc(meta["_date_mod_disp"])) \
        .replace("{{READ}}", str(meta["_read"])) \
        .replace("{{JSONLD}}", build_jsonld(meta, slug)) \
        .replace("{{QUICK_FACTS}}", render_quick_facts(meta)) \
        .replace("{{FAQ}}", render_faq(meta)) \
        .replace("{{BODY}}", body_html)


# ---- hub + sitemap upserts -------------------------------------------------
def upsert_hub_card(meta, dry=False):
    slug = meta["slug"]
    href = f"{slug}.html"
    hub = HUB_FILE.read_text(encoding="utf-8")
    if href in hub:
        print(f"  hub: card for {href} already present — skip")
        return
    # Always insert at the TOP of the grid (newest articles first).
    # New card never gets card-purple so it sits cleanly at position 1.
    card = f'''
        <!-- Article: {esc(meta['title'])} -->
        <article class="card animate-fade-in" style="display:flex; flex-direction:column;">
          <div class="card-image-wrapper">
            <a href="{href}"><img src="../../images/{meta.get('image','hero-banner.png')}" alt="{esc(meta.get('image_alt', meta['title']))}"></a>
          </div>
          <h3 class="card-title" style="font-size: 1.2rem;">
            <a href="{href}" style="color: inherit; text-decoration: none;">{esc(meta.get('card_title', meta['title']))}</a>
          </h3>
          <p class="card-text" style="font-size:0.92rem;">{esc(meta.get('card_text', meta.get('description','')))}</p>
          <div class="card-meta"><span>📅 {esc(meta['_date_disp'])}</span> • <span>👤 Wiki Editors</span></div>
          <a href="{href}" class="footer-link" style="margin-top:auto;">Read more →</a>
        </article>
'''
    # Insert right after the opening <div class="grid"> tag
    anchor = '<div class="grid">\n'
    if anchor not in hub:
        anchor = '<div class="grid">'  # fallback without trailing newline
    new_hub = hub.replace(anchor, anchor + card, 1)
    if dry:
        print(f"  hub: WOULD insert card for {href} (at top)")
        return
    HUB_FILE.write_text(new_hub, encoding="utf-8")
    print(f"  hub: inserted card for {href} (at top)")


def upsert_sitemap(meta, dry=False):
    slug = meta["slug"]
    loc = f"{SITE}/pages/articles/{slug}.html"
    sm = SITEMAP_FILE.read_text(encoding="utf-8")
    if loc in sm:
        print(f"  sitemap: {loc} already present — skip")
        return
    entry = (
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{meta['_date_mod']}</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "    <priority>0.8</priority>\n"
        "  </url>\n\n"
    )
    new_sm = sm.replace("</urlset>", entry + "</urlset>", 1)
    if dry:
        print(f"  sitemap: WOULD insert {loc}")
        return
    SITEMAP_FILE.write_text(new_sm, encoding="utf-8")
    print(f"  sitemap: inserted {loc}")


# ---- driver ----------------------------------------------------------------
def normalize_meta(meta, md_path):
    if "title" not in meta:
        raise SystemExit(f"ERROR: {md_path} is missing required 'title' in frontmatter")
    meta.setdefault("slug", md_path.stem)
    today = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    meta["_date"] = (meta.get("date") or today)
    meta["_date_mod"] = (meta.get("date_modified") or today)
    # display form: "June 1, 2026"
    def disp(d):
        try:
            return _dt.datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")
        except Exception:
            return d
    meta["_date_disp"] = disp(meta["_date"])
    meta["_date_mod_disp"] = disp(meta["_date_mod"])
    return meta


def build_one(md_path, dry=False, index=True):
    meta, body = parse_frontmatter(Path(md_path).read_text(encoding="utf-8"))
    meta = normalize_meta(meta, Path(md_path))
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    meta["_read"] = int(meta.get("read_time") or max(2, round(words / 200)))
    html_out = render_article(meta, body)
    out_path = ARTICLES_DIR / f"{meta['slug']}.html"
    print(f"• {md_path}  ->  pages/articles/{meta['slug']}.html  ({words} words)")
    if dry:
        print("  [dry-run] not writing file")
    else:
        out_path.write_text(html_out, encoding="utf-8")
    if index:
        upsert_hub_card(meta, dry=dry)
        upsert_sitemap(meta, dry=dry)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Build The Mound articles from Markdown.")
    ap.add_argument("markdown", nargs="?", help="path to a .md file in content/")
    ap.add_argument("--all", action="store_true", help="build every .md in content/")
    ap.add_argument("--dry-run", action="store_true", help="print actions, write nothing")
    ap.add_argument("--no-index", action="store_true", help="don't touch hub/sitemap")
    args = ap.parse_args()

    targets = []
    if args.all:
        # skip drafts/examples whose filename starts with "_"
        targets = sorted(p for p in CONTENT_DIR.glob("*.md") if not p.name.startswith("_"))
    elif args.markdown:
        targets = [Path(args.markdown)]
    else:
        ap.error("give a markdown file or --all")

    for t in targets:
        build_one(t, dry=args.dry_run, index=not args.no_index)
    print("done.")


# ---- the page template (kept in sync with the hand-built pages) ------------
TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Google tag (gtag.js) — GA4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-XV21PXX090"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XV21PXX090');
  </script>
  <meta name="description" content="{{DESCRIPTION}}">
  <meta name="keywords" content="{{KEYWORDS}}">
  <meta name="author" content="The Mound Fan Wiki Editors">

  <title>{{TITLE}}</title>

  <!-- Canonical -->
  <link rel="canonical" href="https://themound.online/pages/articles/{{SLUG}}.html">

  <!-- Favicons -->
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="apple-touch-icon" href="../../favicon.svg">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://themound.online/pages/articles/{{SLUG}}.html">
  <meta property="og:title" content="{{TITLE}}">
  <meta property="og:description" content="{{DESCRIPTION}}">
  <meta property="og:image" content="{{OG_IMAGE}}">

  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:title" content="{{TITLE}}">
  <meta property="twitter:description" content="{{DESCRIPTION}}">
  <meta property="twitter:image" content="{{OG_IMAGE}}">

  <link rel="stylesheet" href="../../css/style.css">
  <style>
    .article-body { max-width: 800px; margin: 0 auto; }
    .article-meta { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 2rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 1.5rem; }
    .article-body h2 { font-size: 1.6rem; margin-top: 2.75rem; margin-bottom: 1rem; }
    .article-body h3 { font-size: 1.2rem; margin-top: 1.75rem; margin-bottom: 0.6rem; color: var(--primary-glow); }
    .article-body p { color: var(--text-secondary); line-height: 1.85; margin-bottom: 1.25rem; font-size: 1.02rem; }
    .article-body ul, .article-body ol { color: var(--text-secondary); line-height: 1.85; margin: 0 0 1.5rem 1.3rem; }
    .article-body li { margin-bottom: 0.6rem; }
    .article-body a { color: var(--primary-glow); }
    .key-facts { background: rgba(0,255,204,0.05); border: 1px solid rgba(0,255,204,0.2); border-radius: 10px; padding: 1.5rem 1.75rem; margin: 0 0 2.5rem; }
    .key-facts h2 { margin-top: 0; font-size: 1.15rem; letter-spacing: 0.05em; text-transform: uppercase; color: var(--primary-glow); }
    .key-facts table { width: 100%; border-collapse: collapse; }
    .key-facts td { padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.06); vertical-align: top; color: var(--text-secondary); }
    .key-facts td:first-child { font-weight: 600; color: var(--text-primary); width: 38%; }
    .specs-table, .cmp-table { width: 100%; border-collapse: collapse; margin: 1rem 0 2rem; font-size: 0.95rem; }
    .specs-table th, .specs-table td, .cmp-table th, .cmp-table td { text-align: left; padding: 0.7rem 0.9rem; border: 1px solid rgba(255,255,255,0.08); color: var(--text-secondary); vertical-align: top; }
    .specs-table th, .cmp-table th { background: rgba(177,0,255,0.08); color: var(--text-primary); }
    .specs-table td:first-child, .cmp-table td:first-child { font-weight: 600; color: var(--text-primary); }
    .breadcrumbs { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; }
    .breadcrumbs a { color: var(--text-secondary); }
    .note { font-size: 0.9rem; color: var(--text-muted); font-style: italic; border-left: 3px solid var(--secondary-glow, #7a00ff); padding-left: 1rem; margin: 2rem 0; }
    .badge { display:inline-block; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; background:rgba(177,0,255,0.2); color:#d9a6ff; padding:0.2rem 0.6rem; border-radius:4px; vertical-align:middle; margin-left:0.5rem; }
    .creature, .realm { border-left: 3px solid var(--primary-glow); padding-left: 1.25rem; margin: 1.5rem 0; }
    .creature h3, .realm h3 { margin-top: 0; }
    .tag { display:inline-block; font-size:0.68rem; letter-spacing:0.06em; text-transform:uppercase; padding:0.15rem 0.55rem; border-radius:4px; vertical-align:middle; margin-left:0.5rem; }
    .tag-confirmed { background:rgba(0,255,204,0.18); color:#7dffe6; }
    .tag-expected { background:rgba(177,0,255,0.2); color:#d9a6ff; }
    .faq h3 { color: var(--text-primary); }
    @media (max-width: 600px) { .cmp-table { font-size: 0.8rem; } .cmp-table th, .cmp-table td { padding: 0.45rem 0.5rem; } }
  </style>

  <!-- Structured Data: Breadcrumb + Article (+ FAQ) -->
  <script type="application/ld+json">
{{JSONLD}}
  </script>
</head>
<body>

  <!-- HEADER / STICKY NAVIGATION -->
  <header class="header" id="main-header">
    <div class="container nav-container">
      <a href="../../index.html" class="logo" id="nav-logo">
        THE MOUND<span>: OMEN OF CTHULHU</span>
      </a>
      <nav aria-label="Main Navigation">
        <ul class="nav-menu" id="nav-menu-list">
          <li class="nav-item"><a href="../../index.html" class="nav-link" id="nav-home">Home</a></li>
          <li class="nav-item"><a href="index.html" class="nav-link active" id="nav-news">News</a></li>
          <li class="nav-item"><a href="../guides.html" class="nav-link" id="nav-guides">Guides</a></li>
          <li class="nav-item"><a href="../lore.html" class="nav-link" id="nav-lore">Lore</a></li>
          <li class="nav-item"><a href="../bestiary.html" class="nav-link" id="nav-bestiary">Bestiary</a></li>
          <li class="nav-item"><a href="../equipment.html" class="nav-link" id="nav-equipment">Equipment</a></li>
          <li class="nav-item"><a href="../calculator.html" class="nav-link" id="nav-calculator">Planner</a></li>
        </ul>
      </nav>
      <button class="hamburger" id="nav-hamburger-toggle" aria-label="Toggle mobile menu">
        <span class="bar"></span><span class="bar"></span><span class="bar"></span>
      </button>
    </div>
  </header>

  <!-- SUB HERO -->
  <section class="sub-hero" id="article-hero">
    <div class="sub-hero-bg" style="background-image: url('{{IMAGE_LOCAL}}');"></div>
    <div class="sub-hero-overlay"></div>
    <div class="container sub-hero-content">
      <h1 class="sub-hero-title" style="font-size: 2.4rem;">{{HERO_TITLE}}</h1>
    </div>
  </section>

  <!-- ARTICLE -->
  <section style="padding-top: 3rem;">
    <div class="container">
      <article class="article-body animate-fade-in">

        <div class="breadcrumbs">
          <a href="../../index.html">Home</a> › <a href="index.html">News &amp; Guides</a> › {{CRUMB}}
        </div>

        <div class="article-meta">
          📅 Published {{DATE}} · Last updated {{DATE_MOD}} · By The Mound Fan Wiki Editors · ~{{READ}} min read
        </div>

{{QUICK_FACTS}}
{{BODY}}

{{FAQ}}
      </article>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="footer" id="main-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col">
          <div class="footer-logo">THE MOUND<span>: OOM</span></div>
          <p class="footer-desc">
            The ultimate fan-built guide and database for The Mound: Omen of Cthulhu. Developed to assist all explorers of the cold cognitive deep.
          </p>
        </div>
        <div class="footer-col">
          <h4>Database</h4>
          <ul class="footer-links">
            <li><a href="../bestiary.html" class="footer-link">Creature Bestiary</a></li>
            <li><a href="../equipment.html" class="footer-link">Equipment Database</a></li>
            <li><a href="../calculator.html" class="footer-link">Expedition Planner</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Site & Legal</h4>
          <ul class="footer-links">
            <li><a href="../about.html" class="footer-link">About Us</a></li>
            <li><a href="../contact.html" class="footer-link">Contact</a></li>
            <li><a href="../privacy.html" class="footer-link">Privacy Policy</a></li>
            <li><a href="../privacy.html#terms" class="footer-link">Terms of Service</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Information</h4>
          <ul class="footer-links">
            <li><a href="../guides.html" class="footer-link">Survival Guides</a></li>
            <li><a href="../lore.html" class="footer-link">Mythos & Lore</a></li>
            <li><a href="https://store.steampowered.com/app/2569760/The_Mound_Omen_of_Cthulhu/" class="footer-link" target="_blank">Steam Store</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 The Mound: Omen of Cthulhu Fan Wiki. All rights reserved. Game content and materials are trademarks of ACE Team / Nacon.</p>
        <p>Designed by <a href="#" style="color: var(--primary-glow);">Antigravity</a></p>
      </div>
    </div>
  </footer>

  <button class="back-to-top" id="btn-back-to-top" aria-label="Back to top">▲</button>

  <script src="../../js/main.js"></script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
