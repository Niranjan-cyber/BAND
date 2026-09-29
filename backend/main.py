"""Hello-world FastAPI entrypoint. No product logic — see AGENTS.md rule 2.

Vercel resolves this via `[tool.vercel] entrypoint = "backend.main:app"` in pyproject.toml
(zero-config Python runtime: https://vercel.com/docs/frameworks/backend/fastapi).

Same-origin deployment: the frontend build in frontend/dist/ is served by this same app via
app.frontend(), so there is no separate backend URL to wire up — a deliberate deviation from
the kit's default "frontend reads API base URL from a pipeline-set env var" pattern. See
RUNBOOK.md "Known gotchas" for why, and what changes if Pocketful later needs a split deploy.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

_allowed = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed or ["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "mode": os.environ.get("APP_MODE", "live")}


# Declared before app.frontend() only matters for app.mount(); API routes above always win.
# Points at frontend/public/ (source-controlled) not frontend/dist/ (gitignored build output) —
# there's no bundler yet, this is hand-written static HTML. Switch to frontend/dist/ once a real
# frontend kit with a build step lands (frontend/README.md), and add that build step to CI.
app.frontend("/", directory="frontend/public")
