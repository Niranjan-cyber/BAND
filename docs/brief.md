# Event brief: WeAreDevelopers x BAND — Dark Factory / Pocketful

(Fuller template: build-hackathon skill, assets/event-brief-template.md.)

Source of truth: the official kickoff repo **github.com/band-ai/dark-factory-wearedevs**,
specifically `docs/participant-guide.md` ("This guide is the authoritative rules and
instructions for participants"). Everything below with no caveat is quoted or paraphrased
from that guide, read directly on 2026-09-29 — not from third-party participant notes.

## Event signature
| Field | Value |
|---|---|
| Working hours available | Build window Sep 26 – Oct 5, 2026 (~6 days left as of Sep 29) |
| Team size and strengths | Solo (confirmed eligible) |
| Mandated tech / services / region | **Band Desktop required** for seat/room creation. Python 3.12+, Git, a running Docker daemon, your own model-provider access, for the harness. **Any implementation language for the submitted service itself** (Python/TS/Go/Rust/Java all judged the same way, over HTTP against your `Dockerfile`) |
| Judging criteria (with weights) | **Confirmed, exact:** Factory 50% (generic — another team could point your mandates at a different problem; effective — how far through the 4 stages with spec-compliant code; reusable — `FACTORY.md` + `mandates/` are enough to stand it up) / App 25% (coherent, presentation-ready, responsive, clear UI) / Agent Teamwork 25% (seats really shared the work; autonomy — the task you dispatch per stage is the only human input) |
| Deliverables | Public GitHub repo containing: `README.md`, `FACTORY.md`, `mandates/` (≥3 seat files, each starting `Harness: [name]` / `Model: [exact model id]`), `room.json` (full room download from Band), `stage-1/`…`stage-4/` (Dockerfile + RUN.md + source each). Plus a presentation and a video showing factory operation |
| Compliance items → owner | 3+ distinct seat identities with named mandates → you. Mandates stay 100% generic (no endpoint paths/field names/error codes) → you. Room log shows real `@handle` exchanges both directions between ≥2 seats → you. `stage-1/` builds from a clean container via its `RUN.md` → you. Code built to spec, not to the visible tests (only part of each stage's checks ship; rest are held back) → you |
| Deadline (and buffer) | **Mon Oct 5, 23:59 PDT** — confirmed (this is the same instant as "Oct 6, 1:59 AM CDT" from an earlier unofficial source; PDT=UTC-7, CDT=UTC-5, both check out) |

## Hard disqualifiers (verbatim from the guide)
1. "A stage counts only if the code that passes its tests came out of a collaboration in your Band Desktop room" — no hand-written/hand-fixed code.
2. "Code written to the tests disqualifies the entry... Build to the specification, not the tests." You only get part of each stage's checks.
3. "A mandate that names track-specific detail disqualifies the entry" — no endpoint paths, field names, or error codes in `mandates/`.

## Track: Pocketful
"A wallet and payments app, a Venmo" — hard because "money must never be created, destroyed
or spent twice, under concurrent transfers, retries and rounding."

| Stage | What you build | Graded by |
|---|---|---|
| 1 | JSON API: idempotent writes, atomic multi-item ops, state export/import | API conformance |
| 2 | Browser UI, richer resource model, recovery from stale state/lost responses | API + Playwright, plus stage 1 |
| 3 | State over time: point-in-time rules/corrections, past records stay truthful | API conformance, upgrades, concurrent writes, plus 1+2 |
| 4 | Atomic bulk changes to existing records without breaking history | Own suite + populated-state upgrades, plus 1-3 |

**All four stages' exact specs are already in the kickoff repo** —
`pocketful/spec/stage-1.md` through `stage-4.md`, plus the real test suites in
`pocketful/test/`. This is the actual field-name/status-code/data-testid source of truth;
no more guessing needed on that front. Shipped test coverage is partial by design (stage 1
~79-83%, stage 4 ~16-21% of the full suite) — the held-back tests are what "build to spec,
not to the tests" is checking.

## One-pager
- Pitch (one sentence): *(fill in once you scope the Pocketful build)*
- Persona:
- Problem:
- Wow moment:

## Cut list (explicitly not building)
- Real frontend framework (shipping static hello-world first; swap later)
- A real datastore (not chosen yet — see AGENTS.md stack table)

## Riskiest dependency: proven from the deployed environment?
| Dependency | Proven? | Time | Notes |
|---|---|---|---|
| Band Desktop seat/room creation on Windows | **Genuinely unclear — needs a human answer** | — | The guide's harness setup says "On Windows, run these steps inside WSL2," but that instruction is scoped to the Python/Docker/Playwright *harness* only. Separately, the Docker Sandbox section lists "Windows 11" as a supported *host* for "Band Desktop 0.4.10 or newer," implying a native Windows GUI build exists — but the only public releases I could find (github.com/band-app/band) ship macOS-only `.dmg`/`.zip` artifacts, no Windows installer. Ask in the **BAND Discord** (https://discord.com/invite/5YkNXmYfjk) — the guide names it as the formal channel for exactly this |
| Harness setup itself (Python venv, Docker, Playwright) under WSL2 | Not yet run | — | Fully specified now, not blocked on the Windows-GUI question — see RUNBOOK.md, can do this immediately |
| Vercel FastAPI zero-config deploy | **Proven 2026-09-29** | ~3 iterations, ~30 min | Live at https://we-are-dev-xband.vercel.app, CI green. Hit and fixed: static-promotion crash (now inlines HTML), SSO wall on generated URLs (use the production domain), duplicate-project ambiguity (added `project-slug`) — see RUNBOOK.md |
