#!/usr/bin/env python3
"""Static builder for the Rootstock site.

Pages are authored as content fragments in `src/*.html` with a short front
matter block. This script wraps each one in the shared shell (head, header,
footer, scripts), expands {{icon:name}} shortcodes, and writes the finished
page to the repository root so the site can be served from any static host.

    python3 tools/build.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

SITE = {
    "name": "Rootstock",
    "tagline": "Farm-funded forests",
    "email": "hello@rootstock.earth",
    "phone": "+44 (0)1497 555 118",
    "address": "Cwm Aeron Farm, Hay-on-Wye, Powys HR3 5QA",
}

# --- Icon set (24×24, 1.75 stroke, round caps) --------------------------------
ICONS = {
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-left": '<path d="M19 12H5M11 18l-6-6 6-6"/>',
    "arrow-up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "arrow-down-right": '<path d="M7 7h10v10M7 17 17 7"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "sprout": '<path d="M7 20h10M12 20v-8"/><path d="M12 12c0-3.5-2.5-6-6-6 0 3.5 2.5 6 6 6Z"/><path d="M12 12c0-3 2-5.5 5-5.5 0 3-2 5.5-5 5.5Z"/>',
    "tree": '<path d="M12 2 6.5 10h3L5 16h6v6h2v-6h6l-4.5-6h3Z"/>',
    "drop": '<path d="M12 2.7 6.7 8a7.5 7.5 0 1 0 10.6 0Z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "heart": '<path d="M20.8 5.6a5.5 5.5 0 0 0-7.8 0L12 6.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 22l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18Z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>',
    "star": '<path d="m12 3 2.7 5.6 6.3.9-4.5 4.3 1 6.2-5.5-3-5.5 3 1-6.2L3 9.5l6.3-.9Z"/>',
    "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 7 9 6 9-6"/>',
    "phone": '<path d="M21 16.9v2.6a2 2 0 0 1-2.2 2 19.6 19.6 0 0 1-8.5-3 19.3 19.3 0 0 1-6-6 19.6 19.6 0 0 1-3-8.6A2 2 0 0 1 3.3 2H6a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L7.1 9.9a16 16 0 0 0 6 6l1.2-1.1a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7A2 2 0 0 1 21 16.9Z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "play": '<path d="M8 5.5v13l11-6.5Z"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "hand-coins": '<path d="M11 15h2a2 2 0 0 0 0-4H9.5L7 13"/><path d="m2 16 4-4 6 6 4-2 6 4"/><circle cx="16" cy="6" r="3"/>',
    "recycle": '<path d="M7 19H5a2 2 0 0 1-1.7-3l2-3.3M17 19h2a2 2 0 0 0 1.7-3l-2.2-3.7M9.3 5.5 10.5 3.4a2 2 0 0 1 3.4 0l1.3 2.2"/><path d="m6 16 1.6 3H11M18 16l-1.6 3H13M12 3v5M8 8l4-4 4 4"/>',
    "book": '<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v18H6.5A2.5 2.5 0 0 0 4 22.5Z"/><path d="M4 19.5h16"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
    "external": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><path d="M15 3h6v6M10 14 21 3"/>',
    "sun": '<circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8 6 18M18 6l1.8-1.8"/>',
    "moon": '<path d="M21 13.2A9 9 0 1 1 10.8 3a7 7 0 0 0 10.2 10.2Z"/>',
    "quote": '<path d="M10 11H6a3 3 0 0 1 3-3V6a5 5 0 0 0-5 5v7h6Zm10 0h-4a3 3 0 0 1 3-3V6a5 5 0 0 0-5 5v7h6Z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "layers": '<path d="m12 2 9 5-9 5-9-5Z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "type": '<path d="M4 7V4h16v3M9 20h6M12 4v16"/>',
    "sparkle": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6.3 6.3 9 9M15 15l2.7 2.7M17.7 6.3 15 9M9 15l-2.7 2.7"/>',
    "map": '<path d="m9 4-6 2.5v15L9 19l6 2.5 6-2.5v-15L15 6.5Z"/><path d="M9 4v15M15 6.5v15"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1M9 11h6M9 15h4"/>',
    "lock": '<rect x="4" y="10" width="16" height="11" rx="2.5"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "cookie": '<path d="M12 3a9 9 0 1 0 9 9 4 4 0 0 1-5-5 4 4 0 0 1-4-4Z"/><path d="M9 9h.01M14 13h.01M9.5 15h.01"/>',
    "scale": '<path d="M12 3v18M7 21h10M3 8l4-4 4 4M3 8a4 4 0 0 0 8 0M13 12l4-4 4 4M13 12a4 4 0 0 0 8 0M7 4h10"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "wind": '<path d="M3 8h10a3 3 0 1 0-3-3M3 16h13a3 3 0 1 1-3 3M3 12h16"/>',
    "twitter": '<path d="M22 5.9a8 8 0 0 1-2.4.7 4 4 0 0 0 1.8-2.2 8.2 8.2 0 0 1-2.6 1A4.1 4.1 0 0 0 11.8 9 11.6 11.6 0 0 1 3.4 4.7a4.1 4.1 0 0 0 1.3 5.5 4 4 0 0 1-1.9-.5 4.1 4.1 0 0 0 3.3 4 4.1 4.1 0 0 1-1.9.1 4.1 4.1 0 0 0 3.8 2.9A8.3 8.3 0 0 1 2 18.4a11.6 11.6 0 0 0 6.3 1.8c7.5 0 11.7-6.3 11.5-12a8.2 8.2 0 0 0 2.2-2.3Z"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/>',
    "facebook": '<path d="M14 8.5V7c0-1 .4-1.5 1.6-1.5H17V2.5h-2.4C11.8 2.5 11 4 11 6.4v2.1H9V12h2v9.5h3V12h2.3l.4-3.5Z"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 10.5V17M8 7.5v.01M12 17v-3.8c0-1.2.8-2.2 2-2.2s2 1 2 2.2V17"/>',
    "youtube": '<rect x="2.5" y="5" width="19" height="14" rx="4"/><path d="m10.5 9 5 3-5 3Z"/>',
}


def icon(name, size=20, cls=""):
    path = ICONS.get(name)
    if path is None:
        raise SystemExit("Unknown icon: %s" % name)
    return ('<svg class="ico %s" width="%d" height="%d" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true">%s</svg>' % (cls, size, size, path))


NAV = [
    ("index.html", "Home"),
    ("about.html", "Our Farm"),
    ("projects.html", "Projects"),
    ("get-involved.html", "Get Involved"),
    ("contact.html", "Contact"),
]


def header_html():
    nav = "".join('<a href="%s">%s</a>' % (h, l) for h, l in NAV)
    drawer = "".join('<a href="%s">%s<span>%02d</span></a>' % (h, l, i + 1)
                     for i, (h, l) in enumerate(NAV))
    drawer += ('<a href="design-system.html">Design System<span>06</span></a>'
               '<a href="contact.html#visit">Visit the farm<span>07</span></a>')
    return f"""
  <div class="progress-bar" data-progress aria-hidden="true"></div>
  <div class="veil" data-veil aria-hidden="true"></div>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="header" data-header>
    <div class="wrap header-inner">
      <a class="brand" href="index.html" aria-label="Rootstock — home">
        <img src="assets/img/logo.svg" alt="" width="34" height="34">
        <span class="brand-name">Rootstock<small>Farm &amp; Forest</small></span>
      </a>
      <nav class="nav" data-nav aria-label="Primary">{nav}</nav>
      <div class="header-actions">
        <button class="theme-toggle" data-theme-toggle type="button" aria-label="Switch theme">
          {icon('sun', 18, 'ico-sun')}{icon('moon', 18, 'ico-moon')}
        </button>
        <a class="btn btn-accent btn-sm hide-md" href="get-involved.html#donate" data-magnetic>
          Plant a tree {icon('arrow-right', 15, 'btn-ico')}
        </a>
        <button class="burger" data-burger type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </header>

  <div class="drawer" id="drawer" data-drawer aria-hidden="true" aria-label="Mobile menu">
    <nav data-nav aria-label="Mobile">{drawer}</nav>
    <div class="drawer-foot">
      <a class="btn btn-accent btn-block" href="get-involved.html#donate">Plant a tree {icon('arrow-right', 16, 'btn-ico')}</a>
      <div class="cluster small muted">
        <a href="mailto:{SITE['email']}" class="cluster gap-sm">{icon('mail', 16)} {SITE['email']}</a>
      </div>
      <div class="social">
        <a href="https://x.com/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on X (opens in a new tab)">{icon('twitter', 17)}</a>
        <a href="https://instagram.com/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on Instagram (opens in a new tab)">{icon('instagram', 17)}</a>
        <a href="https://facebook.com/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on Facebook (opens in a new tab)">{icon('facebook', 17)}</a>
        <a href="https://linkedin.com/company/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on LinkedIn (opens in a new tab)">{icon('linkedin', 17)}</a>
      </div>
    </div>
  </div>
