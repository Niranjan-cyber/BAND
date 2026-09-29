"""Hello-world FastAPI entrypoint. No product logic — see AGENTS.md rule 2.

Vercel resolves this via `[tool.vercel] entrypoint = "backend.main:app"` in pyproject.toml
(zero-config Python runtime: https://vercel.com/docs/frameworks/backend/fastapi).

The hello-world page is inlined as a string below rather than served from frontend/public/ via
FastAPI's app.frontend()/StaticFiles: that relies on Vercel's build-time static-promotion scan,
which (confirmed via `vercel logs` on the first real deploy, 2026-09-29) did NOT bundle
frontend/public/ into the function — it crashed with "Frontend directory 'frontend/public' does
not exist" at runtime. Root cause not fully diagnosed (likely: the promotion scan doesn't apply,
or applies differently, for a custom `[tool.vercel] entrypoint` vs. the default `app.py`/`main.py`
at repo root shown in Vercel's docs examples). Inlining sidesteps it entirely for now — it's pure
Python, so it's guaranteed to be in the bundle.

When a real frontend kit with an actual build step lands (frontend/README.md), that build output
(e.g. frontend/dist/ from `npm run build`) should go through Vercel's standard static-build
pipeline instead (a real Build Command + Output Directory), not this static-promotion path — see
RUNBOOK.md "Known gotchas" before reproducing this trap with a real frontend.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

_allowed = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed or ["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Dark Factory — Pocketful</title>
<style>
  :root {
    --bg: #ffffff; --text: #111827; --text-muted: #4b5563; --surface: #f3f4f6; --border-ui: #6b7280;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #0b1220; --text: #f9fafb; --text-muted: #9ca3af; --surface: #111a2e; --border-ui: #9ca3af; }
  }
  body { margin: 0; padding: 2rem; background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; }
  main { max-width: 32rem; margin: 4rem auto; text-align: center; }
  h1 { font-size: 1.5rem; }
  p { color: var(--text-muted); }
  .badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
  .badge[data-status="ok"] { background: #16a34a22; color: #16a34a; }
  .badge[data-status="checking"] { background: #6b728022; color: #6b7280; }
  .badge[data-status="error"] { background: #dc262622; color: #dc2626; }
</style>
</head>
<body>
<main data-mode="live">
  <h1>Dark Factory — Pocketful</h1>
  <p>Hello-world walking skeleton. Replace this page with the real frontend kit (see frontend/README.md).</p>
  <p>API status: <span id="status" class="badge" data-status="checking">checking…</span></p>
</main>
<script>
  fetch('/health')
    .then((r) => r.json())
    .then((data) => {
      const el = document.getElementById('status');
      el.textContent = data.status + ' (' + data.mode + ')';
      el.dataset.status = data.status === 'ok' ? 'ok' : 'error';
    })
    .catch(() => {
      const el = document.getElementById('status');
      el.textContent = 'unreachable';
      el.dataset.status = 'error';
    });
</script>
</body>
</html>
"""


@app.get("/health")
def health():
    return {"status": "ok", "mode": os.environ.get("APP_MODE", "live")}


@app.get("/", response_class=HTMLResponse)
def index():
    return _PAGE
