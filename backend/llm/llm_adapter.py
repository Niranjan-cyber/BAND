"""Config-driven LLM adapter (standard library only). One interface, provider chosen by environment.

Why: switching model provider mid-event must be a config change, not a migration with a missed caller.
Every model call in the product goes through `complete()` or `complete_json()`.

Environment
  LLM_PROVIDER    echo | anthropic | openai-compatible      (default: echo, offline and deterministic)
  LLM_MODEL       the provider's model id                    (never hardcode; check the provider's current docs)
  LLM_API_KEY     secret; backend only, never in a client bundle
  LLM_BASE_URL    override base URL (required for openai-compatible gateways; optional for anthropic)
  LLM_TIMEOUT_S   per-request timeout in seconds             (default 30)
  LLM_REPLAY_DIR  if set: saved responses are replayed from / recorded to this directory
  LLM_RECORD      "1" to record live responses into LLM_REPLAY_DIR (otherwise replay only, falling back to live)

Add a provider by writing one function `_call_<name>(req, cfg) -> dict` and registering it in PROVIDERS.
Cloud-native providers (e.g. a managed-model service behind your cloud's SDK) plug in the same way.
"""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class LlmRequest:
    messages: list                      # [{"role": "system"|"user"|"assistant", "content": str}, ...]
    max_tokens: int = 1024
    temperature: float = 0.2
    timeout_s: Optional[float] = None


@dataclass
class LlmResponse:
    text: str
    provider: str
    model: str
    latency_ms: int
    replayed: bool = False
    usage: dict = field(default_factory=dict)


def _cfg():
    return {
        "provider": os.environ.get("LLM_PROVIDER", "echo"),
        "model": os.environ.get("LLM_MODEL", ""),
        "api_key": os.environ.get("LLM_API_KEY", ""),
        "base_url": os.environ.get("LLM_BASE_URL", ""),
        "timeout_s": float(os.environ.get("LLM_TIMEOUT_S", "30")),
        "replay_dir": os.environ.get("LLM_REPLAY_DIR", ""),
        "record": os.environ.get("LLM_RECORD", "") == "1",
    }


def _post_json(url, headers, payload, timeout):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        raise RuntimeError(f"LLM HTTP {e.code}: {detail}") from None


def _call_echo(req, cfg):
    last_user = next((m["content"] for m in reversed(req.messages) if m["role"] == "user"), "")
    return {"text": f"[echo] {last_user[:200]}", "usage": {}}


def _call_anthropic(req, cfg):
    if not cfg["api_key"] or not cfg["model"]:
        raise RuntimeError("LLM_API_KEY and LLM_MODEL are required for the anthropic provider")
    base = (cfg["base_url"] or "https://api.anthropic.com").rstrip("/")
    system = "\n\n".join(m["content"] for m in req.messages if m["role"] == "system")
    msgs = [m for m in req.messages if m["role"] != "system"]
    payload = {"model": cfg["model"], "max_tokens": req.max_tokens, "temperature": req.temperature, "messages": msgs}
    if system:
        payload["system"] = system
    out = _post_json(f"{base}/v1/messages",
                     {"x-api-key": cfg["api_key"], "anthropic-version": "2023-06-01"},
                     payload, req.timeout_s or cfg["timeout_s"])
    text = "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
    u = out.get("usage", {})
    return {"text": text, "usage": {"input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens")}}


def _call_openai_compatible(req, cfg):
    if not cfg["api_key"] or not cfg["model"] or not cfg["base_url"]:
        raise RuntimeError("LLM_API_KEY, LLM_MODEL and LLM_BASE_URL are required for openai-compatible")
    payload = {"model": cfg["model"], "messages": req.messages, "max_tokens": req.max_tokens,
               "temperature": req.temperature}
    out = _post_json(cfg["base_url"].rstrip("/") + "/chat/completions",
                     {"Authorization": f"Bearer {cfg['api_key']}"}, payload, req.timeout_s or cfg["timeout_s"])
    text = out["choices"][0]["message"]["content"] or ""
    u = out.get("usage", {})
    return {"text": text, "usage": {"input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens")}}


PROVIDERS: dict = {
    "echo": _call_echo,
    "anthropic": _call_anthropic,
    "openai-compatible": _call_openai_compatible,
}


def _replay_path(cfg, req):
    key = json.dumps([cfg["provider"], cfg["model"], req.messages, req.temperature, req.max_tokens], sort_keys=True)
    return os.path.join(cfg["replay_dir"], hashlib.sha256(key.encode()).hexdigest()[:24] + ".json")


def complete(req: LlmRequest) -> LlmResponse:
    cfg = _cfg()
    if cfg["replay_dir"]:
        path = _replay_path(cfg, req)
        if os.path.exists(path):
            saved = json.load(open(path))
            return LlmResponse(saved["text"], cfg["provider"], cfg["model"], 0, replayed=True, usage=saved.get("usage", {}))
    if cfg["provider"] not in PROVIDERS:
        raise RuntimeError(f"Unknown LLM_PROVIDER {cfg['provider']!r}; known: {sorted(PROVIDERS)}")
    t0 = time.time()
    out = PROVIDERS[cfg["provider"]](req, cfg)
    latency = int((time.time() - t0) * 1000)
    resp = LlmResponse(out["text"], cfg["provider"], cfg["model"], latency, usage=out.get("usage", {}))
    # Log every call: one line, greppable, no prompt content.
    print(json.dumps({"llm_call": True, "provider": resp.provider, "model": resp.model,
                      "latency_ms": latency, "usage": resp.usage}))
    if cfg["replay_dir"] and cfg["record"]:
        os.makedirs(cfg["replay_dir"], exist_ok=True)
        json.dump({"text": resp.text, "usage": resp.usage}, open(_replay_path(cfg, req), "w"))
    return resp


def _extract_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.IGNORECASE)
    start = min([i for i in (t.find("{"), t.find("[")) if i != -1], default=-1)
    if start == -1:
        raise ValueError("no JSON found in model output")
    return json.loads(t[start:])


def complete_json(req: LlmRequest, validate: Callable[[object], object]):
    """Ask for JSON, validate it, retry once with the error message. Never returns a fake result on failure."""
    last_err = None
    messages = list(req.messages)
    for _ in range(2):
        r = complete(LlmRequest(messages, req.max_tokens, req.temperature, req.timeout_s))
        try:
            return validate(_extract_json(r.text))
        except Exception as e:  # validation or parse error
            last_err = e
            messages = messages + [
                {"role": "assistant", "content": r.text},
                {"role": "user", "content": f"Your output was invalid ({e}). Reply with valid JSON only."},
            ]
    raise RuntimeError(f"model did not return valid JSON after retry: {last_err}")


if __name__ == "__main__":
    print(complete(LlmRequest([{"role": "user", "content": "hello from the adapter smoke test"}])).text)
