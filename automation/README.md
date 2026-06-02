# The Mound — content generator (Plan B)

Turns a Markdown file into a full, SEO-ready HTML article that matches the
hand-built pages, and (optionally) wires it into the News hub + sitemap.

This is the "publish" target for an automated content pipeline:

```
RSS/news  ->  LLM writes Markdown  ->  (optional) image API makes header  ->  build_site.py  ->  pages/articles/<slug>.html (+ hub card + sitemap)  ->  git push  ->  Cloudflare deploys
```

## Why this exists
Every article page repeats the same `<head>`, GA tag, 7-item nav, footer, and
JSON-LD scaffold. Hand-maintaining that across 11+ files is the reason small
changes (adding GA, editing the nav) needed bulk scripts. With this generator,
**authors write content only**; the boilerplate, JSON-LD (incl. FAQPage),
hub card, and sitemap entry are produced automatically and consistently.

## Install
```
pip install markdown        # recommended (tables, nicer lists). Works without it via a built-in fallback.
```

## Usage
```
python3 build_site.py content/my-article.md            # build + add hub card + sitemap entry
python3 build_site.py content/my-article.md --dry-run  # show what it would do, write nothing
python3 build_site.py content/my-article.md --no-index # write the HTML only, don't touch hub/sitemap
python3 build_site.py --all                            # build every content/*.md (skips files starting with "_")
```
Output: `../pages/articles/<slug>.html`. Re-running is safe — hub/sitemap inserts are idempotent (skipped if the slug already exists).

## Markdown frontmatter
```markdown
---
title: "Full article title (used in <title>, H1, OG, JSON-LD)"
slug: "url-filename"            # optional; default = markdown filename
description: "meta description / OG description"
keywords: "comma, separated"    # optional
image: "article_xxx.png"        # file in images/ ; used for hero bg + OG image
image_alt: "alt text"           # optional
hero_title: "Big H1 in hero"    # optional; default = title
crumb: "Short breadcrumb"       # optional; default = title
card_title: "Hub card title"    # optional; default = title
card_text: "Hub card blurb"     # optional; default = description
date: "2026-06-01"              # optional; default = today (UTC)
date_modified: "2026-06-01"     # optional; default = today (UTC)
read_time: 6                    # optional; default = computed from word count
quick_facts:                    # optional -> teal summary box (value may contain HTML)
  - "Release date | July 15, 2026"
  - "Platforms | PC, PS5, Xbox Series X|S"
faq:                            # optional -> visible FAQ + FAQPage rich-result JSON-LD
  - q: "Question text?"
    a: "Answer text (may contain <a> links)."
---

Body in **Markdown**. ## headings, paragraphs, - lists, [links](x.html),
tables, and raw HTML (e.g. <div class="note">…</div>, <span class="tag tag-expected">expected</span>) all work.
```

## Editorial rules (keep these — they protect SEO + AdSense)
- Write like a human editor. Avoid AI tells: "In this guide", "delve into",
  "unlock the secrets", "game-changing", "comprehensive guide".
- The game is pre-release: label anything unconfirmed as **Expected / estimate /
  not confirmed / community-reported**. Never present guesses as fact.
- Keep a human in the loop before publishing. Do **not** mass-publish thin
  auto-generated articles — Google penalizes "scaled content abuse" and it can
  cost AdSense eligibility.

## Available helper CSS classes (use raw HTML in the body)
`key-facts` (auto via quick_facts), `specs-table`, `cmp-table`, `note`,
`badge`, `creature`, `realm`, `tag tag-confirmed`, `tag tag-expected`, `faq` (auto via faq).
```
