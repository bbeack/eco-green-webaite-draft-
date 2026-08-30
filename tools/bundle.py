#!/usr/bin/env python3
"""Bundle the whole site into one self-contained HTML file.

The site itself is an ordinary multi-page static site; this produces a single
file for hosts that can only serve one page (a preview link, an email
attachment, a USB stick). Every asset - stylesheet, scripts, fonts and all
artwork - is inlined, and a small router swaps between the twelve pages.

    python3 tools/bundle.py            ->  dist/rootstock-preview.html
"""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

# index first so it is the landing route; the rest in reading order
ORDER = ["index.html", "about.html", "projects.html", "get-involved.html", "contact.html",
         "design-system.html", "privacy.html", "terms.html", "cookies.html",
         "accessibility.html", "thank-you.html", "404.html"]


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def data_uri(path, mime):
    with open(os.path.join(ROOT, path), "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode())


def inline_css():
    css = read("assets", "css", "style.css")
    css = css.replace('url("../fonts/plus-jakarta-sans-latin.woff2")',
                      'url("%s")' % data_uri("assets/fonts/plus-jakarta-sans-latin.woff2", "font/woff2"))
    css = css.replace('url("../fonts/plus-jakarta-sans-latin-ext.woff2")',
                      'url("%s")' % data_uri("assets/fonts/plus-jakarta-sans-latin-ext.woff2", "font/woff2"))
    css = css.replace('url("../img/pattern-leaves.svg")',
                      'url("%s")' % data_uri("assets/img/pattern-leaves.svg", "image/svg+xml"))
    return css


IMG_RE = re.compile(r'(["\'(])assets/img/([A-Za-z0-9._-]+\.svg)(["\')])')


def inline_images(html, cache={}):
    def sub(m):
        name = m.group(2)
        if name not in cache:
            cache[name] = data_uri("assets/img/" + name, "image/svg+xml")
        return m.group(1) + cache[name] + m.group(3)
    return IMG_RE.sub(sub, html)


def main():
    os.makedirs(DIST, exist_ok=True)
    index = read("index.html")

    # the chrome is identical on every page, so lift it from the first one
    chrome_open = re.search(r'<body class="page-index">(.*?)<main id="main">', index, re.S).group(1)
    chrome_close = re.search(r'</main>\s*(<footer.*?)<script src=', index, re.S).group(1)

    routes = []
    for page in ORDER:
        html = read(page)
        title = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
        desc = re.search(r'<meta name="description" content="(.*?)">', html, re.S).group(1).strip()
        body = re.search(r'<main id="main">(.*?)</main>', html, re.S).group(1)
        # form redirects become router hops rather than page loads
        body = body.replace(' data-redirect="thank-you.html"', ' data-bundle-redirect="thank-you.html"')
        routes.append((page, title, desc, body))

    parts = []
    parts.append("<title>Rootstock Farm &amp; Forest</title>\n")
    parts.append("<style>\n%s\n</style>\n" % inline_css())
    parts.append("""<script>
  /* Theme before first paint. A host that has already stamped a theme on the
     document wins - the viewer chose it, and this page should not argue. */
  (function () {
    try {
      var stamped = document.documentElement.getAttribute('data-theme');
      if (stamped) { localStorage.setItem('rootstock:theme', stamped); return; }
      var t = localStorage.getItem('rootstock:theme');
      if (!t) t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', t);
    } catch (e) {}
  })();
</script>
""")
    parts.append(inline_images(chrome_open))
    for i, (page, title, desc, body) in enumerate(routes):
        parts.append('\n<main id="main" class="route" data-route="%s" data-doc-title="%s"%s>\n%s\n</main>\n'
                     % (page, title.replace('"', "&quot;"), "" if i == 0 else " hidden", inline_images(body)))
    parts.append(inline_images(chrome_close))
    parts.append("<script>\n%s\n</script>\n" % read("assets", "js", "site.js"))
    parts.append("<script>\n%s\n</script>\n" % read("assets", "js", "forms.js"))
    parts.append(ROUTER)

    out = "".join(parts)
    path = os.path.join(DIST, "rootstock-preview.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    print("bundled %d pages -> dist/rootstock-preview.html (%.1f MB)" % (len(routes), len(out) / 1048576))


ROUTER = """<script>
/* Client-side router for the single-file build. The multi-page site needs
   none of this; it exists only so all twelve pages work from one URL. */
(function () {
  'use strict';
  var routes = {};
  Array.prototype.forEach.call(document.querySelectorAll('[data-route]'), function (m) {
    routes[m.dataset.route] = m;
  });
  var current = 'index.html';
  var veil = document.querySelector('[data-veil]');
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  function markNav(file) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-nav] a'), function (a) {
      var href = (a.getAttribute('href') || '').split('#')[0];
      if (href === file) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
  }

  function reveal(main) {
    // hidden routes never intersect, so nudge the observers once shown
    window.dispatchEvent(new Event('resize'));
    window.dispatchEvent(new Event('scroll'));
    if (reduced) {
      Array.prototype.forEach.call(main.querySelectorAll('[data-reveal], .stagger, .split-text'),
        function (e) { e.classList.add('is-visible'); });
    }
  }

  function go(file, hash) {
    var main = routes[file];
    if (!main) return false;
    if (main !== routes[current]) {
      routes[current].hidden = true;
      main.hidden = false;
      current = file;
      document.title = main.dataset.docTitle || document.title;
      markNav(file);
    }
    var target = hash && document.getElementById(hash);
    var y = target ? target.getBoundingClientRect().top + window.scrollY - 90 : 0;
    // 'auto' defers to CSS scroll-behavior, which is smooth here - a route
    // change must jump, not animate several thousand pixels
    try { window.scrollTo({ top: y, behavior: 'instant' }); }
    catch (err) { window.scrollTo(0, y); }
    reveal(main);
    return true;
  }

  function navigate(file, hash) {
    if (!routes[file]) return false;
    if (reduced || !veil) return go(file, hash);
    veil.classList.add('is-out');
    setTimeout(function () {
      go(file, hash);
      veil.classList.remove('is-out');
    }, 420);
    return true;
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    var href = a.getAttribute('href');
    if (!href || a.target === '_blank') return;
    if (href.charAt(0) === '#' || href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) return;
    var bits = href.split('#');
    if (!routes[bits[0]]) return;
    e.preventDefault();
    e.stopPropagation();            // beat the multi-page transition handler
    var drawer = document.querySelector('[data-drawer]');
    if (drawer && drawer.classList.contains('is-open')) {
      document.querySelector('[data-burger]').click();
    }
    navigate(bits[0], bits[1]);
  }, true);

  /* Forms that would navigate to the confirmation page hop routes instead. */
  document.addEventListener('rootstock:captured', function (e) {
    var form = e.target;
    var dest = form.getAttribute('data-bundle-redirect');
    if (!dest) return;
    var record = e.detail;
    var name = record.data.firstName || record.data.name || '';
    form.reset();
    Array.prototype.forEach.call(form.querySelectorAll('.has-error'),
      function (f) { f.classList.remove('has-error'); });
    setTimeout(function () {
      navigate(dest, null);
      window.Rootstock.Forms.renderThanks(
        new URLSearchParams('type=' + encodeURIComponent(record.type) +
                            (name ? '&name=' + encodeURIComponent(name) : '')));
    }, 20);
  });

  markNav('index.html');
})();
</script>
"""


if __name__ == "__main__":
    main()
