---
name: website-change
description: Guides a non-technical team member through changing the aimtravel.bg website end to end - new branch from main, the change itself, commit + push with a generated message, a pull request, and the merge that deploys to production. Use when someone asks to change, fix or add something on the website (texts, pages, images, prices, styles - "промени на сайта", "смени текста", "добави снимка"), or to continue such a change ("продължи", "провери PR-а", "merge").
---

# Website change (for non-technical team members)

The person running this skill is usually **not a developer**. Talk to them in the
language they write in (normally Bulgarian), in plain words, one step at a time.
Never show raw git output without explaining it. Run every git command yourself;
the person only clicks on GitHub pages you link to.

Fixed facts:

- Repository: `aimtravel/aimtravel_site_repo` (public), remote `origin` over SSH.
- No reviewer is requested. Stoyan Stoyanov is the person to ask for help.
- **Merging into `main` deploys to https://aimtravel.bg immediately.** There is no staging.
- `main` is protected: PR only; required checks **Django check + UI smoke tests**,
  **Frontend build**, **Ruff (changed Python files)**; the branch must be up to date
  with `main`; approvals are not required. The PR may be merged as soon as the
  three checks are green.
- There is no `gh` CLI. The person opens and merges the PR in the browser. You read
  the state through the public GitHub API with `curl` (no login needed):
  `API=https://api.github.com/repos/aimtravel/aimtravel_site_repo`.
  The unauthenticated limit is 60 requests/hour, so do **not** poll in a loop: check
  once each time the person tells you something changed. If the API answers 403/404
  (rate limit, or the repo became private), ask the person to read the PR page to you.
- Follow `CLAUDE.md` (secrets, personal data, legacy folders, migrations).

## Step 0 - Where are we?

1. `git rev-parse --show-toplevel` and `git remote get-url origin` - must be this
   repository (`aimtravel/aimtravel_site_repo`). If not, stop and explain.
2. `git status --short` and `git branch --show-current`.
   - On a branch other than `main` with work already pushed, look for its PR:
     `curl -s "$API/pulls?head=aimtravel:<branch>&state=all"`.
     Open PR -> continue at **Step 5**; merged PR -> **Step 7** (clean-up), then
     ask what the new change is.
   - Uncommitted changes the person did not make in this conversation: do **not**
     discard, stash or commit them. Show the list, explain, and ask Stoyan's help if
     the person does not recognise them. (Modified `*.pyc` files only: they come from
     running Python - `git restore -- '*.pyc'` is safe.)
3. Check GitHub access: `GIT_TERMINAL_PROMPT=0 git ls-remote --exit-code origin main`.
   If it fails (Permission denied, Host key verification failed, passphrase prompt),
   stop: the person must finish the SSH part of the setup guide
   ("AIM Travel - промени по сайта с Claude", section 2). Do not try to create or
   change SSH keys or git config yourself.

## Step 1 - New branch from main

1. Ask what should change, if not already clear. Ask for the exact page (URL on
   aimtravel.bg) and the exact new text/image. Clarify before editing.
2. `git fetch origin --prune`
3. Branch name: `fix/<slug>` for corrections, `feature/<slug>` for new things;
   `<slug>` = 2-5 lowercase English words with hyphens, ASCII only
   (e.g. `fix/contacts-phone-number`). Make sure it does not exist:
   `git ls-remote --heads origin <branch>` and `git branch --list <branch>`.
4. `git switch --no-track -c <branch> origin/main`
   (works even when this session runs in a worktree where `main` cannot be checked out).

## Step 2 - Make the change

