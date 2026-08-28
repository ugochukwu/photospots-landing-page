---
title: "Design handoff: photospots.net Fieldbook redesign (2026-08-28)"
summary: High-fidelity design spec for the Fotospots landing site — landing (EN+DE), privacy, 404, and the deferred shared-spot page — with palette, typography, layout grids, copy, and interaction rules; the binding definition of done for beads under epic photospots-landing-page-91e.
updated: 2026-08-28
status: living
---

# Handoff: photospots.net redesign (Fieldbook 2.0)

## Overview
Full redesign of photospots.net, the marketing and universal-link site for **Fotospots · Photo Fieldbook** (iOS, App Store id 6466506171), in the Fieldbook visual language derived from the Mugo Works brand system. Four pages: landing (EN + DE), spot-blind shared-spot landing (`/s/*`), privacy policy (`/privacypolicy`), and 404.

## About the Design Files
The files in `designs/` are **design references created in HTML** (Design Component prototypes). They show the intended look and behavior; they are not production code to deploy directly. The task is to **recreate these designs as a static site** served from the existing `/srv/photospots` root behind Caddy (per ADR-0005 in the Fotospots repo). Plain static HTML + CSS (+ a few lines of JS for the language toggle) is the right target; no framework is needed. Open each `.dc.html` in a browser (with `support.js` and `assets/` alongside) to see the rendered design.

## Fidelity
**High-fidelity.** Colors, type, spacing, copy, and layout are final. Recreate pixel-perfectly. All copy (EN and DE) is the approved App Store listing 2.0 voice — do not rewrite it.

## Site map & routing
| URL | Design file | Notes |
|---|---|---|
| `/` | `Photospots Landing.dc.html` | EN default; DE via toggle |
| `/s/*` | `Shared Spot.dc.html` | MUST be spot-blind: never read/log the `u` query parameter (ADR-0005) |
| `/privacypolicy` | `Privacy Policy.dc.html` | Keep this exact URL — the shipping app links it (`SettingsScreen.swift:114`) |
| any other path | `404.dc.html` | |

Non-design requirements already decided in ADR-0005 (Fotospots repo, `docs/adr/2026-08-13-shareable-spot-links-private-transport.md`):
- Serve the AASA file at `/.well-known/apple-app-site-association` on BOTH `photospots.net` and `www.photospots.net`, status 200, `content-type: application/json`, no redirect between hosts for that path.
- Smart App Banner on all pages: `<meta name="apple-itunes-app" content="app-id=6466506171">`.
- The `/s/` page never reads the `u` parameter; the handoff happens on-device.

## Design tokens (Fieldbook palette)
Grounds (max 2 per page: cream + one purple brand-moment section):
- `--ground: #F6F2EA` (cream, page)
- `--ground-brand: #4F489B` (Fotospots brand purple; iPad section only)
- `--bezel: #2A2620` (device bezel, also headline ink)

Text on cream: ink `#2A2620` (headings), body `#6B655C`, muted/mono `#96908A`, hairline `#DCD5C7`.
Text on purple: bright `#F6F2EA`, muted `#BEB9E0`, hairline `#3D3878`.
Interactive: `#4F489B`, hover `#5E55B5` (buttons) / `#665DBE` (links). Mugo works mark ink on light: `#1e4d30`.

Type (Google Fonts):
- **Space Grotesk** 400/500/700 — headlines, body, buttons. H1 72–76px / lh 0.98 / ls −0.04em; H2 46–52px / lh 1.05–1.1 / ls −0.03em; card titles 22–24px 700; body 16–19px / lh 1.6–1.65.
- **Space Mono** 400/700 — labels and meta only. Caps labels 11–13px, letter-spacing 0.14–0.2em; numbered list markers 22–26px 700 purple; lowercase wit lines prefixed `//`.

Radii: buttons 6px, app icon img 8–10px, device bezels 34–46px. No shadows, no gradients. Default links: `a { color: #4F489B }`, hover `#665DBE`, no underline.

Decoration: topographic contour lines are the ONLY motif — SVG paths, `stroke: #96908A`, `stroke-width: 1.5`, group `opacity: 0.55` inside a wrapper at `opacity: 0.13`, absolutely positioned behind hero/closing sections.

Device frame (drawn, editorial — not a hardware render):
- Wrapper: `background: #2A2620`, padding 6–13px, radius 36–46px, `outline: 1.5px solid #96908A` (`#BEB9E0` on purple) with `outline-offset: 4–6px` (the "keyline").
- Screenshot img inside, radius = wrapper radius − padding × ~1.
- iPhone only: a flat Dynamic Island pill (`#2A2620`, ~68–90px wide, radius = half height) absolutely centered near the top, covering the hardware island in the raw capture.