"""


def footer_html():
    """Light footer on the page paper, matching the reference layout."""
    return f"""
  <footer class="footer">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html">
          <img src="assets/img/logo.svg" alt="" width="32" height="32">
          <span class="brand-name">Rootstock<small>Farm &amp; Forest</small></span>
        </a>
        <p class="small mt-4" style="max-width:28ch">Together, we can grow a valley that
          feeds people and forests for generations to come.</p>
        <form class="mt-5" data-capture="newsletter" data-success="Subscribed - thank you.">
          <input class="hp" type="text" name="_hp" tabindex="-1" autocomplete="off" aria-hidden="true" aria-label="Leave this field empty">
          <div class="inline-form">
            <label class="sr-only" for="footer-email">Email address</label>
            <input class="input" id="footer-email" name="email" type="email" required placeholder="Enter your email">
            <button class="btn btn-primary btn-sm" type="submit" aria-label="Subscribe">{icon('arrow-right', 15)}</button>
          </div>
          <div class="field mt-3"><p class="field-error"></p></div>
          <p class="form-status" data-form-status role="status"></p>
        </form>
      </div>
      <div>
        <h4>Explore</h4>
        <div class="footer-links">
          <a href="index.html">Home</a>
          <a href="about.html">Our Farm</a>
          <a href="projects.html">Forest Projects</a>
          <a href="get-involved.html">Get Involved</a>
          <a href="contact.html">Contact</a>
        </div>
      </div>
      <div>
        <h4>Get Involved</h4>
        <div class="footer-links">
          <a href="get-involved.html#donate">Plant a tree</a>
          <a href="get-involved.html#monthly">Become a Grove Keeper</a>
          <a href="get-involved.html#volunteer">Volunteer days</a>
          <a href="get-involved.html#partners">Partner with us</a>
          <a href="get-involved.html#gift">Gift a woodland</a>
        </div>
      </div>
      <div>
        <h4>Support</h4>
        <div class="footer-links">
          <a href="get-involved.html#faq">FAQs</a>
          <a href="projects.html#impact">Impact reporting</a>
          <a href="about.html#accounts">Where the money goes</a>
          <a href="privacy.html">Privacy policy</a>
          <a href="terms.html">Terms of use</a>
          <a href="cookies.html">Cookie policy</a>
          <a href="accessibility.html">Accessibility</a>
          <a href="design-system.html">Design system</a>
        </div>
      </div>
      <div>
        <h4>Follow Us</h4>
        <div class="social">
          <a href="https://x.com/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on X (opens in a new tab)">{icon('twitter', 16)}</a>
          <a href="https://instagram.com/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on Instagram (opens in a new tab)">{icon('instagram', 16)}</a>
          <a href="https://facebook.com/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on Facebook (opens in a new tab)">{icon('facebook', 16)}</a>
          <a href="https://linkedin.com/company/rootstockearth" target="_blank" rel="noopener" aria-label="Rootstock on LinkedIn (opens in a new tab)">{icon('linkedin', 16)}</a>
        </div>
        <h4 class="mt-6">Visit</h4>
        <p class="small">{SITE['address']}<br>Farm shop open Fri&ndash;Sun, 9&ndash;4</p>
        <p class="small mt-3"><a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> Rootstock Farm &amp; Forest CIC. Company no. 11902847. A not-for-profit community interest company.</p>
      <p class="cluster gap-sm">{icon('leaf', 14)} 100% of trading profit funds planting</p>
    </div>
  </footer>

  <button class="to-top" data-to-top type="button" aria-label="Back to top">{icon('arrow-up', 17)}</button>
