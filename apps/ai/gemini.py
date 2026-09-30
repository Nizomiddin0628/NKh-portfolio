"""Google Gemini REST client — no SDK, only the standard library.

Endpoints (https://ai.google.dev/api):
    POST {BASE}/models/{model}:generateContent
    POST {BASE}/models/{model}:streamGenerateContent?alt=sse
    GET  {BASE}/models

The key is read from settings.GEMINI_API_KEY (.env) and is sent only in the
request header; it never appears in logs, errors or responses.

Model chain: settings.GEMINI_MODELS (comma separated). A model that answers
404 (unknown), 429 (quota) or 503 (overloaded) is skipped and the next one is
tried; the last model that worked is remembered for 30 minutes so it is tried
first next time.
"""
import base64
import json
import logging
import ssl
import time
import urllib.error
import urllib.request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODELS = ("gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash",
                  "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite")
LITE_MODELS = ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash")
REMEMBER_SECONDS = 30 * 60


class AiError(Exception):
    """A problem the user can be told about. `code` is one of:
    no_key, bad_key, quota, busy, denied, blocked, stopped, timeout, generic."""

    def __init__(self, code, detail=""):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def api_key():
    return (getattr(settings, "GEMINI_API_KEY", "") or "").strip()


def enabled():
    return bool(api_key())


def models(kind="main"):
    """Model names to try, in order. The last working one goes first."""
    if kind == "lite":
        chain = list(getattr(settings, "GEMINI_LITE_MODELS", None) or LITE_MODELS)
    else:
        chain = list(getattr(settings, "GEMINI_MODELS", None) or DEFAULT_MODELS)
    last = cache.get(f"ai:model:{kind}")
    if last in chain:
        chain.remove(last)
        chain.insert(0, last)
    return chain


def _remember(kind, model):
    cache.set(f"ai:model:{kind}", model, REMEMBER_SECONDS)


def _classify(status, text):
    low = (text or "").lower()
    if status in (401, 403) or "api key not valid" in low or "api_key_invalid" in low:
        return "bad_key"
    if status == 429 or "resource_exhausted" in low or "quota" in low:
        return "quota"
    if status in (500, 502, 503, 504) or "overloaded" in low:
        return "busy"
    if status == 404:
        return "no_model"
    if "permission" in low:
        return "denied"
    return "generic"


def _request(url, body=None, timeout=90):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET", headers={
        "Content-Type": "application/json",
        "x-goog-api-key": api_key(),
        "User-Agent": "portfolio-assistant/1.0",
    })
    ctx = ssl.create_default_context()
    return urllib.request.urlopen(req, timeout=timeout, context=ctx)


def _read_error(exc):
    try:
        return exc.read().decode("utf-8", "replace")
    except Exception:
        return ""


