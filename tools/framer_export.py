#!/usr/bin/env python3
"""Generate the Framer code-component design system from the real stylesheet.

Framer code components have no global stylesheet and share a document with
whatever else is on the Framer page, so the site's CSS cannot be dropped in
as-is. This rewrites it to be safe inside Framer:

  * every selector is scoped under `.rootstock`, so nothing leaks out
  * `:root` and `body` rules move onto that wrapper
  * `html` rules are dropped (a component must not restyle the document)
  * the dark theme becomes `.rootstock[data-theme="dark"]`, plus a
    prefers-color-scheme block so the wrapper's "Auto" setting works
  * keyframe names are prefixed, so `spin` or `fade-up` cannot collide with
    animations the Framer project defines itself
  * `@font-face` is rewritten to carry the woff2 inline, so the components
    make no third-party request - the same promise the site's cookie policy
    makes
  * `url(../img/...)` references are inlined as data URIs

Running this keeps the components in step with assets/css/style.css - the
stylesheet stays the single source of truth.

    python3 tools/framer_export.py
"""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "framer")
SCOPE = ".rootstock"
KEYFRAME_PREFIX = "rs-"

# assets small enough to ship inside the component
INLINE_ASSETS = {
    "logo": "logo.svg",
    "avatarA": "avatar-a.svg", "avatarB": "avatar-b.svg", "avatarC": "avatar-c.svg",
    "avatarD": "avatar-d.svg", "avatarE": "avatar-e.svg",
    "partner1": "partner-1.svg", "partner2": "partner-2.svg", "partner3": "partner-3.svg",
    "partner4": "partner-4.svg", "partner5": "partner-5.svg", "partner6": "partner-6.svg",
}


def font_uri(subset):
    path = os.path.join(ROOT, "assets", "fonts", "plus-jakarta-sans-%s.woff2" % subset)
    with open(path, "rb") as fh:
        return "data:font/woff2;base64," + base64.b64encode(fh.read()).decode()


def data_uri(name):
    with open(os.path.join(ROOT, "assets", "img", name), "rb") as fh:
        return "data:image/svg+xml;base64," + base64.b64encode(fh.read()).decode()


# --------------------------------------------------------------- CSS parsing --
def split_blocks(css):
    """Split a stylesheet body into (prelude, block_or_None) pairs, in order."""
    out, i, n, start = [], 0, len(css), 0
    while i < n:
        ch = css[i]
        if ch == "{":
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            out.append((css[start:i].strip(), css[i + 1:j - 1]))
            i = start = j
        elif ch == ";" and css[start:i].strip().startswith("@"):
            out.append((css[start:i].strip(), None))     # e.g. @import
            i += 1
            start = i
        else:
            i += 1
    tail = css[start:].strip()
    if tail:
        out.append((tail, None))
    return out


def scope_selector(sel):
    """Scope one selector under the wrapper. Returns None to drop the rule."""
    sel = " ".join(sel.split())
    if sel in ("html", "html, body", "body, html"):
        return None
    if sel == ":root":
        return SCOPE
    if sel.startswith(":root"):
        return SCOPE + sel[len(":root"):]
    if sel.startswith('[data-theme='):
        return SCOPE + sel
    if sel == "body":
        return SCOPE
    if sel.startswith("body."):
        return SCOPE + sel[len("body"):]
    if sel.startswith("body "):
        return SCOPE + sel[len("body"):]
    if sel.startswith("html "):
        return SCOPE + sel[len("html"):]
    if sel.startswith("*"):
        return SCOPE + " " + sel
    return SCOPE + " " + sel


def transform(css, keyframes):
    out = []
    for prelude, block in split_blocks(css):
        if block is None:
            if prelude and not prelude.startswith("@import"):
                out.append(prelude + ";")
            continue
        low = prelude.lower()
        if low.startswith("@font-face"):
            out.append("@font-face {%s}" % block)      # kept, with the file inlined below
            continue
        if low.startswith("@keyframes"):
            name = prelude.split(None, 1)[1].strip()
            keyframes.add(name)
            out.append("@keyframes %s%s {%s}" % (KEYFRAME_PREFIX, name, block))
            continue
        if low.startswith("@media") or low.startswith("@supports") or low.startswith("@layer"):
            inner = transform(block, keyframes)
            if inner.strip():
                out.append("%s {\n%s\n}" % (prelude, inner))
            continue
        if low.startswith("@"):
            out.append("%s {%s}" % (prelude, block))
            continue
        sels = [scope_selector(s) for s in prelude.split(",") if s.strip()]
        sels = [s for s in sels if s]
        if not sels:
            continue
        out.append("%s {%s}" % (", ".join(sels), block))
    return "\n".join(out)


