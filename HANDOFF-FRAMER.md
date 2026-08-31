# Handoff: rebuild this site in Framer

You are working directly with a Framer project. This repository contains a
finished, working version of the site, built as static HTML/CSS/JS. Your job is
to reproduce it inside Framer.

Everything below is the spec. The repository is the reference implementation —
read it rather than guessing.

---

## First, a decision to put to the user

There are two ways to do this, and they give very different results. Ask which
they want before building.

**A. Native Framer rebuild (recommended).** Recreate the pages as real Framer
frames, text layers, stacks and styles via `framer.agent.applyChanges`. Slower
to build, but the client can then edit every heading, colour and image on the
canvas. This is the point of using Framer.

**B. Code components.** `framer/*.tsx` in this repo already contains four
working, self-contained code components (header, hero, CTA, footer). They can be
pulled in through Framer's Code Sync plugin in about two minutes. They render
correctly but are opaque to Framer's editor — nobody can click a heading and
retype it.

Most people asking for "the site in Framer" want A. B is a shortcut that
forecloses on the reason they moved to Framer. If they want a mix, B is
reasonable for the hero (which has fiddly floating cards) and A for everything
else.

---

## The design system

Ported from `assets/css/style.css`, which is the source of truth. Create these
as Framer colour and text styles first — do not hard-code values on layers.

### Colour

| Token | Hex | Used for |
| --- | --- | --- |
| Paper | `#F2F1EB` | page background; the panels sit on it |
| Panel | `#FFFFFF` | default section background |
| Panel tint | `#EFEEE7` | alternating sections |
| Forest 900 | `#14240F` | dark sections, CTA band, footer socials |
| Forest 600 | `#3D6B34` | buttons |
| Forest 500 | `#47793B` | brand text, the highlighted word in headlines |
| Forest 100 | `#E6F0DF` | icon circles, soft fills |
| Lime 500 | `#C9F04D` | the single accent — giving actions only |
| Lime 600 | `#B2E23A` | lime hover |
| Ink 900 | `#15170F` | body and heading text |
| Ink 500 | `#5F6459` | muted text |
| Ink 400 | `#696E62` | hints, captions, footer meta |
| Border | `#E7E5DB` | card and input borders |
| Border strong | `#D8D5C8` | dividers |
| Clay 500 | `#C3714A` | degraded-land imagery only |

Two rules that matter: lime is reserved for donate/give actions and appears at
most once per screen; lime is never used for text on a light background — it
fails contrast at every size. Every pairing above clears 4.5:1 in both themes.

### Type

**Plus Jakarta Sans** throughout. Weights 400–800. Headings 600–700, body 400.

| Role | Size (min → max) | Line height | Tracking |
| --- | --- | --- | --- |
| Display (hero) | 2.70 → 5.10rem | 1.0 | -0.038em |
| H1 | 2.35 → 4.35rem | 1.04 | -0.036em |
| H2 | 1.95 → 3.30rem | 1.08 | -0.034em |
| H3 | 1.22 → 1.55rem | 1.12 | -0.032em |
| Lead | 1.08 → 1.24rem | 1.62 | normal |
| Body | 1.00 → 1.06rem | 1.62 | normal |
| Small | 0.875 → 0.94rem | 1.62 | normal |
| Eyebrow | 0.75rem | — | 0.13em, uppercase, weight 700 |

Body never goes below 16px at any width.

**Important:** Plus Jakarta Sans ships an unusually narrow space glyph
(0.175em against a typical 0.30em), so word gaps look collapsed at large sizes.
The site applies `word-spacing: 0.085em` globally and `0.1em` on the display
headline. Reproduce that or the hero will read as "Growfood."

### Layout

The page is a vertical stack of **rounded panels on warm paper** — this is the
defining visual idea, so get it right first.

- Page background: paper `#F2F1EB`
- Each section: a rounded rectangle, max width **1660px**, centred
- Gap between panels and to the viewport edge: **`clamp(0.4rem, 0.9vw, 1rem)`**
- Panel corner radius: **`clamp(18px, 1.9vw, 32px)`**
- Padding inside a panel: **`clamp(1.15rem, 0.35rem + 3.6vw, 4.75rem)`** horizontal,
  **`clamp(3rem, 1.6rem + 4.6vw, 6.5rem)`** vertical
