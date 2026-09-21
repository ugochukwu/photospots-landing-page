---
title: "ADR-0001: Netlify hosting and a spot-blind 200 landing at /s/"
summary: Move photospots.net from GitHub Pages to Netlify so share paths can return HTTP 200, and serve one spot-blind static landing at /s/* and /share/* via a Netlify rewrite.
updated: 2026-09-21
status: living
---

# ADR-0001: Netlify hosting and a spot-blind 200 landing at /s/

## Status

Accepted. Supersedes the hosting-medium assumption (netcup plus Caddy) recorded in the Fotospots app repository's ADR-0005, and only that assumption. ADR-0005's privacy model (the spot-blind, device-only share handoff) is kept, not replaced. Completes the app-repo bead Fotospots-jya.3 ("static spot-blind landing at /s/*").

## Date

2026-09-21

## Context

A spot share link looks like `photospots.net/s/<token>?u=<icloud CKShare url>`. It is an iOS universal link. When Fotospots is installed, iOS intercepts the tap and opens the app directly, and this web page is never loaded. When the app is not installed, the browser falls through to the web and loads `/s/<token>`.

Here is the wall. GitHub Pages serves a file only when a file exists at that path. `/s/<token>` is a made-up path with no matching file on disk, so Pages answers with its 404 page and, importantly, an HTTP 404 status. A link crawler (WhatsApp, iMessage, Signal, Slack) that receives a 404 shows no preview at all. Pages has no setting that makes it return 200 for a path that is not a real file. This is not a misconfiguration we can fix on Pages; it is what Pages is.

app-repo ADR-0005 chose a private share transport and assumed the web side could serve these paths, referencing a netcup plus Caddy setup that could rewrite `/s/*` to a static page. We never stood that up. The live site has been GitHub Pages the whole time (`gh api repos/ugochukwu/photospots-landing-page/pages`: branch `master`, path `/`). So the hosting half of that assumption is stale, and Fotospots-jya.3 has stayed open because Pages cannot satisfy it.

## Decision

Move photospots.net hosting to Netlify and add a `netlify.toml` at the repo root that does three things.

1. No build. Publish the repository root exactly as committed, the same set of files Pages serves today. Netlify runs no build command.

2. A rewrite, not a redirect, for `/s/*` and `/share/*` to a single static file, `s.html`. The difference matters. A redirect (301 or 302) tells the browser to go fetch a different URL, and a crawler that lands on a 404 first still sees the 404. A rewrite keeps the URL bar on `/s/<token>` and returns HTTP 200 with the landing's HTML in the same response. Think of it as the receptionist handing you the brochure at the same desk, rather than sending you up to another floor to ask again. In `netlify.toml` a rewrite is a redirect rule with `status = 200`.

3. A header rule that sets `Content-Type: application/json` on `/.well-known/apple-app-site-association`, and a self-referential 200 rule that pins `/.well-known/*` so nothing rewrites or redirects it.

The landing at `s.html` is spot-blind. It is one static HTML file, served identically for every `/s/*` and `/share/*` URL. It never reads the token and never reads the `?u` query parameter, and it shows no per-spot data. It carries a generic invitation, a Download on the App Store link, the Smart App Banner meta, and generic Open Graph and Twitter tags so a crawler renders a clean, spot-free card. Its only script is the language toggle, which reads `localStorage` and sets `data-lang`, never `location.search`.

Why spot-blind is a hard line, not a preference: the `u` parameter is an iCloud CKShare URL, which is a capability. Anyone holding it can reach the shared record. A web page that read it, logged it, or reflected it into the DOM would leak that capability into browser history, referrer headers, crawler caches, and analytics. So the web page must never touch it. The real handoff is device-only: the universal link opens the app, and the app resolves the share. This is exactly ADR-0005's invariant, kept intact under the new host.

## Consequences

Positive. Share previews work: a crawler gets a 200 and a generic card instead of a 404. Fotospots-jya.3 can close. As a side benefit, Netlify gives a deploy preview per pull request, which the forge adapter notes Pages does not.

Costs (nothing here is free). We now run a second hosting provider and have to understand its edge behavior, most sharply its domain-level redirect (see Risks). There is a DNS cutover with a propagation window. The forge and stack adapters currently describe GitHub Pages as the deploy target; both will need updating after cutover, tracked as a follow-up rather than folded in here.

## Options considered

| Option | Why not (or why) |
|--------|------------------|
| Stay on GitHub Pages, redirect with client JS | Does not work. Pages returns a 404 status no matter what the page does, and crawlers do not run JS, so the preview is already lost before any script runs. |
| netcup plus Caddy (the ADR-0005 assumption) | A full server to provision, secure, and keep patched for what is a static site. Heavier than the problem. |
| Cloudflare Pages or Workers | Viable. More moving parts than a two-rule `netlify.toml`, and no reason to prefer it here. |
| Netlify rewrite | Chosen. A static host that can return 200 for a synthetic path with a few lines of config, and gives PR previews. |

## Migration sequence

Ordered so that Pages stays a working fallback until the new host is proven.

1. Connect this repository to Netlify (Michel's step). No DNS change yet.
2. Verify on the `*.netlify.app` preview URL: `/s/<anything>` returns 200 with the generic card, and the AASA returns 200 as `application/json`.
3. DNS cutover: point photospots.net (apex and www) at Netlify.
4. Verify the AASA on both hosts (see the top risk below).
5. Only after the cutover is confirmed healthy, retire the Pages `CNAME` and the Pages workflow. This change does not touch `CNAME`, `.nojekyll`, the Pages workflow, or the existing AASA content, precisely so that step 5 is a separate, deliberate act.

## Rollback

Revert DNS to GitHub Pages. Because this change leaves `CNAME`, `.nojekyll`, the Pages workflow, and the AASA in place, Pages remains a live, correct target throughout the migration. Rollback is a DNS change measured in minutes to propagate, not a rebuild.

## Risks

Top risk: the AASA must return 200 with no redirect on both hosts. Apple's CDN fetches `https://<host>/.well-known/apple-app-site-association` directly and requires an HTTP 200 with no redirect. Netlify applies a domain-level primary-domain redirect by default, a 301 from the non-primary host to the primary one (for example apex to www, or the reverse). `netlify.toml` cannot disable that redirect; it is a domain setting. If that redirect applies to the apex, the AASA fetch gets a 301 and universal links silently stop opening the app, with no error a user would see. After connecting the site, it must be verified that the AASA returns 200 with no `location:` header on BOTH `photospots.net` and `www.photospots.net` (a `curl -sI` on each), and the domain configuration adjusted until that holds.

Second: Apple caches the AASA, normally minutes to hours and occasionally up to 24 hours. Any coordinated launch needs slack for propagation.

Third: the DNS cutover has its own propagation window during which some resolvers see Pages and some see Netlify. Both serve the same files, so this is tolerable, but the AASA verification in step 4 should be repeated once DNS has settled.

## References

- `netlify.toml`, `s.html` (this repository)
- `docs/adapters/stack.md`, `docs/adapters/forge.md` (both say GitHub Pages today; update after cutover)
- Fotospots app repo: ADR-0005 (private share transport, spot-blind invariant) and bead Fotospots-jya.3
- Landing-page bead photospots-landing-page-s8z
