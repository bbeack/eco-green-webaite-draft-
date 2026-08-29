# Rootstock — Farm & Forest

A complete, production-ready marketing site for **Rootstock**, a (fictional) regenerative farm
in the Welsh borders whose entire trading profit funds native woodland planting.

Static HTML, CSS and vanilla JavaScript. No framework, no runtime dependencies, no external
asset hosts — open `index.html` in a browser and the whole site works.

---

## Pages

| Page | File | What it does |
| --- | --- | --- |
| Home | `index.html` | Hero, mission, project carousel, how-it-works, impact figures, testimonial, CTA |
| Our Farm | `about.html` | Story timeline, four practice tabs, full "where the money goes" breakdown, team |
| Projects | `projects.html` | Filterable project grid, four detailed project sections, impact reporting, data tables |
| Get Involved | `get-involved.html` | Donation form with live calculator, monthly giving, volunteering, partnerships, gifting, FAQ |
| Contact | `contact.html` | Contact form, response-time table, visiting info, newsletter |
| **Design system** | `design-system.html` | Tokens, components, motion and accessibility documentation (linked in the footer) |
| Privacy policy | `privacy.html` | UK GDPR policy: what we collect, lawful bases, retention, rights |
| Terms of use | `terms.html` | Site terms, donation terms, volunteering, environmental-claims rules, liability |
| Cookie policy | `cookies.html` | Exactly what is stored in the browser, and why there is no cookie banner |
| Accessibility | `accessibility.html` | WCAG 2.2 AA statement, known gaps, farm access |
| Thank you | `thank-you.html` | Post-submission confirmation, personalised per capture type |
| Not found | `404.html` | Branded error page with recovery links |

Plus generated `sitemap.xml` and `robots.txt`.

## Information capture

Six form types are wired through one handler (`assets/js/forms.js`): newsletter, donation,
volunteer, partner, gift and contact.

- Validation on blur and on submit, with error text (never colour alone), `aria-invalid`,
  and focus moved to the first invalid field.
- Honeypot field on every public form to absorb bots.
- Submissions are saved to `localStorage` under `rootstock:leads` and replayed on the
  confirmation page, so the whole flow is demonstrable with no backend.
- The donation form recalculates amount, tree count, CO₂e and annual value live.

**To send submissions somewhere real**, set an endpoint — no markup changes needed:

```js
Rootstock.Forms.config.endpoint = 'https://your-collector.example/leads';
```

Each form POSTs `{ type, page, submittedAt, data }` as JSON. Useful helpers in the console:
`Rootstock.Forms.leads()`, `.export()`, `.clear()`.

## Design system

Documented in full at `design-system.html` and implemented entirely in `assets/css/style.css`.

- **Panels.** Every page is a vertical stack of rounded panels on warm paper (`#F2F1EB`). A
  `.section` *is* the panel — no wrapper markup — so a page only picks a tone: white,
  paper tint (`.section-alt`) or forest (`.section-deep`).
- **Colour.** Leaf greens rather than emerald, one lime accent reserved for giving, warm
  papers underneath. Light and dark are token swaps only; components never reference a raw
  colour. Every text pairing clears 4.5:1 in both themes.
- **Type.** Plus Jakarta Sans, self-hosted as one variable file per subset (49KB total, no
  third-party request — the cookie policy promises exactly that). A fluid `clamp()` scale with
  no typographic breakpoints, and body text never below 16px at any width.

## Motion

Scroll reveals (six variants), exit softening, staggered groups, headline word wipes, parallax,
pointer-tracked card tilt, magnetic buttons, animated counters and meters, marquees, a clip-path
drawer, and a page-transition veil. Every one of them is disabled under
`prefers-reduced-motion`, and a `<noscript>` fallback makes all revealed content visible when
JavaScript is unavailable.

## Structure

```
index.html …                built pages (commit these; this is what you deploy)
assets/css/style.css        the only stylesheet — tokens through components
assets/js/site.js           theme, nav, reveals, counters, tabs, accordions, carousel, parallax
assets/js/forms.js          validation, capture, donation calculator, confirmation page
assets/img/*.svg            all artwork, procedurally generated
assets/fonts/*.woff2        Plus Jakarta Sans, self-hosted (variable, 400-800)
src/*.html                  page content fragments (edit these)
tools/build.py              wraps fragments in the shared header/footer; writes sitemap + robots
tools/gen_art.py            regenerates every illustration from the palette
```

## Working on it

```bash
python3 tools/build.py      # rebuild pages after editing anything in src/
python3 tools/gen_art.py    # regenerate illustrations after changing the palette
npx http-server -p 8080 .   # or any static server
```

Header, footer, navigation and the icon set live in `tools/build.py` so they cannot drift
between pages. Content lives in `src/`. Built pages are committed, so the site can also be
deployed straight from the repository root with no build step.

## Before going live

1. Point `Rootstock.Forms.config.endpoint` at a real collector, and connect a payment provider
   to the donation form.
2. Set `BASE_URL` in `tools/build.py` to your domain and rebuild (updates `sitemap.xml`/`robots.txt`).
3. Replace the placeholder social handles in `tools/build.py` (`rootstockearth`).
4. Swap in real photography if you prefer it to the generated illustrations — the layouts expect
   4:3 or wider images, and the hero expects a composition that reads left-to-right (the panel
   fades its left edge into white).

## Responsiveness

Verified at 320, 360, 390, 414, 480, 600, 768, 834, 1024, 1180, 1280, 1440, 1680, 1920 and
2560px across all twelve pages: no horizontal overflow anywhere, no text below its intended
minimum, and touch targets within WCAG 2.2 AA. The layout collapses from the two-column hero to
a stacked one at 1080px, drops the desktop nav for the drawer at 900px, and goes single-column
at 640px.

## Notes

Rootstock is a fictional organisation created for this build. Figures, projects, staff, the
company number and the address are illustrative.
