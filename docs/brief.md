# Event brief: WeAreDevelopers x BAND — Dark Factory / Pocketful

(Fuller template: build-hackathon skill, assets/event-brief-template.md.)

## Event signature
| Field | Value |
|---|---|
| Working hours available | Build window Sep 26 – Oct 5, 2026 (started; ~6 days left as of Sep 29). Submission deadline **Oct 6, 2026 ~1:59 AM CDT — single unofficial source, CONFIRM on your lablab.ai submission dashboard/kickoff email before trusting this** |
| Team size and strengths | Solo (confirmed eligible; no phone verification needed) |
| Mandated tech / services / region | **BAND Desktop required** (macOS/Linux only — running via WSL2, see RUNBOOK.md). SDK adapters available: Claude Code, Codex, LangGraph, CrewAI, Pydantic AI, Agno, Anthropic, Gemini |
| Judging criteria (with weights) | **Unverified, single source:** Factory 50% (generic/reusable design, spec-compliant stages, `FACTORY.md`) / App 25% (coherent UI, maintainable code) / Agent Teamwork 25% (genuine seat collaboration, autonomy after initial dispatch). **Confirmed independently:** grading is literal and automated — exact field names, exact status codes, exact `data-testid` values; a cosmetically-correct-but-mistyped attribute scores zero |
| Deliverables | Project title + short/long description, cover image, video presentation, slide deck, public GitHub repo, hosted demo with public URL. **Unverified but repeated in one source:** video MUST include a recording of the BAND Desktop room, or the team is disqualified |
| Compliance items → owner | Video includes BAND room recording → you. Seat mandates stay generic/domain-agnostic (no track-specific language) → you. `FACTORY.md` + seat-mandate docs + factory description + BAND room export → you. Confirm exact deadline + rubric weights on official dashboard → you, before final push |
| Deadline (and buffer) | Treat Oct 5 (build window close) as the real deadline; Oct 6 1:59 AM CDT is unverified — don't rely on the extra hours |

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
| BAND Desktop under WSL2 | Not proven | — | Never run in this session; do this before anything else per compressed-mode rules |
| Vercel FastAPI zero-config deploy | Not proven | — | Files written, no live deploy observed yet — do the dry run |
| Exact grading harness (field names / status codes / `data-testid`) | Unknown | — | Only available from the official per-track spec at kickoff, not on the public page — find it in your enrollment materials/Discord before building Pocketful's real endpoints |