def rename_keyframe_uses(css, names):
    for name in sorted(names, key=len, reverse=True):
        # `animation: <name> ...` and `animation-name: <name>`
        css = re.sub(r"(animation(?:-name)?\s*:[^;}]*?)\b%s\b" % re.escape(name),
                     lambda m: m.group(1) + KEYFRAME_PREFIX + name, css)
    return css


def add_auto_dark(css):
    """Mirror the dark tokens into a prefers-color-scheme block for 'Auto'."""
    m = re.search(r"\.rootstock\[data-theme=\"dark\"\] \{(.*?)\n\}", css, re.S)
    if not m:
        raise SystemExit("dark token block not found - has the stylesheet changed?")
    body = m.group(1)
    auto = ('\n\n/* "Auto" wrapper: follow the viewer\'s OS setting unless the\n'
            '   component has been pinned to a theme. */\n'
            '@media (prefers-color-scheme: dark) {\n'
            '  %s[data-theme="auto"] {%s\n  }\n}\n' % (SCOPE, body))
    return css + auto


def strip_comments(css):
    """Remove comments before parsing - otherwise a comment sitting above a
    rule is read as part of that rule's selector."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def build_css():
    css = open(os.path.join(ROOT, "assets", "css", "style.css"), encoding="utf-8").read()
    css = strip_comments(css)
    keyframes = set()
    css = transform(css, keyframes)
    css = rename_keyframe_uses(css, keyframes)
    css = add_auto_dark(css)
    css = css.replace('url("../img/pattern-leaves.svg")', 'url("%s")' % data_uri("pattern-leaves.svg"))
    for subset in ("latin", "latin-ext"):
        css = css.replace('url("../fonts/plus-jakarta-sans-%s.woff2")' % subset,
                          'url("%s")' % font_uri(subset))
    # the wrapper needs the reset applied to itself, not only its descendants
    css = css.replace(".rootstock *, .rootstock *::before, .rootstock *::after { box-sizing: border-box; }",
                      ".rootstock, .rootstock *, .rootstock *::before, .rootstock *::after { box-sizing: border-box; }")
    # `display: flow-root` stops panel margins collapsing out of the wrapper -
    # without it the host page shows through the gaps between panels.
    css += ("\n\n.rootstock { display: flow-root; }\n"
            '.rootstock[data-brand-font="off"] { --font-sans: inherit; --font-display: inherit; }\n')
    return css


HEADER = '''// AUTO-GENERATED by tools/framer_export.py - do not edit by hand.
// Regenerate after changing assets/css/style.css:  python3 tools/framer_export.py
//
// Shared foundation for the Rootstock Framer components. Every component calls
// useRootstock(), which injects this stylesheet into the document once.
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    css = build_css()
    assets = {k: data_uri(v) for k, v in INLINE_ASSETS.items()}

    parts = [HEADER, 'import { useEffect } from "react"\n\n']
    parts.append("export const designSystemCss = String.raw`\n%s\n`\n\n" % css.replace("`", "\\`").replace("${", "$\\{"))
    parts.append("export const assets = {\n")
    for key, uri in assets.items():
        parts.append('    %s:\n        "%s",\n' % (key, uri))
    parts.append("}\n\n")
    parts.append('''export type Theme = "auto" | "light" | "dark"

/**
 * Injects the design system once per document and returns the wrapper props
 * every Rootstock component spreads onto its outermost element.
 */
export function useRootstock(theme: Theme = "auto", brandFont: boolean = true) {
    useEffect(() => {
        if (typeof document === "undefined") return
        if (document.getElementById("rootstock-design-system")) return
        const style = document.createElement("style")
        style.id = "rootstock-design-system"
        style.textContent = designSystemCss
        document.head.appendChild(style)
    }, [])

    return {
        className: "rootstock",
        "data-theme": theme,
        "data-brand-font": brandFont ? "on" : "off",
    }
}
''')
    path = os.path.join(OUT, "RootstockDesignSystem.tsx")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("".join(parts))
    print("wrote framer/RootstockDesignSystem.tsx (%.1f KB, %d inlined assets)"
          % (os.path.getsize(path) / 1024, len(assets)))

    # a copy of the scoped CSS on its own, for verifying the transform
    debug = os.path.join(ROOT, "dist", "framer-scoped.css")
    os.makedirs(os.path.dirname(debug), exist_ok=True)
    with open(debug, "w", encoding="utf-8") as fh:
        fh.write(css)


if __name__ == "__main__":
    main()