- Content inside a panel is capped so the header, hero copy and every section
  align on one vertical. Verify this at 1440px and 2560px.

Other radii: cards 20px, small cards 14px, inputs 10px, buttons and pills fully
rounded.

Shadows are green-tinted, never grey — `rgb(28 40 24 / …)` — and soft. Cards
rest flat and lift on hover.

### Breakpoints

- **1080px** — hero goes from two columns to stacked, artwork above copy
- **900px** — desktop nav is replaced by the drawer
- **640px** — everything single column

---

## Pages

Five main pages, four legal pages, plus a confirmation and a 404. Read each
`.html` file at the repo root for exact copy — do not rewrite the words.

| Page | File | Sections in order |
| --- | --- | --- |
| Home | `index.html` | Hero · impact ticker · mission (tinted, with trusted-by row) · projects carousel + lime signup · how-it-works (tinted) · impact figures (dark) · testimonial · CTA band |
| Our Farm | `about.html` | Banner · farm image + 4 stats · story timeline · practice tabs (tinted) · where-the-money-goes with meters · team · CTA |
| Projects | `projects.html` | Banner · 4 stats · filterable project grid · four project detail sections (alternating tint) · film (dark) · impact reporting + data table · CTA |
| Get Involved | `get-involved.html` | Banner · donation form with live calculator + sticky summary · monthly giving (tinted) · volunteering + booking form · partnerships (dark) · gift · FAQ accordion |
| Contact | `contact.html` | Banner · 4 contact cards · contact form + response-time table · visit info (tinted) · CTA |
| Legal | `privacy.html` `terms.html` `cookies.html` `accessibility.html` | Banner · sticky contents nav · prose |
| Confirmation | `thank-you.html` | Personalised per submission type |
| 404 | `404.html` | Branded, with recovery links |

The footer is light on the paper: brand + signup, three link columns, socials as
dark green circles, legal line. The header is transparent over the hero with
centred nav and one lime CTA.

---

## Artwork

`assets/img/*.svg` — 26 files, all generated by `tools/gen_art.py` rather than
photographed, so the site has no external image dependencies.

Upload them to Framer as assets. The hero is `hero-split.svg`: restored forest
on the left dissolving into cracked bare earth on the right. Its composition is
deliberate — the canopy sits at 20–50% of the frame width because the hero panel
fades its left edge into white, and artwork hard against the left edge gets
washed out before it is seen. Crop it at roughly 46% horizontal focus.

If the client prefers photography, the layouts expect 4:3 or wider.

---

## Forms

Six types: newsletter, donation, volunteer, partner, gift, contact. Build them
with Framer's own form handling.

The donation form is the one with real logic — read `assets/js/forms.js`:

- £3 funds one tree; the calculator shows amount, tree count, CO₂e and annual value
- One-off vs monthly; preset amounts plus a custom field
- CO₂e is `trees × 0.025` tonnes over 20 years
- The submit button label changes with the amount ("Give £30 a month")

Validation rules worth keeping: validate on blur, describe errors in words as
well as colour, move focus to the first invalid field, and put a honeypot on
every public form.

---

## Motion

Restrained and purposeful. Scroll reveals (fade/rise, ~700ms, ease-out-expo,
staggered ~70ms), counters that animate once on entry, progress meters that fill
on entry, cards that lift 5px on hover, buttons that lift 2px.

Everything must be disabled under `prefers-reduced-motion`.

---

## Accessibility — treat as requirements, not aspirations

The site makes these promises publicly on `accessibility.html`, so the Framer
build has to keep them:

- 4.5:1 contrast minimum, verified in both light and dark
- Visible focus states on everything interactive
- 44×44px touch targets on buttons and controls; 24×24px on inline links
- All motion disabled under reduced-motion
- Real labels on form fields, errors in text
- Meaningful alt text; decorative artwork hidden from screen readers

---

## Ground rules

1. **Don't rewrite the copy.** It was written deliberately — plain, specific,
   and honest about failures. Reproduce it exactly.
2. **Styles before layers.** Create the colour and text styles first, then build
   with them, so the client can retheme in one place.
3. **Check 320px and 2560px.** The static site has zero horizontal overflow at
   both; the Framer build should match.
4. **The numbers are illustrative.** Rootstock is a fictional organisation
   created for this build — figures, projects, staff, the company number and the
   address are all invented. If this is going live for a real client, every one
   needs replacing.
