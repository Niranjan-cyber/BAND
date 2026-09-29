# backend/

Put your practiced backend service shape here. Required properties:
- One deployable service with a `GET /health` route (used by the pipeline and `public_url_check.py`).
- All model calls go through `llm/` (config-driven provider/model).
- CORS allow-list read from an env var set by the pipeline.
- No catch-all exception handlers that hide failures; log one line per external call.
- Packaged identically locally and in the cloud (same root, same import paths).