def list_models():
    """Names of the generateContent-capable models the key can use."""
    if not enabled():
        raise AiError("no_key")
    try:
        with _request(f"{BASE}/models?pageSize=100", timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise AiError(_classify(exc.code, _read_error(exc)), "list") from exc
    except Exception as exc:
        raise AiError("generic", str(exc)) from exc
    out = []
    for m in data.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            out.append(m.get("name", "").replace("models/", ""))
    return out


# ── Requests ─────────────────────────────────────────────────────────────────

def _merge_stream(resp, on_text, stop):
    """Read an SSE stream and rebuild one response dict out of the chunks.

    Text parts are concatenated into a single part; function calls are kept
    as separate parts; thoughtSignature values are preserved on the part
    they arrived with, so the model's turn can be sent back verbatim.
    """
    parts = []
    text_buf = []
    text_sig = None
    usage = {}
    grounding = {}
    finish = ""
    blocked = None

    def flush_text():
        nonlocal text_buf, text_sig
        if text_buf:
            part = {"text": "".join(text_buf)}
            if text_sig:
                part["thoughtSignature"] = text_sig
            parts.append(part)
            text_buf, text_sig = [], None

    for raw in resp:
        if stop and stop():
            raise AiError("stopped")
        line = raw.decode("utf-8", "replace").strip()
        if not line.startswith("data:"):
            continue
        try:
            chunk = json.loads(line[5:].strip())
        except ValueError:
            continue
        if chunk.get("usageMetadata"):
            usage = chunk["usageMetadata"]
        if chunk.get("promptFeedback", {}).get("blockReason"):
            blocked = chunk["promptFeedback"]["blockReason"]
        for cand in chunk.get("candidates", [])[:1]:
            if cand.get("groundingMetadata"):
                grounding = cand["groundingMetadata"]
            finish = cand.get("finishReason", finish)
            for part in cand.get("content", {}).get("parts", []):
                if part.get("thought"):
                    continue
                if "text" in part:
                    delta = part["text"]
                    if delta:
                        text_buf.append(delta)
                        if on_text:
                            on_text(delta)
                    if part.get("thoughtSignature") and not text_sig:
                        text_sig = part["thoughtSignature"]
                else:
                    flush_text()
                    parts.append(part)
    flush_text()
    if blocked and not parts:
        raise AiError("blocked", blocked)
    return {
        "candidates": [{"content": {"role": "model", "parts": parts}, "finishReason": finish,
                        "groundingMetadata": grounding}],
        "usageMetadata": usage,
    }


def generate(contents, *, system=None, tools=None, temperature=0.3, max_tokens=4096,
             think="low", on_text=None, stop=None, timeout=90, kind="main",
             response_mime=None):
    """Call Gemini once (with streaming when `on_text` is given).

    Returns {"model": name, "data": response-dict}. Raises AiError.
    """
    if not enabled():
        raise AiError("no_key")

    gen = {"temperature": temperature, "maxOutputTokens": max_tokens}
    if think:
        gen["thinkingConfig"] = {"thinkingLevel": think}
    if response_mime:
        gen["responseMimeType"] = response_mime
    body = {"contents": contents, "generationConfig": gen}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if tools:
        body["tools"] = tools

    last = AiError("generic", "no model answered")
    for model in models(kind):
        method = "streamGenerateContent?alt=sse" if on_text else "generateContent"
        url = f"{BASE}/models/{model}:{method}"
        tried_without_thinking = False
        while True:
            try:
                if stop and stop():
                    raise AiError("stopped")
                with _request(url, body, timeout=timeout) as resp:
                    if on_text:
                        data = _merge_stream(resp, on_text, stop)
                    else:
                        data = json.loads(resp.read().decode())
                _remember(kind, model)
                return {"model": model, "data": data}
            except urllib.error.HTTPError as exc:
                text = _read_error(exc)
                if exc.code == 400 and "thinking" in text.lower() and not tried_without_thinking:
                    body["generationConfig"].pop("thinkingConfig", None)
                    tried_without_thinking = True
                    continue
                code = _classify(exc.code, text)
                logger.warning("Gemini %s -> HTTP %s (%s)", model, exc.code, code)
                last = AiError(code, f"HTTP {exc.code}")
                if code in ("no_model", "quota", "busy"):
                    break  # next model
                raise last from exc
            except AiError:
                raise
            except TimeoutError as exc:
                last = AiError("timeout", str(exc))
                break
            except Exception as exc:
                if "timed out" in str(exc).lower():
                    last = AiError("timeout", str(exc))
                    break
                logger.warning("Gemini %s failed: %s", model, exc)
                last = AiError("generic", type(exc).__name__)
                break
    raise last


# ── Reading a response ───────────────────────────────────────────────────────

def parts_of(data):
    try:
        return data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return []


def text_of(data):
    return "".join(p.get("text", "") for p in parts_of(data) if not p.get("thought")).strip()


def calls_of(data):
    return [p["functionCall"] for p in parts_of(data) if "functionCall" in p]


def sources_of(data):
    out, seen = [], set()
    try:
        chunks = data["candidates"][0].get("groundingMetadata", {}).get("groundingChunks", [])
    except (KeyError, IndexError, TypeError):
        chunks = []
    for c in chunks:
        web = c.get("web") or {}
        uri, title = web.get("uri"), web.get("title") or web.get("uri")
        if uri and uri not in seen:
            seen.add(uri)
            out.append({"title": title[:80], "url": uri})
    return out[:6]


def usage_of(data):
    u = data.get("usageMetadata") or {}
    return int(u.get("promptTokenCount", 0) or 0), int(u.get("candidatesTokenCount", 0) or 0)


# ── Helpers ──────────────────────────────────────────────────────────────────

def inline_part(raw, mime):
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(raw).decode()}}


TRANSCRIBE_PROMPT = (
    "Transcribe this audio exactly as spoken, in the language spoken (Uzbek, Russian or English). "
    "Write Uzbek in Latin script. Output only the transcript, no comments. "
    "If a part is unintelligible write [unclear]."
)


def transcribe(raw, mime="audio/ogg"):
    """Speech -> text with the cheapest model. Returns a plain string."""
    res = generate(
        [{"role": "user", "parts": [inline_part(raw, mime), {"text": TRANSCRIBE_PROMPT}]}],
        temperature=0, max_tokens=1024, think="minimal", kind="lite", timeout=60,
    )
    return text_of(res["data"])


def ping():
    """One tiny request to prove the key works. Returns the model name."""
    started = time.time()
    res = generate([{"role": "user", "parts": [{"text": "Reply with the single word: ok"}]}],
                   temperature=0, max_tokens=16, think="minimal", timeout=30)
    return res["model"], int((time.time() - started) * 1000)
