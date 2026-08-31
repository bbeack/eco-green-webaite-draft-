# Rootstock components for Framer

React code components that reproduce the Rootstock site's design system inside a
Framer project. They exist because Framer's GitHub sync only accepts `.tsx`
files — it imports React components onto a Framer canvas, and has no way to
take a static HTML site. See the note on limitations at the end.

## What's here

All four are **generated and self-contained**: each imports only `react` and
`framer`, both of which Framer provides. Nothing references another file in the
project, so there is no import for Framer to resolve.

| File | What it is |
| --- | --- |
| `SiteHeader.tsx` | Brand, centred nav, lime CTA, mobile drawer, theme toggle. |
| `HeroSection.tsx` | Hero panel: copy, email capture, stats, artwork, floating cards. |
| `CallToAction.tsx` | The dark call-to-action panel. |
| `SiteFooter.tsx` | Footer: brand, sign-up, link columns, socials, legal line. |
| `assets/` | The scene artwork, for uploading into Framer once. |

Each file is around 170KB, because the stylesheet, the font and the artwork are
inlined into every one. That is deliberate: a duplicated *generated* file costs
nothing to maintain — `tools/framer_export.py` rebuilds all four from one
source — and it buys certainty that they load.

## Getting them into Framer

1. In Framer, open the **Code Sync** plugin and connect this repository.
2. Select the four `.tsx` files in `framer/` and pull them in. Everything else
   in the repo will still show as "Unsupported" — that is expected and fine.
3. Drag a component onto a page. Each one carries its own defaults, so it looks
   right immediately.
4. Upload the SVGs from `framer/assets/` and set them on the **Artwork** and
   **Thumb** properties.

### If a component won't drop onto the canvas

Two things caused this in the first cut, both now fixed:

- **A shared module.** The components used to import a common `Rootstock.tsx`.
  If Framer can't resolve that import the file errors and won't instantiate.
  They are now self-contained, so there is no import to fail.
- **A zero-height header.** `SiteHeader` used `position: fixed`, which takes its
  content out of flow — the component measured 0px tall and landed on the canvas
  as an empty box. Sticky is now **off** by default, so the header sits in normal
  flow with real height. Pin it with Framer's own position controls; turn Sticky
  on only if you specifically want CSS `position: fixed`.

If something still won't place, check the file for an error badge in Framer's
code editor — that tells you it failed to compile, which is a different problem
from it being the wrong kind of file.

## How the styling works

Framer components share one document, and Framer owns `<body>`. So the
stylesheet can't be dropped in as-is. `tools/framer_export.py` rewrites it:

- every selector is scoped under `.rootstock`, so nothing leaks onto the Framer
  page — and the page's own CSS doesn't leak in
- `:root` and `body` rules move onto that wrapper, which is `display: flow-root`
  so panel margins don't collapse out of it and expose the page behind
- the dark theme becomes `.rootstock[data-theme="dark"]`, with a
  `prefers-color-scheme` block so each component's **Theme → Auto** works
- keyframes are prefixed `rs-`, so a `spin` or `fade-up` in your Framer project
  can't collide with the site's
- Plus Jakarta Sans is embedded as a data URI, and the artwork the components
  always need is inlined too — the components make **no third-party requests**,
  which keeps the promise the site's own cookie policy makes

The component sources live in `tools/framer_components/`. Edit those, or
`assets/css/style.css`, then regenerate:

```bash
python3 tools/framer_export.py
```

That keeps the stylesheet the single source of truth for both the site and the
Framer components, and rebuilds all four self-contained files from it.

## Shared properties

Every component has:

- **Theme** — Auto (follows the viewer's OS), Light or Dark.
- **Brand font** — on uses the embedded Plus Jakarta Sans; off inherits whatever
  font the Framer project sets.

The hero and footer sign-up forms also take an **Endpoint**. Left empty they
validate and confirm locally, which is what you want while designing. Set it to
a URL and each submission is POSTed as
`{ email, source, submittedAt }`.

## Limitations, stated plainly

- **These were verified outside Framer, not inside it.** They compile, type-check
  cleanly against React 18 and 19 types, render correctly, and pass a suite
  covering the forms, theme switching, the drawer, counters and layout from
  320px to 2560px — all in a headless browser against a deliberately hostile
  host page — including each component rendered **alone**, which is how Framer
  places them. What I could not do is open Framer and drop them on a canvas.
  Expect small adjustments there, particularly around sizing.
- **This is four components, not the site.** The other sections — mission,
  projects, the donation form, the legal pages — are not ported. They can be, on
  the same pattern.
- **Framer owns the page.** Navigation, page structure, SEO and hosting are
  Framer's, not this repo's. The components fill sections of a Framer page; they
  don't reproduce the site's routing.
- **The multi-page site is unaffected.** It remains the deployable thing in this
  repo; nothing here changes it.