- Find where the page lives: live templates are in top-level `templates/`
  (not `aimtravel_site/templates/`), styles/images/scripts in `static/`, the
  application form in `frontend/src/`. A lot of content (news, offers, prices,
  homepage sections) is **in the database**, edited in the Django admin
  (https://aimtravel.bg/admin/), not in the code. If the requested text is not in the
  repository, say so: the change is done in the admin, no PR is needed - and stop.
- Keep the change as small as possible; UI texts are in Bulgarian.
- Never add or commit: `credentials.py`, `wat_credentials.py`, `.env`, passwords or
  keys, database dumps, documents/photos with applicants' personal data,
  `static/dist/`, `node_modules/`, `*.pyc`. Never edit legacy folders listed in
  `CLAUDE.md` (`venv/`, `staticfiles/`, `media/`, `private_media/`, ...).
- If the change needs Python model changes/migrations, a new package, a change in
  `aimtravel_site/settings.py`, `deploy/`, `.github/` or `.cpanel.yml`, explain the
  risk in plain words and recommend asking Stoyan before continuing; continue only
  if the person confirms.
- Images: ask the person for the file path, copy it into the right `static/img/...`
  folder with a lowercase ASCII file name; prefer `.webp`/`.jpg` under ~500 KB.
- If the developer setup from `README.md` exists on this computer (`credentials.py`
  and a Python 3.11 environment), you may run `python manage.py test tests`
  (expect `OK (expected failures=2)`). Otherwise say the automatic checks on GitHub
  will test it.
- Show the result: `git status --short` and `git diff --stat`, then explain in plain
  words what changed in each file (old text -> new text). **Ask for confirmation
  before committing.**

## Step 3 - Commit and push

1. Stage only the files of this change, by name: `git add <file> <file>`
   (never `git add .` / `-A`). Re-check `git status --short`: nothing from the
   forbidden list may be staged.
2. Write the commit message yourself, in English, in the style of the history:
   `<type>: <what changed>` (type `fix`, `feat`, `content`, `style`, `docs`),
   max ~70 chars, then a blank line and 1-3 lines on why / which page.
   Example: `content: update phone number on the contacts page`.
   Show it to the person (with a Bulgarian translation) and use it unless they want
   changes.
3. `git commit -m "<subject>" -m "<body>"`
4. `GIT_TERMINAL_PROMPT=0 git push -u origin <branch>`. If the push is rejected,
   explain the message; never force-push.

## Step 4 - Open the pull request (browser)

Build a link that pre-fills the PR, and also print the title and description in
the chat so they can be copied if the link fails:

```
https://github.com/aimtravel/aimtravel_site_repo/compare/main...<branch>?quick_pull=1&title=<title>&body=<body>
```

- URL-encode title and body (spaces as `+`, newline `%0A`, `@` `%40`, `#` `%23`,
  `&` `%26`, Cyrillic as UTF-8 `%XX`). Keep the body short (link under ~2000 chars).
- Title = the commit subject. Body (English):
  ```
  What: <1-2 lines>
  Why: <1 line>
  Page: <https://aimtravel.bg/...>
  Tested: <tests run locally / only the automatic checks>
  ```
- Never put personal data, passwords or keys in the link or the description.

Tell the person, step by step:
1. Open the link. Check that it says **base: main** <- **compare: <branch>**.
2. Leave **Reviewers** empty and click **Create pull request**.
3. Tell you when it is created.

## Step 5 - Check the pull request

`curl -s "$API/pulls?head=aimtravel:<branch>&state=all"` -> take `number`,
`html_url`, `head.sha`. Then:

- Checks: `curl -s "$API/commits/<head.sha>/check-runs"` -> each `name`, `status`,
  `conclusion`. The checks take a few minutes; if they are still `queued` /
  `in_progress`, ask the person to tell you when the PR page shows them finished
  (or to come back later and say "продължи").
- A check failed (`conclusion` = `failure`): read why -
  `curl -s "$API/check-runs/<id>/annotations"` and the run's `output`. Explain it
  simply, fix it on the same branch, commit (Step 3), push - the PR updates and the
  checks run again. If the cause is unclear or outside this change, ask Stoyan.
- Someone left comments on the PR (`$API/pulls/<n>/reviews`,
  `$API/pulls/<n>/comments`): read them to the person, fix on the same branch,
  commit, push.

## Step 6 - Merge (deploys to production)

Only when all three required checks have `conclusion: success` on the latest
`head.sha`:

1. `curl -s "$API/pulls/<n>"` -> `mergeable_state`:
   - `behind` (out of date with main): the person clicks **Update branch** on the
     PR page; the checks run again - go back to Step 5.
   - `dirty` (conflicts): `git fetch origin`, `git merge origin/main`, resolve the
     conflicts keeping both sides' intent, show the person what you did, commit,
     push, back to Step 5. If unsure, ask Stoyan.
2. Remind the person: merging puts the change **live on aimtravel.bg within
   minutes**. Ask: "Ready for it to go live?" Continue only on a clear yes.
3. The person clicks **Merge pull request** -> **Confirm merge**.
4. Verify: `curl -s "$API/pulls/<n>"` -> `merged` is `true`; note `merge_commit_sha`.
5. Deploy: after a few minutes,
   `curl -s "$API/actions/workflows/deploy-production.yml/runs?branch=main&per_page=5"`
   -> the run whose `head_sha` = `merge_commit_sha`. `conclusion: success` = live.
   Then ask the person to open the changed page on https://aimtravel.bg (hard refresh:
   Cmd+Shift+R / Ctrl+F5). If the run failed, give them its `html_url` and tell them
   to send it to Stoyan right away - the deploy restores the previous version by
   itself, but Stoyan must look at it.

## Step 7 - Clean up

1. The person clicks **Delete branch** on the merged PR page.
2. Locally: `git fetch origin --prune`; then `git switch main && git pull --ff-only`
   (skip the switch if `main` is checked out in another worktree) and
   `git branch -d <branch>`.
3. Summarise in 2-3 lines: what changed, the PR link, that it is live.
