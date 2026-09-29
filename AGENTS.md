# AGENTS.md (mirror to CLAUDE.md if your tooling reads that name)

How humans and coding agents work in this repo. Keep it under ~80 lines: agents load it every session.

## Golden rules
1. **There is always a working, deployed demo.** A change that breaks the golden path on the public URL gets
   reverted or fixed before anything else merges.
2. **The public URL is the only surface that counts.** Verify on it, not on localhost.
3. **RUNBOOK.md first.** Before running or suggesting any infra/deploy command, read `RUNBOOK.md`. Never run a
   deploy command from memory. Any command used twice goes into `RUNBOOK.md` or a script.
4. **No manual deploys.** Push to main; the pipeline tests, deploys and smoke-tests.
5. **No silent fallbacks in deployed code.** No catch-all exception handlers that return empty data, no default demo
   data on error. Failures must be visible.
6. **Never hand-write evidence.** Quotes, metrics and "verified" flags shown as real must come from real runs.
   Label sample data (`data-mode="sample"`).
7. **One slice at a time**, UI to storage. Read the slice card. Don't add breadth.
8. **Log as you go** in `LEARNING.md` (one line per decision or surprise).

## Stack (fill in once, then keep stable)
| Layer | Choice | Notes |
|---|---|---|
| Frontend | Static HTML/CSS/vanilla JS (`frontend/dist/`) | Hello-world only. Swap for a real framework before build-hackathon phase 2; keep it served by `app.frontend()` (same-origin) unless a split deploy is needed |
| Backend | FastAPI (Python), Vercel Python runtime, zero-config via `pyproject.toml` `[tool.vercel] entrypoint` | Single Vercel Function — see `backend/main.py` |
| Data | Not chosen yet | Pocketful (wallet/payments, double-entry) will need a real datastore — pick one before phase 2 and add its deploy/migration step to this runbook |
| LLM | via `llm-adapter` (provider/model in config) | `LLM_PROVIDER=echo` by default; BAND's own agent runtime is separate from this adapter — this is for any in-app model calls the product itself makes |
| Cloud + region | Vercel, region: default | Confirm latency once BAND agent calls or a database are added |
| CI | GitHub Actions: `.github/workflows/ci-deploy.yml` | Push → Vercel's GitHub integration auto-deploys → CI waits via GitHub Deployments API (`vercel/wait-for-deployment-action`) → Playwright smoke test. No `VERCEL_TOKEN` — Claude Code's Vercel login can't create one |
| Agent runtime | BAND Desktop, via WSL2 (Windows host doesn't support it natively) | See `RUNBOOK.md` "BAND Desktop (WSL2)" — **not yet verified end-to-end in this session** |

## Commands
See `RUNBOOK.md`. Common ones: `uvicorn backend.main:app --reload`, `vercel dev`, `pytest`, `npx playwright test tests/smoke` (against `PUBLIC_URL`).

## Skills and tools that are verified to load
| Need | Skill / tool | Verified on | Notes |
|---|---|---|---|
| Deploy (cloud) | Vercel GitHub integration + `wait-for-deployment-action` | **not yet run for real** | Switched from CLI tokens after confirming Claude Code's Vercel login can't create them (2026-09-29). Dashboard import step still needs doing — see RUNBOOK.md |
| Frontend design | `dataviz` / `artifact-design` skills (for later polish) | not yet used | |
| Browser testing | Playwright (`tests/smoke/golden-path.spec.ts`) | **not yet run** | No Playwright install observed in this session |
| Docs / diagrams | — | | |
| Demo video / submission | hackathon-demo-submission | | Use once there's a real golden path to script |
| Event process | build-hackathon | | Hand off here after the dry run passes |

Skills live in ONE folder (`<skills folder>`). Do not copy them elsewhere and exclude that folder from repo-wide
search and indexing of product code.

## Definition of done for a slice
Works on the public URL from a fresh browser; smoke test asserts `data-mode="live"`; error and empty states handled;
logs show it working; commands in the runbook; `LEARNING.md` updated.

## Do not
- Commit secrets or `.env`.
- Add dependencies or new technologies without the decider's OK (one new technology per event).
- Refactor during the freeze.
