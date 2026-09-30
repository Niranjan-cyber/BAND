# Runbook — dark-factory-pocketful

Every command anyone (human or agent) runs more than once lives here or in a script. Check this file
before running an infra command from memory.

## Environments
| Env | Public URL | API URL | Cloud account / profile / region |
|---|---|---|---|
| Production | https://we-are-dev-xband.vercel.app | same origin — `/health` | Vercel project `we-are-dev-xband` (`prj_P68DhuHgTYNVASf0gugrxskcHHzA`), team `niranjan-cybers-projects` (`team_Ght27pzXQ8zjMO4zVEthPeyk`), region: default |

## Band Desktop + harness — one-time setup
Source: `docs/participant-guide.md` in the **official** kickoff repo, read directly 2026-09-29
(github.com/band-ai/dark-factory-wearedevs) — not third-party notes. Two separate things, don't
conflate them:

1. **The harness** (Python/Docker/Playwright — runs the stage checks). The guide explicitly says
   "On Windows, run these steps inside WSL2." **Proven working end to end, 2026-09-29:**
   ```sh
   # Inside WSL2 Ubuntu (wsl -d Ubuntu):
   sudo apt-get install -y python3.14-venv   # not preinstalled on fresh Ubuntu — hit this for real
   cd ~ && git clone https://github.com/band-ai/dark-factory-wearedevs
   cd dark-factory-wearedevs
   python3 -m venv .venv && . .venv/bin/activate
   python -m pip install -r harness/requirements.txt
   python -m playwright install --with-deps chromium
   python -m harness --help        # confirmed: shows `run` and `check` subcommands
   ```
   That repo also has the actual Pocketful/Tablekeeper specs (`pocketful/spec/stage-1.md` etc.)
   and test suites — it's already cloned to `~/dark-factory-wearedevs` in WSL2 Ubuntu.

   **Docker Desktop's WSL integration gotcha (hit for real):** `docker` wasn't found in Ubuntu
   even after enabling the toggle in Settings → Resources → WSL Integration, because Ubuntu was
   reinstalled *after* Docker Desktop had already started — it never picked up the new distro.
   Fix: Settings → Resources → WSL Integration → **Refetch distros**, then fully quit Docker
   Desktop from its system-tray icon (not just close the window) and reopen it.

   Per the guide's convention, also set up (already done in WSL2 Ubuntu, `~/band-work/`):
   ```sh
   mkdir -p ~/band-work/result/stage-1 ~/band-work/checks
   git -C ~/band-work/result init -b main
   git -C ~/band-work/result config user.name "Your Name"
   git -C ~/band-work/result config user.email you@example.test
   ```
   `~/band-work/result` is the actual submission repo (starts empty on purpose — the graded
   language/framework isn't chosen by the event). Give agent seats its **absolute path**, not a
   relative one.

2. **Band Desktop itself** (creates the ≥3 coding-agent "seats" and the room — this is where the
   actual autonomy/collaboration the rubric grades happens). **Resolved 2026-09-29:** band.ai's
   own download page (band.ai/download) explicitly lists "macOS, Windows & Linux" support — runs
   **natively on Windows, no WSL2 needed for the app itself**. (The `github.com/band-app/band`
   GitHub Releases I checked earlier only had macOS artifacts — wrong/incomplete channel; the
   real Windows/Linux builds are served through band.ai's own site with OS auto-detection on the
   Download button, not that repo.) Just install it directly on Windows: band.ai/download → click
   Download → run the installer → sign in (free account, per the hacker guide).

## Band Desktop room status (as of 2026-09-30, ~00:20)
**Done:**
- Team "Feature crew" created in Band Desktop (5 seats: Planner, Implementer, Test author,
  Reviewer, Integrator — handles `niranjaniyerofi/<role>`), all switched from the Codex default to
  Claude Code.
- **Claude Code runtime bug + fix, hit for real:** switching a seat's runtime to Claude Code fails
  with `'C:\Users\Niranjan' is not recognized as an internal or external command` — Band's launcher
  doesn't quote the Command path, and the Windows username has a space ("Niranjan Iyer"). Fix: in
  Agent setup → Runtime → Launch details → Command, replace `claude` with the short (8.3, no-space)
  path: `C:\Users\NIRANJ~1\AppData\Roaming\npm\claude.cmd` (get it via
  `(New-Object -ComObject Scripting.FileSystemObject).GetFile("<full path>").ShortPath` in
  PowerShell if the npm install location ever changes). Then "Test runtime" goes green. Do this
  per-seat — no bulk/team-level way to set it found in the UI.
- All 5 seats confirmed responsive with a real bidirectional `@handle` exchange in the "Feature
  crew" room (Planner↔Implementer, then Reviewer/Integrator/Test author each replied) — this is
  Gate 2 ("room log shows messages exchanged between at least two of your own seats... with a reply
  in each direction") genuinely satisfied, not just configured.
- Mandate files written (verbatim from each seat's actual Band "Role" tab content — that tab is
  literally "sent to this agent's model as part of its instructions," so the mandate must match it,
  not paraphrase it) and committed in `~/band-work/result/mandates/{planner,implementer,test-author,
  reviewer,integrator}.md`, each starting `Harness: Claude Code` / `Model: claude-sonnet-5`.
  **The Model line is a best guess** (matches this environment) — not independently confirmed as
  what each seat actually resolves to at runtime; verify against the real room transcript/room.json
  before final submission.

**Done (2026-09-30):**
- `CREDITS.md` added and committed to `~/band-work/result` (the real submission repo, dark-factory-pocketful),
  disclosing Claude Code's role in scaffolding + writing the 5 mandate files, and stating that
  `stage-1/`–`stage-4/` app code comes only from the Band room collaboration. **Committed locally, not yet
  pushed** — push when you're ready to make it public.

**Not yet done — do this before dispatching stage-1:**
1. **Fix each seat's working directory.** Currently blank/default ("managed workspace" — Band
   creates a sandboxed copy). The guide warns: *"a seat works in its own sandbox, may not be able to
   resolve `../band-work`, and will otherwise create a repository only it can see."* Since
   `~/band-work/result` lives in WSL2 and the seats run as Windows-native Claude Code, point each
   seat's working directory at the Windows-visible UNC path:
   `\\wsl.localhost\Ubuntu\home\niranjan_iyer\band-work\result`
   (Agents → each seat → Runtime tab → Edit → Working directory field.) Not yet verified that Band's
   Windows-native process can actually read/write through this UNC path — test it once on one seat
   before doing all 5.
2. **Dispatch stage-1**, one message to Planner (send it yourself in the room — I can't click inside
   Band Desktop), referencing the spec at its Windows-visible path:
   `\\wsl.localhost\Ubuntu\home\niranjan_iyer\dark-factory-wearedevs\pocketful\spec\stage-1.md`
   Keep the dispatch minimal — don't hand it a pre-baked architecture; over-specifying undercuts the
   Factory criterion, which grades the factory's *own* planning.
3. **From the moment that's sent: hands-off.** No further messages into the room, no fixing seat
   output by hand (disqualifier #1), no steering. Verify only via the harness
   (`python -m harness check` / `run` from `~/dark-factory-wearedevs`), which doesn't touch the room.

## Local setup
```bash
# Backend (from repo root)
python -m venv .venv && source .venv/bin/activate   # WSL2/Linux; on native Windows use .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# Frontend: static hello-world checked into frontend/dist/ — no build step yet.
# Once you swap in a real frontend kit (frontend/README.md), add its dev/build commands here.

# Full stack locally, same way Vercel serves it:
npm install --global vercel@latest
vercel dev
```

## Deploy
**Primary path: Vercel's GitHub integration, not CLI tokens.** Claude Code's Vercel login is
scoped and can't run `vercel tokens add` (confirmed 2026-09-29 — fails with "Cannot create
tokens for this app"). Rather than fight that, deploys go through Vercel's own GitHub integration
(push-to-deploy), and CI waits for that deployment via GitHub's Deployments API
(`vercel/wait-for-deployment-action` — no Vercel token needed in CI at all).

**One-time dashboard setup** (only you can do this — needs your Vercel account):
1. vercel.com/new → Import Git Repository → pick this GitHub repo.
2. Framework preset: Vercel should auto-detect the FastAPI zero-config setup from
   `pyproject.toml`'s `[tool.vercel] entrypoint`. If it asks, Root Directory is `.`.
3. Production Branch: `main`.
4. Deploy once from the dashboard to confirm it builds, then every push to `main` auto-deploys.

`vercel link` (already run once in this repo) recorded the project locally in `.vercel/repo.json`
(note: newer Vercel CLI versions use `repo.json`, not the older `project.json` — don't go looking
for the latter):
```bash
cat .vercel/repo.json   # orgId + projectId, useful if you ever do get a CLI token
```

Manual/emergency deploy, only if both CI and the Git integration are down, and only if you've
created a personal token yourself at vercel.com/account/tokens (Claude Code's login can't):
```bash
vercel pull --yes --environment=production --token=$VERCEL_TOKEN
vercel build --prod --token=$VERCEL_TOKEN
vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN
```

## Verify
```bash
# Smoke test against the public URL CI just deployed:
PUBLIC_URL=https://<your-deployment-url> npx playwright test tests/smoke

# Logs (works under the current CLI login even though `vercel tokens add` doesn't):
vercel logs we-are-dev-xband.vercel.app --json
# Dashboard: project -> Deployments -> select deployment -> Functions tab (backend/main.py)
```

## Rollback
```bash
# Vercel dashboard -> Deployments -> pick the last green one -> "Promote to Production"
# or, non-interactively:
vercel rollback <deployment-url-or-id> --token=$VERCEL_TOKEN
```

## Known gotchas
| Symptom | Cause | Fix |
|---|---|---|
| **[hit for real, 2026-09-29]** `FUNCTION_INVOCATION_FAILED`, 500 on every route; `vercel logs` shows `RuntimeError: Frontend directory 'frontend/public' does not exist` | Vercel's build-time static-promotion scan for `app.frontend()`/`app.mount()` did not bundle `frontend/public/` with a custom `[tool.vercel] entrypoint` (only confirmed to work for the docs' default `app.py` at repo root) | `backend/main.py` now inlines the hello-world HTML as a Python string instead of serving from disk — sidesteps the promotion scan entirely. When a real frontend build lands, use Vercel's standard static Build Command + Output Directory pipeline, not `app.frontend()`, and prove it with a real deploy before trusting it |
| **[hit for real, 2026-09-29]** Production URL 302-redirects to `vercel.com/sso-api` (login wall) | Vercel's default "Standard Protection" protects every *generated per-deployment URL* (the one with a random hash, e.g. `we-are-dev-xband-pw6ani3ie-….vercel.app`) even for production — it only exempts the clean **production domain** (`we-are-dev-xband.vercel.app`) | Always test/share the clean production domain, not the URL `wait-for-deployment-action` or a build log hands you (that's the generated one). If judges need a specific hash-suffixed preview URL, disable protection for it in Settings → Deployment Protection, or use a bypass token |
| `vercel tokens add` fails: "Cannot create tokens for this app" | Claude Code's Vercel login uses a scoped OAuth grant that can't mint personal tokens | Don't fight it — use the Git integration (this repo's current setup) instead of CLI-token deploys. Only a token created by you at vercel.com/account/tokens works for manual CLI deploys |
| **[hit for real, 2026-09-29]** `wait-for-deployment-action` hangs until its 600s timeout, never finds the deployment | This GitHub repo has **two Vercel projects** linked to it (`band` and `we-are-dev-xband` — confirmed via `vercel projects ls`, a leftover from setup, not intentional). With 2 projects on one repo, GitHub's environment name becomes `Production – we-are-dev-xband` (suffixed) instead of plain `Production`, which the action can't find without help | `.github/workflows/ci-deploy.yml` now passes `project-slug: we-are-dev-xband` to disambiguate. **You should also clean up the `band` project in the Vercel dashboard** (delete it or disconnect it from this GitHub repo) — it's an unused duplicate auto-deploying alongside the real one for no reason |
| This kit's usual "frontend reads API base URL from a pipeline env var" rule doesn't apply here | Deliberate deviation: FastAPI serves frontend+backend from one Vercel project, same origin, so `fetch('/health')` needs no base URL | If Pocketful later needs a separate frontend host (e.g. a heavier framework deploy elsewhere), reintroduce `VITE_API_BASE_URL` from pipeline outputs and update `.env.example` |
| BAND Desktop GUI doesn't appear in WSL2 | WSLg not enabled, or WSL version too old | `wsl --update`, confirm `wsl --version` shows WSLg; restart WSL (`wsl --shutdown`) |
