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
   "On Windows, run these steps inside WSL2." Confirmed commands, verbatim from the guide:
   ```sh
   # Inside WSL2 (wsl --install -d Ubuntu if you don't have a distro yet; already installed here)
   python3 --version                # use any Python 3.12+ interpreter
   docker --version                 # the daemon must be running
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install -r harness/requirements.txt
   python -m playwright install --with-deps chromium   # --with-deps needed on Linux
   python -m harness --help
   ```
   Run these from the `dark-factory-wearedevs/` directory after cloning
   `github.com/band-ai/dark-factory-wearedevs` — that repo also has the actual Pocketful/Tablekeeper
   specs (`pocketful/spec/stage-1.md` etc.) and test suites, so clone it regardless.

2. **Band Desktop itself** (creates the ≥3 coding-agent "seats" and the room — this is where the
   actual autonomy/collaboration the rubric grades happens). **Genuinely unresolved as of
   2026-09-29:** the guide's Docker Sandbox section lists "Windows 11" as a supported host for
   "Band Desktop 0.4.10 or newer" (implying a native Windows GUI build), but the only public
   releases I found (github.com/band-app/band, checked v0.38.0/v0.37.0/v0.35.0/nightly) ship only
   macOS `.dmg`/`.zip` — no Windows installer, no Linux build either (so it can't just run in
   WSL2 as a Linux app). **Ask in the BAND Discord before assuming either way** —
   https://discord.com/invite/5YkNXmYfjk, named in the guide as "the formal channel for Band
   Desktop, seat, permission and harness questions." Don't build the actual Pocketful factory
   until this is resolved; the harness setup above doesn't depend on the answer, so do that now.

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
