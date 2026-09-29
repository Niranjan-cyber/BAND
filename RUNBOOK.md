# Runbook — dark-factory-pocketful

Every command anyone (human or agent) runs more than once lives here or in a script. Check this file
before running an infra command from memory.

## Environments
| Env | Public URL | API URL | Cloud account / profile / region |
|---|---|---|---|
| Production | (filled after first `vercel deploy`, and by CI in `RUNBOOK` updates) | same origin as public URL — `/health` | Vercel project `dark-factory-pocketful`, region: default (check latency once BAND agent calls are added) |

## BAND Desktop (WSL2) — one-time setup
BAND Desktop does not support Windows natively (macOS/Linux only, per participant notes — confirm current
support on band's own docs before relying on this). Run it inside WSL2:

```bash
# In an elevated PowerShell, if WSL2 isn't installed yet:
wsl --install -d Ubuntu

# Inside the WSL2 Ubuntu shell:
curl -fsSL <band-install-url-from-their-docs> | sh   # replace with the real installer command from band's docs
band --version                                        # confirms the CLI is on PATH
band login                                             # free account, no card required per participant notes
```

**Not yet verified in this session** (no BAND account here): the exact install command, whether BAND
Desktop's GUI needs an X server / WSLg (Windows 11 ships WSLg by default, so a GUI app should show up
without extra config — confirm on first run), and whether the coding-agent plugin needs a separate install
step. Fill this section in for real the first time you do it and keep the exact commands.

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

# Logs: Vercel dashboard -> project -> Deployments -> select deployment -> Functions tab (backend/main.py)
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
| Frontend served but `/health` 404s | FastAPI route declared after `app.frontend()`, or wrong entrypoint path in `pyproject.toml` | API routes always win over frontend regardless of order per Vercel's docs — if this still 404s, check `[tool.vercel] entrypoint` matches the real module path |
| `vercel build` can't find the frontend | `frontend/dist/` is gitignored (build-output convention) but the hello-world page has no build step | Hello-world lives in `frontend/public/` (source-controlled) instead, per `backend/main.py`'s `app.frontend()` call. Once a real bundler is added, switch that call to `frontend/dist/` and add `npm run build` to CI before `vercel build` |
| This kit's usual "frontend reads API base URL from a pipeline env var" rule doesn't apply here | Deliberate deviation: FastAPI serves frontend+backend from one Vercel project, same origin, so `fetch('/health')` needs no base URL | If Pocketful later needs a separate frontend host (e.g. a heavier framework deploy elsewhere), reintroduce `VITE_API_BASE_URL` from pipeline outputs and update `.env.example` |
| BAND Desktop GUI doesn't appear in WSL2 | WSLg not enabled, or WSL version too old | `wsl --update`, confirm `wsl --version` shows WSLg; restart WSL (`wsl --shutdown`) |
| Preview deploy smoke test fails with 401 | Vercel preview deployment protection (auth wall) | Deploy `--prod` (as this pipeline does) or add a protection bypass token |
