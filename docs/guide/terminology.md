---
title: Terminology
summary: This project's binding domain language for code, docs, and ADRs.
updated: 2026-08-28
status: draft
---

# Terminology

This project's domain language. These terms are **binding**: use them exactly — in code
(variable, type, function, module, and file names), documentation, ADRs, commit messages, bead
titles, and PR text. General industry terms (UI, API, HTTP…) are not defined here.

**Status: draft, first pass.** Written from the app repository's own product docs
(`design-handoff/app-store-listing-2.0-brief.md`, `docs/product/foundations.md` in
`~/Dev/Fotospots`) for Michel's review — this landing-page repo does not own the product's
domain model, it only has to stay consistent with it. If a needed concept has no term yet, add
it here in the same change rather than inventing an ad-hoc name.

## Product identity

- **Fotospots** — the product's name, going forward. The App Store listing name is
  `Fotospots · Photo Fieldbook` (locked at plan time in the app repo's 2.0 listing brief); this
  site uses "Fotospots" as the wordmark and "Photo Fieldbook" as its subtitle/tagline.
- **Photo Spots** — the retired 1.x name (`Photo Spots - Collect & Share`). Never use it as the
  product's name in new copy; it may appear only where quoting the old listing for historical
  contrast.
- **Fieldbook** — the 2.0 experience: a self-curated, hand-built map of places worth
  photographing. Used as a noun for the product's character ("the Fieldbook release"), not as a
  synonym for any one screen.

## Domain objects (from the app; kept consistent here)

- **Spot** — a single place the owner has saved. Never "location" or "pin" as the primary noun
  for the object itself (a pin is how a spot is drawn on the map).
- **Pin** — the map marker for a spot, or for a cluster of spots. Fair game as a design/UI term.
- **Wishlist** — spots the owner wants to shoot but has not yet. Not "bucket list" or "saved for
  later."
- **Map** — the primary surface. Do not call it a "dashboard," "feed," or "home screen" in
  copy; it is a map, and calling it anything else undersells the product's whole point.

## Voice constraints (binding on this site's copy)

- No follow-graph or social-network vocabulary: never "share with the community," "connect with
  photographers," "discover what others are shooting," or any "feed." Sharing is one person
  handing a spot to one person they chose.
- No hype, no superlatives ("best," "amazing," "revolutionary," "ultimate," "powerful"), no
  emoji, no trailing dots (…).
- No em dashes and no en dashes anywhere in committed copy. Use commas, parentheses, colons, or
  separate sentences.
- Warm and inviting, never exclusionary: state what Fotospots is and let the reader decide it
  suits them; never tell a reader who the app is not for.

## This repo's own structural vocabulary

- **Eyebrow** — the small monospace label above a section's headline (e.g. a waypoint dot plus
  a short caps label). Echoes the app's own EXIF-style metadata stamps; do not call it a
  "kicker" or "tag" in code or docs.
- **Spread** — a two-column section pairing a statement/body with a phone or iPad screenshot,
  alternating sides down the page (named for a book's two facing pages, matching the
  "fieldbook" concept). Used in CSS class names (`fs-spread`) and section comments.
- **Frame** — a flat rendered device bezel (dark `#2A2620`, rounded corners) around the app
  screen, with a thin muted-color keyline outline offset a few pixels outward. The Dynamic
  Island is baked into the iPhone raws where applicable. Named with the `fs-shot` family in
  the shipped source: `fs-shot` as the base marker in markup, plus size variants
  `fs-shot-iphone-lg`, `fs-shot-iphone-sm`, and `fs-shot-ipad` that carry the CSS rules. Not
  "mockup" or "device frame" in code, to keep one name for one thing.

## Deprecated — do not use

| Banned term | Use instead |
|-------------|-------------|
| Photo Spots (as the product name in new copy) | Fotospots |
| feed / follow / discover (any social-network framing) | map, spot, wishlist, sharing (one person to one person) |
| dashboard (for the map) | map |