"""


SHELL = """<!DOCTYPE html>
<html lang="en-GB" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#14301F">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="assets/img/hero-split.svg">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
<noscript><style>[data-reveal],.stagger>*,.split-text .word{{opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}}.meter-fill{{width:60%}}</style></noscript>
<script>
  /* Set the theme before first paint so there is no flash of the wrong palette. */
  (function () {{
    try {{
      var t = localStorage.getItem('rootstock:theme');
      if (!t) t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', t);
    }} catch (e) {{}}
  }})();
</script>
</head>
<body class="page-{slug}">
{header}
  <main id="main">
{body}
  </main>
{footer}
<script src="assets/js/site.js" defer></script>
<script src="assets/js/forms.js" defer></script>
</body>
</html>
"""


FM_RE = re.compile(r"^<!--\s*(.*?)\s*-->", re.S)
ICON_RE = re.compile(r"\{\{icon:([a-z0-9-]+)(?::(\d+))?(?::([a-z0-9 _-]+))?\}\}")


def expand(html):
    return ICON_RE.sub(lambda m: icon(m.group(1), int(m.group(2) or 20), m.group(3) or ""), html)


def build():
    if not os.path.isdir(SRC):
        raise SystemExit("no src/ directory")
    header = expand(header_html())
    footer = expand(footer_html())
    pages = sorted(f for f in os.listdir(SRC) if f.endswith(".html"))
    for f in pages:
        raw = open(os.path.join(SRC, f)).read()
        m = FM_RE.match(raw)
        meta = {}
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            raw = raw[m.end():]
        slug = os.path.splitext(f)[0]
        out = SHELL.format(
            title=meta.get("title", "Rootstock"),
            desc=meta.get("desc", "Rootstock — farm-funded forests."),
            slug=slug,
            header=header,
            footer=footer,
            body=expand(raw).rstrip(),
        )
        with open(os.path.join(ROOT, f), "w") as fh:
            fh.write(out)
        print("  built %-24s %6.1f kb" % (f, len(out) / 1024))
    write_sitemap(pages)
    print("%d pages built." % len(pages))


BASE_URL = "https://rootstock.earth/"   # change to your domain before going live
NO_INDEX = {"404.html", "thank-you.html"}


def write_sitemap(pages):
    """Emit sitemap.xml and robots.txt alongside the built pages."""
    import datetime
    today = datetime.date.today().isoformat()
    priority = {"index.html": "1.0", "get-involved.html": "0.9", "projects.html": "0.9",
                "about.html": "0.8", "contact.html": "0.8"}
    urls = []
    for f in pages:
        if f in NO_INDEX:
            continue
        loc = BASE_URL + ("" if f == "index.html" else f)
        urls.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                    "    <priority>%s</priority>\n  </url>" % (loc, today, priority.get(f, "0.5")))
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w") as fh:
        fh.write("User-agent: *\nAllow: /\nDisallow: /thank-you.html\n\nSitemap: %ssitemap.xml\n" % BASE_URL)
    print("  built sitemap.xml + robots.txt")


if __name__ == "__main__":
    build()
