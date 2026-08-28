---
title: Forge adapter
summary: GitHub via the gh CLI — configuration, the forge verb interface, and GitHub-specific conduct rules.
updated: 2026-08-28
status: living
---

# Forge adapter — GitHub via `gh`

All PR actions go through [`scripts/forge`](../../scripts/forge) (run `scripts/forge help`).
Core kit files invoke those verbs and never call the GitHub API directly. This is the GitHub
implementation of the agent kit's forge interface, backed by the `gh` CLI — the same
implementation used by the Fotospots and Mugo Works projects, unmodified.

## Configuration

- Repo: `ugochukwu/photospots-landing-page` (public), inferred from the git remote
  (`FORGE_REPO=<owner>/<repo>` overrides).
- Reviewer: `ugochukwu` (Michel), requested on every PR `pr-create` opens regardless of the
  auto-merge/human-review path (`FORGE_REVIEWER=<login>` overrides).
- Auth: `gh auth login` on this machine (no token file) for **read verbs** (`prs`, `comments`,
  `status`). `gh auth status` must succeed.
- **This repo is public**, unlike Fotospots and Mugo Works (both private). GitHub's native
  auto-merge and required-status branch protection are available on the free plan here, so
  `forge automerge` and the `allows-auto-merge` label path are expected to actually work once
  branch protection is turned on (see the drop-in checklist in `MANIFEST.md`) — this is the
  first project in the family where the auto-merge path is not purely aspirational.

### Bot identity for write verbs

Every **write** verb (`reply`, `comment`, `pr-create`, `pr-edit`, `label`, `unlabel`,
`automerge`, `seed-labels`) invokes `gh` with `GH_TOKEN` set to a distinct bot PAT, sourced from
macOS Keychain (service `mugo-bot`, account `$USER`) inside a `get_bot_token()` helper — the
same `mugo-bot` collaborator identity already used on Fotospots and Mugo Works, reused here
rather than minted fresh. Design intent: agent-authored writes appear as `mugo-bot` in GitHub's
UI, never as the machine's default `gh` identity (Michel's personal PAT), so a reviewer can tell
an agent's comment/PR/label from a human's at a glance. **Read** verbs (`prs`, `comments`,
`status`) keep the default `gh auth` session. This touches only the GitHub API identity; git
commit authorship (`user.name`/`user.email`) is unrelated and untouched.

**Outstanding, not yet done:** `mugo-bot` is not yet a collaborator on
`ugochukwu/photospots-landing-page` (checked via `gh api repos/ugochukwu/photospots-landing-page
/collaborators` on 2026-08-28 — only `ugochukwu` is listed). Every write verb will fail with a
permissions error until Michel adds `mugo-bot` as a collaborator with write access on this repo
specifically (a GitHub PAT's access is per-repo for fine-grained tokens, or governed by org/repo
membership for classic tokens).

Retrieval: `security find-generic-password -s mugo-bot -a "$USER" -w`. If the entry is missing
or `security` fails, `forge` exits non-zero with an error naming the exact fix command (no
silent fallback to default auth):

```
forge: mugo-bot token not found in Keychain (service=mugo-bot, account=<user>). Fix: security add-generic-password -s mugo-bot -a "<user>" -w '<TOKEN>' -U
```

## Verbs

`pr-create` · `pr-edit` · `prs` · `status` · `comments` · `reply` · `comment` · `label` ·
`unlabel` · `automerge` · `seed-labels` (· `upload` — unsupported, see quirks)

Differences from the Forgejo original, on purpose:

- **`reply <pr> <comment-id> <body>`** — GitHub threads replies by review-comment id, not by
  review-id/path/position. `forge comments` emits the `comment_id` to use.
- **`automerge <pr>`** — replaces the Forgejo label-triggered workflow: it enables GitHub's
  native auto-merge (squash), and GitHub performs the merge once required checks pass. The
  `auto-merge` label is applied alongside purely as a visible marker. Needs branch protection
  with a required status check turned on first (see MANIFEST.md's drop-in checklist) — until
  then `forge automerge` fails cleanly and the PR waits for a human.
- **No deny-list backstop yet** — GitHub's native auto-merge has no equivalent hook. Treat
  `.github/**`, `.claude/**`, `CLAUDE.md`, `AGENTS.md`, and `docs/adapters/**` as never-auto-merge
  by policy: QA routes beads touching them to human review regardless of labels.
- **`pr-create <head> <base> <title> <body>` gates on `pr-body-embeds-comparison-shots`**: it
  derives the bead id from `head` (`bd/photospots-landing-page-<id>` or
  `bd/dev/photospots-landing-page-<id>`, read from `bd config get issue_prefix` rather than
  hardcoded) and checks `git ls-files` for that bead's
  `docs/qa-screenshots/<bead-id>/` on the current tree. If any image file is there, the resolved
  body must embed at least one inline (`![alt](url.png)` or `<img src="...">`) — a plain path
  reference does not count.
- **`pr-create` always requests a reviewer**: every PR is opened with `--reviewer "$FORGE_REVIEWER"`
  (default `ugochukwu`), so a human review is on record regardless of the merge path.

## Host quirks (GitHub)

- **Rendering**: newlines in PR/issue bodies render as line breaks. Never hard-wrap bodies —
  one unbroken line per paragraph or bullet, blank line between blocks.
- **Bodies with backticks or `$(...)`** go through `@<file>` or stdin `-`, never inline.
- **Review comments anchor to commit SHAs**: bring branches current by **merging** `main` in,
  never rebase + force-push — a force-push detaches review threads.
- **No image upload API for PR bodies**: screenshots are committed on the bead branch under
  `docs/qa-screenshots/<bead-id>/` and linked by path; reviewers open them in the Files tab.
- **Squash merges**: GitHub's squash leaves the branch "unmerged" in git's eyes — delete bead
  branches with `git branch -D` after the merge is confirmed.
- Authorship marking is the `mugo-bot` identity itself; comment bodies carry no prefix.
- **GitHub Pages, not Netlify**: unlike Mugo Works, this repo deploys via GitHub Pages
  (`gh api repos/ugochukwu/photospots-landing-page/pages`: branch `master`, path `/`, custom
  domain `www.photospots.net`). There is no deploy-preview-per-PR the way Netlify gives Mugo
  Works; the render check runs against a local server instead (see the stack adapter).
