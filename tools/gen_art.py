#!/usr/bin/env python3
"""Procedural SVG scene generator for the Rootstock site.

Every illustration on the site is generated here so the project ships with
self-contained artwork (no external image hosts, no broken images offline).
Run: python3 tools/gen_art.py
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "img")
os.makedirs(OUT, exist_ok=True)


# ---------------------------------------------------------------- helpers ---
def hexf(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ca, cb = hexf(a), hexf(b)
    return "#%02x%02x%02x" % tuple(round(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))


def shade(c, t):
    return mix(c, "#06120c", t)


def tint(c, t):
    return mix(c, "#ffffff", t)


def ridge(y, amp, seg, w, seed, rough=0.5):
    """A smooth-ish ridge line as a list of points across width w."""
    rnd = random.Random(seed)
    pts = []
    prev = y
    for i in range(seg + 1):
        x = w * i / seg
        target = y + rnd.uniform(-amp, amp)
        prev = prev + (target - prev) * rough
        pts.append((x, prev))
    return pts


def smooth_path(pts, h, w, close_bottom=True):
    """Catmull-Rom-ish smoothing into a cubic path, closed to the bottom."""
    d = "M %.1f %.1f" % pts[0]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cx = (x0 + x1) / 2
        d += " C %.1f %.1f %.1f %.1f %.1f %.1f" % (cx, y0, cx, y1, x1, y1)
    if close_bottom:
        d += " L %.1f %.1f L 0 %.1f Z" % (w, h, h)
    return d


def conifer(x, base, height, width, color, rnd, layers=None):
    """A stylised conifer built from stacked triangles."""
    layers = layers or rnd.randint(3, 5)
    g = ['<g>']
    trunk_w = max(1.4, width * 0.11)
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="%.1f"/>'
             % (x - trunk_w / 2, base - height * 0.18, trunk_w, height * 0.2, shade(color, 0.55), trunk_w / 2))
    for i in range(layers):
        t = i / max(1, layers - 1)
        ly = base - height * 0.12 - (height * 0.82) * t
        lw = width * (1.0 - t * 0.62)
        lh = height * 0.34
        c = mix(color, tint(color, 0.22), t)
        g.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
                 % (x, ly - lh, x + lw / 2, ly, x - lw / 2, ly, c))
    g.append('</g>')
    return "".join(g)


def broadleaf(x, base, height, width, color, rnd):
    """A stylised round-crowned tree from overlapping blobs."""
    g = ['<g>']
    trunk_w = max(1.6, width * 0.1)
    g.append('<path d="M %.1f %.1f q %.1f %.1f %.1f %.1f l %.1f 0 q %.1f %.1f %.1f %.1f Z" fill="%s"/>'
             % (x - trunk_w, base, 0, -height * 0.3, trunk_w * 0.35, -height * 0.45,
                trunk_w * 1.3, 0, height * 0.15, trunk_w * 0.35, height * 0.45, shade(color, 0.6)))
    cy = base - height * 0.62
    for i in range(rnd.randint(4, 6)):
        rx = width * rnd.uniform(0.22, 0.4)
        ox = rnd.uniform(-width * 0.24, width * 0.24)
        oy = rnd.uniform(-height * 0.16, height * 0.12)
        c = mix(color, tint(color, 0.3), rnd.random() * 0.8)
        g.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
                 % (x + ox, cy + oy, rx, rx * rnd.uniform(0.78, 1.0), c))
    g.append('</g>')
    return "".join(g)


def svg_open(w, h, extra=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'preserveAspectRatio="xMidYMid slice" role="img" %s>' % (w, h, w, h, extra))


def write(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w") as f:
        f.write(body)
    print("  wrote", name, "(%.1f kb)" % (len(body) / 1024))


def sky(w, h, top, bottom, sun=None, sun_color="#FFF3C4"):
    s = ['<rect width="%d" height="%d" fill="url(#sky)"/>' % (w, h)]
    if sun:
        sx, sy, sr = sun
        s.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#glow)"/>' % (sx, sy, sr * 4.2))
        s.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (sx, sy, sr, sun_color))
    return "".join(s)


def defs_sky(top, bottom, glow="#FFE9A8"):
    return ('<defs>'
            '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
            '<radialGradient id="glow"><stop offset="0" stop-color="%s" stop-opacity=".85"/>'
            '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
            '</defs>' % (top, bottom, glow, glow))


def mist(w, y, h, color="#ffffff", op=0.5, seed=1, bands=3):
    rnd = random.Random(seed)
    out = []
    for i in range(bands):
        yy = y + i * (h / bands)
        pts = ridge(yy, h * 0.18, 8, w, seed * 13 + i)
        d = smooth_path(pts, yy + h / bands * 1.4, w)
        out.append('<path d="%s" fill="%s" opacity="%.2f"/>' % (d, color, op * (1 - i * 0.22)))
    return "".join(out)


def grain(w, h, seed=7, n=140, color="#ffffff", op=0.06):
    """Subtle speckle so flat fills read as textured."""
    rnd = random.Random(seed)
    out = ['<g opacity="%.2f" fill="%s">' % (op, color)]
    for _ in range(n):
        out.append('<circle cx="%.0f" cy="%.0f" r="%.1f"/>'
                   % (rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.6, 2.2)))
    out.append('</g>')
    return "".join(out)


# ---------------------------------------------------------------- scenes ----
def scene_hero_split(w=1400, h=1100):
    """The signature image: restored forest bleeding into degraded land."""
    s = [svg_open(w, h)]
    s.append('<defs>'
             '<linearGradient id="dry" x1="0" y1="0" x2=".3" y2="1">'
             '<stop offset="0" stop-color="#D8B489"/><stop offset=".5" stop-color="#BE9264"/>'
             '<stop offset="1" stop-color="#9A7145"/></linearGradient>'
             '<linearGradient id="forestbase" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#17351A"/><stop offset=".55" stop-color="#1D4322"/>'
             '<stop offset=".78" stop-color="#1D4322" stop-opacity=".7"/>'
             '<stop offset="1" stop-color="#1D4322" stop-opacity="0"/></linearGradient>'
             '<linearGradient id="seam" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="#EFF3E6" stop-opacity="0"/>'
             '<stop offset=".38" stop-color="#EFF3E6" stop-opacity=".42"/>'
             '<stop offset=".58" stop-color="#F2EFE2" stop-opacity=".30"/>'
             '<stop offset="1" stop-color="#F2EFE2" stop-opacity="0"/></linearGradient>'
             '<radialGradient id="glow"><stop offset="0" stop-color="#FFF0BE" stop-opacity=".75"/>'
             '<stop offset="1" stop-color="#FFF0BE" stop-opacity="0"/></radialGradient>'
             '</defs>')

    # --- base: cracked, arid ground across the whole frame -----------------
    s.append('<rect width="%d" height="%d" fill="url(#dry)"/>' % (w, h))
    dry_rnd = random.Random(3)
    for _ in range(120):
        x = dry_rnd.uniform(w * 0.45, w + 40)
        y = dry_rnd.uniform(-20, h + 20)
        pts = [(x, y)]
        for _ in range(dry_rnd.randint(2, 5)):
            x += dry_rnd.uniform(-80, 80)
            y += dry_rnd.uniform(-70, 70)
            pts.append((x, y))
        d = "M " + " L ".join("%.0f %.0f" % p for p in pts)
        s.append('<path d="%s" stroke="%s" stroke-width="%.1f" fill="none" opacity=".5" '
                 'stroke-linecap="round"/>'
                 % (d, dry_rnd.choice(["#7B5733", "#6A4A2C", "#C6A075"]), dry_rnd.uniform(0.8, 2.8)))
    for _ in range(160):
        x = dry_rnd.uniform(w * 0.55, w)
        y = dry_rnd.uniform(0, h)
        s.append('<path d="M %.0f %.0f q %.0f -14 %.0f -28" stroke="#8A6437" stroke-width="1.3" '
                 'fill="none" opacity=".4"/>'
                 % (x, y, dry_rnd.uniform(-8, 8), dry_rnd.uniform(-11, 11)))
    for _ in range(50):  # bleached scrub
        x, y = dry_rnd.uniform(w * 0.62, w), dry_rnd.uniform(0, h)
        sc = dry_rnd.uniform(6, 16)
        for k in range(5):
            a = -math.pi / 2 + dry_rnd.uniform(-1.1, 1.1)
            s.append('<path d="M %.0f %.0f l %.1f %.1f" stroke="#A98455" stroke-width="1.1" '
                     'opacity=".55"/>' % (x, y, math.cos(a) * sc, math.sin(a) * sc))
    for _ in range(70):  # patchy bare-soil tones
        s.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="%s" opacity=".09"/>'
                 % (dry_rnd.uniform(w * 0.35, w), dry_rnd.uniform(0, h), dry_rnd.uniform(30, 110),
                    dry_rnd.uniform(20, 70), dry_rnd.choice(["#8E653B", "#E0C098", "#7A5530"])))
    s.append('<circle cx="%d" cy="%d" r="480" fill="url(#glow)"/>' % (int(w * 0.78), int(h * 0.14)))

    # --- left: dense restored canopy ---------------------------------------
    # The canopy is deliberately centred around 20-50% of the frame: the hero
    # panel fades its left edge into white, so a canopy hard against x=0 would
    # be washed out before it was ever seen.
    canopy = random.Random(5)
    greens = ["#3F7A34", "#4E8F41", "#2E6B2A", "#63A64F", "#245A22", "#7BBE63", "#9ECF86"]
    s.append('<rect x="0" y="0" width="%d" height="%d" fill="url(#forestbase)"/>' % (int(w * 0.78), h))

    def density(x):
        """1.0 across the core, tapering to 0 by 72% of the frame."""
        if x < w * 0.44:
            return 1.0
        return max(0.0, 1.0 - (x - w * 0.44) / (w * 0.28))

    for _ in range(2500):
        x = canopy.uniform(-20, w * 0.76)
        d = density(x)
        if canopy.random() > d * d:
            continue
        y = canopy.uniform(-20, h + 20)
        r = canopy.uniform(4.5, 17) * (0.55 + d * 0.45)
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" opacity="%.1f"/>'
                 % (x, y, r, canopy.choice(greens), 0.6 + canopy.random() * 0.4))
    for _ in range(520):   # sunlit crown tops
        x = canopy.uniform(-10, w * 0.62)
        if canopy.random() > density(x):
            continue
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#BBE2A6" opacity="%.1f"/>'
                 % (x, canopy.uniform(0, h), canopy.uniform(1.8, 6), canopy.uniform(0.15, 0.55)))
    for _ in range(450):   # shadow gaps between crowns
        x = canopy.uniform(-10, w * 0.58)
        if canopy.random() > density(x):
            continue
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#0F2A14" opacity="%.1f"/>'
                 % (x, canopy.uniform(0, h), canopy.uniform(1.8, 7), canopy.uniform(0.12, 0.45)))
    for _ in range(34):    # pioneers colonising the bare ground
        x = canopy.uniform(w * 0.6, w * 0.88)
        r = canopy.uniform(3, 11) * max(0.2, 1 - (x - w * 0.6) / (w * 0.3)) + 3
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" opacity="%.2f"/>'
                 % (x, canopy.uniform(0, h), r, canopy.choice(greens), canopy.uniform(0.4, 0.85)))

    s.append('<rect x="%d" y="0" width="%d" height="%d" fill="url(#seam)"/>'
             % (int(w * 0.42), int(w * 0.52), h))
    s.append(grain(w, h, seed=4, n=260, op=0.06))
    s.append('</svg>')
    return "".join(s)


def scene_landscape(name, w, h, palette, seed, kind="forest"):
    """Layered landscape: sky, ridges, trees, water, foreground."""
    rnd = random.Random(seed)
    s = [svg_open(w, h)]
    s.append(defs_sky(palette["sky_top"], palette["sky_bottom"], palette.get("glow", "#FFE9A8")))
    s.append(sky(w, h, palette["sky_top"], palette["sky_bottom"], palette.get("sun"),
                 palette.get("sun_color", "#FFF3C4")))
    if palette.get("clouds"):
        for i in range(5):
            cx, cy = rnd.uniform(0, w), rnd.uniform(h * 0.05, h * 0.3)
            for j in range(4):
                s.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="#ffffff" opacity=".28"/>'
                         % (cx + j * rnd.uniform(18, 46), cy + rnd.uniform(-8, 8),
                            rnd.uniform(38, 80), rnd.uniform(12, 24)))

    layers = palette["layers"]
    for i, (ly, col) in enumerate(layers):
        y = h * ly
        pts = ridge(y, h * (0.045 if i < 2 else 0.03), 9 + i * 2, w, seed * 31 + i, rough=0.65)
        s.append('<path d="%s" fill="%s"/>' % (smooth_path(pts, h, w), col))
        if kind in ("forest", "misty") and i >= 1:
            base_y = min(p[1] for p in pts) + h * 0.02
            n = 22 + i * 14
            for k in range(n):
                x = rnd.uniform(-20, w + 20)
                # sit the tree on the ridge
                idx = max(0, min(len(pts) - 1, int(x / w * (len(pts) - 1))))
                by = pts[idx][1] + h * 0.02
                th = h * rnd.uniform(0.05, 0.11) * (0.6 + i * 0.22)
                s.append(conifer(x, by, th, th * rnd.uniform(0.42, 0.6), tint(col, 0.06), rnd))
        if kind == "misty" and i < len(layers) - 1:
            s.append(mist(w, y - h * 0.02, h * 0.11, "#ffffff", 0.42, seed=seed + i * 7, bands=2))

    if palette.get("water"):
        wy = h * palette["water"]
        s.append('<rect x="0" y="%.0f" width="%d" height="%.0f" fill="%s"/>'
                 % (wy, w, h - wy, palette["water_color"]))
        for i in range(26):
            yy = wy + (h - wy) * (i / 26) ** 1.5 + 4
            ww = rnd.uniform(w * 0.06, w * 0.3)
            xx = rnd.uniform(0, w - ww)
            s.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.1f" rx="2" fill="#ffffff" opacity="%.2f"/>'
                     % (xx, yy, ww, rnd.uniform(1.5, 4), rnd.uniform(0.06, 0.26)))

    fg = palette.get("foreground")
    if fg:
        y = h * fg[0]
        pts = ridge(y, h * 0.02, 7, w, seed + 99, rough=0.7)
        s.append('<path d="%s" fill="%s"/>' % (smooth_path(pts, h, w), fg[1]))
        if kind in ("forest", "misty"):
            for k in range(9):
                x = rnd.uniform(-30, w + 30)
                th = h * rnd.uniform(0.16, 0.3)
                s.append(conifer(x, y + h * 0.06, th, th * 0.5, shade(fg[1], 0.25), rnd))
        if kind == "broadleaf":
            for k in range(7):
                x = rnd.uniform(-20, w + 20)
                th = h * rnd.uniform(0.14, 0.26)
                s.append(broadleaf(x, y + h * 0.07, th, th * 0.9, shade(fg[1], 0.2), rnd))
    s.append(grain(w, h, seed=seed + 3, n=120, op=0.05))
    s.append('</svg>')
    return "".join(s)


def scene_farm_rows(w=1200, h=900):
    """Contour-planted eco farm seen in perspective."""
    rnd = random.Random(21)
    s = [svg_open(w, h)]
    s.append(defs_sky("#CFE3EE", "#F3EBD6"))
    s.append(sky(w, h, "#CFE3EE", "#F3EBD6", (w * 0.78, h * 0.16, 52), "#FFF6D0"))
    # distant hills
    for ly, col in [(0.34, "#9FBFA4"), (0.40, "#7FAA8A")]:
        pts = ridge(h * ly, h * 0.03, 9, w, int(ly * 100), 0.6)
        s.append('<path d="%s" fill="%s"/>' % (smooth_path(pts, h, w), col))
    # hedgerow
    for k in range(40):
        x = rnd.uniform(-10, w + 10)
        s.append(broadleaf(x, h * 0.44, h * rnd.uniform(0.05, 0.085), h * 0.07, "#417F53", rnd))
    # field bands in perspective
    horizon = h * 0.44
    bands = 16
    for i in range(bands):
        t0 = (i / bands) ** 1.9
        t1 = ((i + 1) / bands) ** 1.9
        y0 = horizon + (h - horizon) * t0
        y1 = horizon + (h - horizon) * t1
        c = rnd.choice(["#6FA85E", "#83B96B", "#5C9450", "#A8C97C", "#C9CE86", "#4E8446"])
        bow = (h - horizon) * 0.04
        s.append('<path d="M 0 %.1f Q %.1f %.1f %d %.1f L %d %.1f Q %.1f %.1f 0 %.1f Z" fill="%s"/>'
                 % (y0, w / 2, y0 + bow, w, y0, w, y1, w / 2, y1 + bow, y1, c))
        # crop rows
        if i > 4:
            step = max(14, 90 - i * 5)
            for x in range(-40, w + 40, step):
                xx = x + (x - w / 2) * t0 * 0.35
                s.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" stroke="%s" stroke-width="%.1f" '
                         'fill="none" opacity=".45"/>'
                         % (xx, y0, xx + 6, (y0 + y1) / 2 + bow * 0.5, xx + 12, y1, shade(c, 0.28),
                            1 + i * 0.22))
    # windbreak trees in the foreground band
    for k in range(7):
        x = rnd.uniform(0, w)
        th = h * rnd.uniform(0.1, 0.2)
        s.append(broadleaf(x, h * rnd.uniform(0.72, 0.96), th, th * 0.95, "#35704A", rnd))
    s.append(grain(w, h, seed=8, n=110, op=0.05))
    s.append('</svg>')
    return "".join(s)


def scene_nursery(w=1200, h=900):
    """Seedling nursery trays — the fundraising unit made visible."""
    rnd = random.Random(33)
    s = [svg_open(w, h)]
    s.append(defs_sky("#E7EFDD", "#CFE0C4"))
    s.append('<rect width="%d" height="%d" fill="url(#sky)"/>' % (w, h))
    s.append('<circle cx="%d" cy="%d" r="360" fill="url(#glow)"/>' % (int(w * 0.3), int(h * 0.12)))
    s.append('<rect x="0" y="%.0f" width="%d" height="%.0f" fill="#6B5A44"/>' % (h * 0.3, w, h * 0.7))
    for i in range(300):
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" opacity=".5"/>'
                 % (rnd.uniform(0, w), rnd.uniform(h * 0.3, h), rnd.uniform(1, 4),
                    rnd.choice(["#5A4B39", "#7D6A50", "#4A3D2E"])))
    rows = 6
    for r in range(rows):
        t = r / (rows - 1)
        y = h * (0.34 + t * 0.62)
        scale = 0.35 + t * 1.0
        cell = 70 * scale
        for i in range(int(w / cell) + 2):
            x = i * cell + (r % 2) * cell * 0.4 - cell
            # pot
            s.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
                     % (x - cell * 0.26, y - cell * 0.38, x + cell * 0.26, y - cell * 0.38,
                        x + cell * 0.18, y, x - cell * 0.18, y, "#3B322A"))
            # seedling
            gh = cell * rnd.uniform(0.5, 0.85)
            s.append('<path d="M %.1f %.1f l 0 %.1f" stroke="#4E7D3C" stroke-width="%.1f" stroke-linecap="round"/>'
                     % (x, y - cell * 0.24, -gh, max(1.2, cell * 0.05)))
            for lf in range(rnd.randint(2, 4)):
                ly = y - cell * 0.24 - gh * rnd.uniform(0.35, 1.0)
                dirn = rnd.choice([-1, 1])
                lw = cell * rnd.uniform(0.24, 0.42)
                s.append('<path d="M %.1f %.1f q %.1f %.1f %.1f %.1f q %.1f %.1f %.1f %.1f Z" fill="%s"/>'
                         % (x, ly, lw * 0.5 * dirn, -cell * 0.16, lw * dirn, -cell * 0.03,
                            -lw * 0.45 * dirn, cell * 0.14, -lw * dirn, cell * 0.03,
                            rnd.choice(["#5E9B44", "#6FB050", "#4C8A3B", "#87C267"])))
    s.append(mist(w, h * 0.26, h * 0.12, "#ffffff", 0.25, seed=12, bands=2))
    s.append(grain(w, h, seed=13, n=100, op=0.05))
    s.append('</svg>')
    return "".join(s)


def scene_planting(w=1200, h=900):
    """Volunteers planting at golden hour — abstract silhouettes."""
    rnd = random.Random(44)
    s = [svg_open(w, h)]
    s.append('<defs>'
             '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#F3C98B"/><stop offset=".5" stop-color="#F0A96B"/>'
             '<stop offset="1" stop-color="#C97F58"/></linearGradient>'
             '<radialGradient id="glow"><stop offset="0" stop-color="#FFE7B0" stop-opacity=".95"/>'
             '<stop offset="1" stop-color="#FFE7B0" stop-opacity="0"/></radialGradient>'
             '</defs>')
    s.append('<rect width="%d" height="%d" fill="url(#sky)"/>' % (w, h))
    s.append('<circle cx="%.0f" cy="%.0f" r="420" fill="url(#glow)"/>' % (w * 0.62, h * 0.46))
    s.append('<circle cx="%.0f" cy="%.0f" r="74" fill="#FFF0C4"/>' % (w * 0.62, h * 0.46))
    for ly, col, op in [(0.5, "#B4784F", 1), (0.58, "#95603F", 1)]:
        pts = ridge(h * ly, h * 0.02, 8, w, int(ly * 77), 0.6)
        s.append('<path d="%s" fill="%s" opacity="%s"/>' % (smooth_path(pts, h, w), col, op))
    # tree line silhouettes
    for k in range(26):
        x = rnd.uniform(-20, w + 20)
        th = h * rnd.uniform(0.06, 0.13)
        s.append(conifer(x, h * 0.6, th, th * 0.5, "#6B4630", rnd))
    pts = ridge(h * 0.68, h * 0.015, 7, w, 5, 0.7)
    s.append('<path d="%s" fill="#4A3222"/>' % smooth_path(pts, h, w))

    def figure(x, base, sc, lean=1):
        g = ['<g fill="#2B1D14">']
        g.append('<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, base - 118 * sc, 15 * sc))
        g.append('<path d="M %.1f %.1f q %.1f %.1f %.1f %.1f l %.1f %.1f q %.1f %.1f %.1f %.1f Z"/>'
                 % (x - 20 * sc, base - 40 * sc, 4 * sc, -50 * sc, 18 * sc, -62 * sc,
                    12 * sc, 2 * sc, 12 * sc, 16 * sc, 10 * sc, 60 * sc))
        # arm reaching down to the soil
        g.append('<path d="M %.1f %.1f q %.1f %.1f %.1f %.1f" stroke="#2B1D14" stroke-width="%.1f" '
                 'fill="none" stroke-linecap="round"/>'
                 % (x + 6 * sc, base - 92 * sc, 26 * sc * lean, 18 * sc, 22 * sc * lean, 52 * sc, 9 * sc))
        # legs
        g.append('<path d="M %.1f %.1f l %.1f %.1f M %.1f %.1f l %.1f %.1f" stroke="#2B1D14" '
                 'stroke-width="%.1f" stroke-linecap="round"/>'
                 % (x - 10 * sc, base - 42 * sc, -6 * sc, 42 * sc,
                    x + 8 * sc, base - 42 * sc, 8 * sc, 42 * sc, 11 * sc))
        g.append('</g>')
        # sapling being planted
        g.append('<path d="M %.1f %.1f l 0 %.1f" stroke="#3E5F2E" stroke-width="%.1f" stroke-linecap="round"/>'
                 % (x + 30 * sc * lean, base, -30 * sc, 3.4 * sc))
        g.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#4C7A34"/>'
                 % (x + 30 * sc * lean, base - 34 * sc, 13 * sc, 9 * sc))
        return "".join(g)

    s.append(figure(w * 0.26, h * 0.86, 1.05, 1))
    s.append(figure(w * 0.52, h * 0.79, 0.8, -1))
    s.append(figure(w * 0.78, h * 0.92, 1.2, -1))
    for i in range(60):
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#FFE3AE" opacity="%.2f"/>'
                 % (rnd.uniform(0, w), rnd.uniform(h * 0.3, h * 0.9), rnd.uniform(1, 3.4),
                    rnd.uniform(0.15, 0.6)))
    s.append('</svg>')
    return "".join(s)


def scene_canopy_top(w=1200, h=900):
    """Aerial canopy texture."""
    rnd = random.Random(55)
    s = [svg_open(w, h)]
    s.append('<rect width="%d" height="%d" fill="#1D4A30"/>' % (w, h))
    greens = ["#2A6740", "#357A4C", "#43915B", "#54A468", "#6BB87C", "#1F5636", "#8ACB92"]
    for i in range(950):
        x, y = rnd.uniform(-30, w + 30), rnd.uniform(-30, h + 30)
        r = rnd.uniform(8, 40)
        s.append('<circle cx="%.0f" cy="%.0f" r="%.0f" fill="%s" opacity="%.2f"/>'
                 % (x, y, r, rnd.choice(greens), rnd.uniform(0.45, 1.0)))
    for i in range(240):
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#B7DCAE" opacity="%.2f"/>'
                 % (rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(2, 9), rnd.uniform(0.08, 0.4)))
    # a river cutting through
    pts = ridge(h * 0.55, h * 0.12, 7, w, 91, 0.55)
    d = "M %.1f %.1f" % pts[0]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cx = (x0 + x1) / 2
        d += " C %.1f %.1f %.1f %.1f %.1f %.1f" % (cx, y0, cx, y1, x1, y1)
    s.append('<path d="%s" stroke="#7FB6C4" stroke-width="52" fill="none" opacity=".9"/>' % d)
    s.append('<path d="%s" stroke="#A9D3DC" stroke-width="26" fill="none" opacity=".7"/>' % d)
    s.append(mist(w, h * 0.05, h * 0.3, "#DCEBDD", 0.16, seed=3, bands=3))
    s.append('</svg>')
    return "".join(s)


def scene_soil(w=1200, h=900):
    """Cross-section of living soil and roots — used for the carbon story."""
    rnd = random.Random(66)
    s = [svg_open(w, h)]
    s.append('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#DCE9CE"/><stop offset="1" stop-color="#BFD6AC"/>'
             '</linearGradient></defs>')
    s.append('<rect width="%d" height="%d" fill="url(#sky)"/>' % (w, h))
    surface = h * 0.32
    s.append('<path d="%s" fill="#4E3B29"/>' % smooth_path(ridge(surface, h * 0.012, 8, w, 4, 0.7), h, w))
    s.append('<path d="%s" fill="#3D2E20"/>' % smooth_path(ridge(h * 0.52, h * 0.02, 6, w, 6, 0.7), h, w))
    s.append('<path d="%s" fill="#31251A"/>' % smooth_path(ridge(h * 0.74, h * 0.02, 6, w, 8, 0.7), h, w))
    for i in range(320):
        s.append('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="%s" opacity=".45"/>'
                 % (rnd.uniform(0, w), rnd.uniform(surface, h), rnd.uniform(1, 5),
                    rnd.choice(["#6B563E", "#8A7050", "#2A2018"])))

    def root(x, y, ang, length, wdt, depth=0):
        if depth > 4 or length < 8:
            return ""
        x2 = x + math.cos(ang) * length
        y2 = y + math.sin(ang) * length
        out = ['<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" stroke="#C4A882" stroke-width="%.1f" '
               'fill="none" stroke-linecap="round" opacity=".85"/>'
               % (x, y, (x + x2) / 2 + rnd.uniform(-14, 14), (y + y2) / 2, x2, y2, wdt)]
        for _ in range(rnd.randint(1, 3)):
            out.append(root(x2, y2, ang + rnd.uniform(-0.85, 0.85), length * rnd.uniform(0.55, 0.8),
                            max(0.7, wdt * 0.65), depth + 1))
        return "".join(out)

    for k in range(6):
        x = w * (0.08 + k * 0.17) + rnd.uniform(-20, 20)
        # trunk above ground
        s.append('<path d="M %.1f %.1f l 0 %.1f" stroke="#5C4326" stroke-width="12" stroke-linecap="round"/>'
                 % (x, surface + 6, -h * rnd.uniform(0.1, 0.2)))
        th = h * rnd.uniform(0.1, 0.18)
        s.append(broadleaf(x, surface + 4, th * 1.6, th * 1.2, "#4A8B4E", rnd))
        s.append(root(x, surface + 8, math.pi / 2, h * 0.16, 8))
    # mycorrhizal filaments
    for i in range(120):
        x, y = rnd.uniform(0, w), rnd.uniform(surface + 20, h)
        s.append('<path d="M %.0f %.0f q %.0f %.0f %.0f %.0f" stroke="#E4D3B0" stroke-width=".9" '
                 'fill="none" opacity=".35"/>' % (x, y, rnd.uniform(-30, 30), rnd.uniform(-20, 20),
                                                  rnd.uniform(-50, 50), rnd.uniform(-30, 30)))
    s.append('</svg>')
    return "".join(s)


def avatar(name, seed, skin, hair, shirt, bg):
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img">']
    s.append('<rect width="120" height="120" rx="60" fill="%s"/>' % bg)
    s.append('<path d="M 60 122 c -30 0 -45 -13 -45 -29 c 0 -13 19 -21 45 -21 c 26 0 45 8 45 21 '
             'c 0 16 -15 29 -45 29 Z" fill="%s"/>' % shirt)
    s.append('<path d="M 60 118 v -46" stroke="%s" stroke-width="2" opacity=".25"/>' % shade(shirt, 0.5))
    s.append('<rect x="50" y="55" width="20" height="24" rx="9" fill="%s"/>' % shade(skin, 0.14))
    style = seed % 3
    # hair mass behind the head
    s.append('<ellipse cx="60" cy="%d" rx="%d" ry="%d" fill="%s"/>'
             % (46 if style != 1 else 50, 25 if style == 1 else 23, 26 if style == 1 else 23, hair))
    if style == 1:  # longer hair falling past the jaw
        s.append('<path d="M 36 46 q -3 24 3 34 q 9 -4 6 -34 Z" fill="%s"/>' % hair)
        s.append('<path d="M 84 46 q 3 24 -3 34 q -9 -4 -6 -34 Z" fill="%s"/>' % hair)
    s.append('<circle cx="60" cy="49" r="21" fill="%s"/>' % skin)
    if style == 0:  # short fringe
        s.append('<path d="M 39 46 q 3 -19 21 -19 q 18 0 21 19 q -8 -10 -21 -10 q -13 0 -21 10 Z" fill="%s"/>' % hair)
    elif style == 1:
        s.append('<path d="M 39 44 q 6 -18 21 -18 q 15 0 21 18 q -10 -7 -21 -7 q -11 0 -21 7 Z" fill="%s"/>' % hair)
    else:  # cropped with a bun
        s.append('<path d="M 39 47 q 0 -21 21 -21 q 21 0 21 21 q -6 -12 -21 -12 q -15 0 -21 12 Z" fill="%s"/>' % hair)
        s.append('<circle cx="83" cy="34" r="8" fill="%s"/>' % hair)
    s.append('<circle cx="52" cy="50" r="2.5" fill="#2B211A"/><circle cx="68" cy="50" r="2.5" fill="#2B211A"/>')
    s.append('<path d="M 52 59 q 8 6 16 0" stroke="#2B211A" stroke-width="2.2" fill="none" '
             'stroke-linecap="round"/>')
    s.append('<ellipse cx="45" cy="56" rx="4" ry="2.6" fill="#E08A72" opacity=".35"/>')
    s.append('<ellipse cx="75" cy="56" rx="4" ry="2.6" fill="#E08A72" opacity=".35"/>')
    s.append('</svg>')
    return "".join(s)


def logo(mono=False):
    """Rootstock mark: a leaf/hill silhouette with a root stem."""
    green = "#2F7A4F" if not mono else "currentColor"
    dark = "#1B4530" if not mono else "currentColor"
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" role="img">']
    s.append('<path d="M24 4 C 12 12 6 22 6 31 a 18 18 0 0 0 36 0 C 42 22 36 12 24 4 Z" fill="%s" opacity=".18"/>' % green)
    s.append('<path d="M24 9 C 14 16 9 24 9 31 a 15 15 0 0 0 30 0 C 39 24 34 16 24 9 Z" fill="%s"/>' % green)
    s.append('<path d="M24 14 v 28" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>' % dark)
    s.append('<path d="M24 26 q -8 -3 -10 -11 q 9 1 10 11 Z M24 32 q 8 -3 10 -11 q -9 1 -10 11 Z" fill="%s"/>' % dark)
    s.append('</svg>')
    return "".join(s)


def favicon():
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">']
    s.append('<rect width="48" height="48" rx="12" fill="#14301F"/>')
    s.append('<path d="M24 11 C 15 17 11 24 11 30 a 13 13 0 0 0 26 0 C 37 24 33 17 24 11 Z" fill="#C6F24E"/>')
    s.append('<path d="M24 16 v 22" stroke="#14301F" stroke-width="2.4" stroke-linecap="round"/>')
    s.append('</svg>')
    return "".join(s)


def pattern_leaves(w=600, h=600):
    rnd = random.Random(77)
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h)]
    for i in range(70):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(0, 360)
        sc = rnd.uniform(0.5, 1.5)
        s.append('<g transform="translate(%.0f %.0f) rotate(%.0f) scale(%.2f)" opacity="%.2f">'
                 '<path d="M0 0 q 18 -6 24 -26 q -20 2 -24 26 Z" fill="#2F7A4F"/></g>'
                 % (x, y, r, sc, rnd.uniform(0.05, 0.18)))
    s.append('</svg>')
    return "".join(s)


def partner_logo(name, seed):
    """Neutral wordmark placeholders for the 'trusted by' row."""
    rnd = random.Random(seed)
    w, h = 220, 48
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img">' % (w, h, w, h)]
    glyph = seed % 4
    if glyph == 0:
        s.append('<circle cx="24" cy="24" r="14" fill="none" stroke="currentColor" stroke-width="3"/>'
                 '<path d="M24 10 v28 M10 24 h28" stroke="currentColor" stroke-width="3"/>')
    elif glyph == 1:
        s.append('<path d="M24 8 L38 24 L24 40 L10 24 Z" fill="none" stroke="currentColor" stroke-width="3"/>')
    elif glyph == 2:
        s.append('<path d="M11 32 q 13 -22 26 0" stroke="currentColor" stroke-width="3" fill="none"/>'
                 '<path d="M11 24 q 13 -22 26 0" stroke="currentColor" stroke-width="3" fill="none" opacity=".55"/>')
    else:
        s.append('<rect x="11" y="11" width="26" height="26" rx="8" fill="none" stroke="currentColor" stroke-width="3"/>'
                 '<circle cx="24" cy="24" r="5" fill="currentColor"/>')
    s.append('<text x="50" y="31" font-family="Verdana,DejaVu Sans,sans-serif" font-size="17" '
             'font-weight="700" letter-spacing="-0.4" fill="currentColor">%s</text>' % name)
    s.append('</svg>')
    return "".join(s)


# ------------------------------------------------------------------- main ---
def main():
    print("Generating artwork ->", OUT)
    write("hero-split.svg", scene_hero_split())
    write("scene-canopy.svg", scene_canopy_top())
    write("scene-farm.svg", scene_farm_rows())
    write("scene-nursery.svg", scene_nursery())
    write("scene-planting.svg", scene_planting())
    write("scene-soil.svg", scene_soil())

    write("scene-misty-hills.svg", scene_landscape(
        "misty", 1200, 900,
        dict(sky_top="#E4EDE6", sky_bottom="#F4EFE2", sun=(880, 170, 60), sun_color="#FFF7DC",
             layers=[(0.42, "#A9C3B0"), (0.52, "#7FA98C"), (0.63, "#5B8C6B"), (0.74, "#3E6E50")],
             foreground=(0.86, "#27503A")), 101, kind="misty"))

    write("scene-valley.svg", scene_landscape(
        "valley", 1200, 900,
        dict(sky_top="#BFDCEA", sky_bottom="#E9F0DF", sun=(300, 150, 44), clouds=True,
             layers=[(0.34, "#93B6C4"), (0.44, "#6E9E86"), (0.55, "#4C8261")],
             water=0.72, water_color="#6FA8B8",
             foreground=(0.8, "#2E6244")), 202, kind="forest"))

    write("scene-highland.svg", scene_landscape(
        "highland", 1200, 900,
        dict(sky_top="#D9E7F0", sky_bottom="#F6EEDD", sun=(940, 200, 50), clouds=True,
             layers=[(0.36, "#B2C4CE"), (0.46, "#8AA9A2"), (0.58, "#628C6C"), (0.7, "#456E51")],
             foreground=(0.85, "#2A5740")), 303, kind="forest"))

    write("scene-wetland.svg", scene_landscape(
        "wetland", 1200, 900,
        dict(sky_top="#CFE6E4", sky_bottom="#F1EBD8", sun=(240, 190, 46), clouds=True,
             layers=[(0.4, "#9CC1B4"), (0.5, "#6FA189")],
             water=0.62, water_color="#79ADAA",
             foreground=(0.84, "#386B52")), 404, kind="broadleaf"))

    write("scene-orchard.svg", scene_landscape(
        "orchard", 1200, 900,
        dict(sky_top="#EAE2CE", sky_bottom="#F7F2E4", sun=(860, 210, 58), sun_color="#FFF4CE",
             layers=[(0.42, "#BFCBA0"), (0.54, "#9DB57F"), (0.66, "#7BA167")],
             foreground=(0.8, "#4E8455")), 505, kind="broadleaf"))

    write("scene-community.svg", scene_landscape(
        "community", 1200, 900,
        dict(sky_top="#F2D9AE", sky_bottom="#F7EBD4", sun=(360, 230, 64), sun_color="#FFF0C0",
             layers=[(0.44, "#C7B58C"), (0.56, "#9BA875"), (0.68, "#6E8F5C")],
             foreground=(0.82, "#416E48")), 606, kind="broadleaf"))

    for i, (nm, skin, hair, shirt, bg) in enumerate([
            ("a", "#E8B98F", "#3B2A20", "#2F7A4F", "#DFEBD8"),
            ("b", "#C68A5E", "#1F1712", "#C6F24E", "#E7E2D2"),
            ("c", "#8D5A3B", "#241A14", "#3E8E5A", "#DCE8EC"),
            ("d", "#F0C9A5", "#7A4A2A", "#1B4530", "#EFE6D4"),
            ("e", "#A8724B", "#2C1F17", "#8CC5A2", "#E3EADC")]):
        write("avatar-%s.svg" % nm, avatar(nm, i, skin, hair, shirt, bg))

    write("logo.svg", logo())
    write("favicon.svg", favicon())
    write("pattern-leaves.svg", pattern_leaves())
    for i, nm in enumerate(["Terraluma", "Northwind", "Cairnroot", "Beacon Co", "Vellum", "Highfield"]):
        write("partner-%d.svg" % (i + 1), partner_logo(nm, i))
    print("done.")


if __name__ == "__main__":
    main()
