---
title: Stack adapter
summary: Every command an agent runs against this project's code — build, test, lint, the CI-mirror quality gate, running the app, and the UI render check.
updated: 2026-08-28
status: living
---

# Stack adapter

Every command an agent runs against this project's code lives here. Core kit files
(CLAUDE.md, the subagents, the skills) reference the section names below and never
hardcode commands — so swapping the stack means editing this one file.

## Build & language

Plain HTML/CSS/JS static site. No build tool, no bundler, no framework — the site is exactly
the files served. Source lives at the **repository root** (not under a `site/` subfolder,
unlike Mugo Works): GitHub Pages for this repo is already configured to serve branch `master`,
path `/` (`gh api repos/ugochukwu/photospots-landing-page/pages`), with the custom domain
`www.photospots.net` already verified and certificated. Keeping the existing path avoids any
Pages/DNS reconfiguration to replace the site's content.

- `index.html` (and one `.html` file, or `<page>/index.html` directory, per additional page —
  see `privacypolicy/index.html`, kept as a directory so the pre-existing `/privacypolicy` URL
  keeps resolving)
- `css/` — stylesheets (`tokens.css` for design tokens, `style.css` for layout/components),
  linked with plain `<link>` tags
- `assets/` — images (app icon, screenshots, favicon), no `js/` yet — add one only if a page
  grows real interactive logic
- `.nojekyll` — **required** at the repo root. GitHub Pages' legacy build type runs Jekyll by
  default, and this kit's own docs (`docs/**/*.md`) carry `---` frontmatter that Jekyll would
  otherwise try to build into pages. `.nojekyll` disables that processing entirely so Pages
  serves every file as-is.
- `CNAME` — must keep containing `www.photospots.net` (GitHub Pages reads this file to serve
  the custom domain; deleting or changing it breaks the live domain).

The one toolchain dependency is Node, used only to run the lint step below via `npx` — pinned
as a `devDependency` in `package.json` so `npm ci` gives every agent and CI run the same
`html-validate` version. `npm run lint` also shells out to `scripts/check-placeholders`
(Python 3, no third-party dependencies) to gate publishing on unresolved brand placeholders
before `html-validate` runs. There is no `npm run build`; deployment ships the repo root as-is
once GitHub Pages picks up the push to `master`.

## Dev self-verify

The cheapest real checks a dev-implementer runs before handing off. One command per line,
cheapest first.

- lint: `npm run lint` — runs `scripts/check-placeholders` (fails if any tracked `*.html`
  still carries an unresolved brand placeholder: the literal `[CONTACT EMAIL]`, or a bare
  `href="#"` call-to-action) and then `html-validate` over every tracked `*.html` file
- render: serve the site locally (see **Run the app** below) and load the changed page(s) in a
  browser — for a static site this *is* the test; there is no headless test runner yet.

## Quality gate (the CI mirror)

`.github/workflows/ci.yml` runs on every push and pull request. QA reproduces the same commands
locally before trusting the check, per the kit's usual practice:

- docs index: `python3 scripts/gen-doc-index --check`
- html lint: `npm ci && npm run lint`

### Fallbacks

- `npx` needs network access to fetch `html-validate` on a first run in a clean environment;
  `npm ci` (run first, per the gate above) avoids that by installing from the committed
  lockfile instead. If npm/network is genuinely unavailable, fall back to `tidy -q -e *.html`
  (present on macOS by default) and say explicitly in the report that the stricter
  `html-validate` gate was skipped.

## Run the app

`python3 -m http.server 8000` from the repo root, then open `http://localhost:8000`.

## UI render check

- Trigger paths: `*.html`, `css/**`, `assets/**`
- Harness: start the local server above, then use the browser preview tool
  (`preview_start`/`navigate`/`computer` screenshot) to load the changed page(s) at both a
  mobile width (375px) and a desktop width (1280px) — this is a marketing landing page, so
  both breakpoints matter. Take a screenshot of each changed page at each width as evidence.
- No JS unit tests exist yet; if a page grows real interactive logic (a form handler, a nav
  toggle with state), add a test harness and record it here in the same change.

## Generated artifacts

- **Docs index** — the generated list in `docs/README.md` is built from each doc's frontmatter.
  Regenerate with `scripts/gen-doc-index` after adding or renaming a doc under `docs/`.