## Screens
### Landing (`/`)
1. **Header**: app icon (34px, r8) + "Fotospots" (20px 700) + "PHOTO FIELDBOOK" mono label; under the wordmark the Mugo Works endorsement lockup (13px M mark + "BY MUGO WORKS" mono 10px ls 0.14em, links to mugoworks.com). Right: EN/DE toggle (mono 12px; active = purple 700 with 1.5px purple underline) + "Get the app" button. Hairline below.
2. **Hero**: two-col grid 1.15fr/0.85fr, gap 64. Left: purple mono eyebrow `// 2.0 · THE FIELDBOOK RELEASE`, 220px hairline rule, H1 "A map you build yourself.", lead paragraph, CTA button "Download on the App Store" + mono "IPHONE + IPAD". Right: iPhone frame (330px) with `i1-{lang}.png`. Topo contours behind.
3. **"WHAT YOU DO WITH IT"**: hairline + mono label; grid `minmax(0,1fr) minmax(0,0.95fr)` gap 72. Left: three hairline-separated stanzas, each mono purple number (01/02/03) + title + body: Keep a place / Plan the next one / Hand one over. Right: two fluid iPhone frames (1fr/1fr grid, max 528px, first offset 56px down) with `i3` and `i6`.
4. **iPad brand moment** (purple full-bleed): mono eyebrow "ON IPAD", rule, H2 "The spot docks. The map stays open.", body, centered iPad frame (860px) with `p2-{lang}.png`.
5. **Closing**: centered H2 "Give it a year." + paragraph + CTA. Topo contours behind.
6. **Footer**: hairline; left mugo works credit (20px mark + "A MUGO WORKS PRODUCT" → mugoworks.com), center mono links PRIVACY POLICY · APP STORE, right `// 2.0`.

German versions of every string, image (`-de` screenshots), and App Store URL (`/de/`) are in the design file's DE block — lift them verbatim.

### Shared spot (`/s/*`)
Centered single viewport on cream with topo contours. Header (wordmark + EN/DE toggle), then: purple mono eyebrow "A SPOT, HANDED TO YOU", rule, H1 "Someone handed you a place.", body, App Store CTA, and the mono footnote `// this page never sees the spot. the handoff happens on your device.` Footer: mugo credit + privacy link. DE strings in the file.

### Privacy policy (`/privacypolicy`)
900px column. Header with ← BACK. Mono eyebrow "PRIVACY POLICY", H1 "Your map stays yours.", lead, then five hairline-separated numbered sections (01 What the app stores / 02 No tracking, no profiles / 03 Location and photos / 04 Sharing a spot / 05 Questions). **The legal text must be reviewed against the currently published policy before it ships.**

### 404
Centered: app icon, mono "404 // OFF THE MAP", rule, H1 "Nothing pinned here.", one bilingual body line, link "Back to the start →".

## Interactions & state
- **Language toggle** (landing + shared spot): swaps all copy, screenshots, and App Store URLs between EN and DE. Persist in `localStorage` key `photospots-lang` (`"en"`/`"de"`); read on load, default EN. In production, consider `?lang=`/`Accept-Language` as the initial default instead.
- Button hover: `#4F489B → #5E55B5`. Link hover: muted `#96908A → #4F489B`; default links `#4F489B → #665DBE`. No other motion — default to stillness.
- Responsive: the prototypes are desktop-first (1200px max content width, 64px side padding). Grids use `minmax(0, …)` so they hold down to ~900px; below that, stack hero and stanza grids to one column and let phone pairs stay side-by-side (they are fluid). Minimum touch targets 44px on mobile.

## Assets (`designs/assets/`)
- `shots/i1|i3|i6-{en,de}.png` — raw iPhone 6.9" captures (1320×2868, include hardware Dynamic Island — the drawn pill must cover it). `shots/p2-{en,de}.png` — raw iPad 13" landscape captures. Source: app-store-listing repo, `screenshots/raw/`.
- `app-icon.png` — shipping app icon (from `Assets.xcassets`).
- `mark-on-light.svg` / `mark-on-dark.svg` / `mark-on-green.svg` — Mugo Works M-peaks mark (brand rules: on cream use `mark-on-light`, never recolor, never more than one logo form per surface).
- Fonts via Google Fonts: `Space+Grotesk:wght@400;500;700`, `Space+Mono:wght@400;700`. Self-hosting is fine and preferred for a production static site.

## Files
- `designs/Photospots Landing.dc.html` — landing, EN + DE
- `designs/Shared Spot.dc.html` — /s/ page, EN + DE
- `designs/Privacy Policy.dc.html` — /privacypolicy
- `designs/404.dc.html`
- `designs/support.js` — prototype runtime only (needed to open the `.dc.html` files); not part of the production site
