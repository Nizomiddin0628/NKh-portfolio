"""HTTP endpoints of the assistant (all under /ai/, outside the language prefix).

    GET  /ai/status/                 -> is it on, role, greeting, suggested questions
    POST /ai/ask/                    -> streamed answer (NDJSON lines)
    POST /ai/transcribe/             -> owner: voice file -> text
    GET  /ai/actions/                -> owner: changes waiting for confirmation
    POST /ai/actions/<id>/confirm/   -> owner
    POST /ai/actions/<id>/cancel/    -> owner
    POST /ai/tg/                     -> Telegram webhook (secret header)
"""
import json
import logging
import queue
import threading
import uuid

from django.conf import settings
from django.db import connection
from django.http import JsonResponse, StreamingHttpResponse
from django.utils.translation import get_language
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from . import actions, agent, gemini, prompts
from .actions import ActionError
from .files import prepare
from .gemini import AiError
from .limits import count_guest, guest_allowed, ip_hash

logger = logging.getLogger(__name__)
MAX_QUESTION = 2000
GUEST_FILE = 8 * 1024 * 1024       # a spec PDF or a few screenshots
OWNER_FILE = 20 * 1024 * 1024
GUEST_AUDIO = 3 * 1024 * 1024      # about two minutes of opus
LANGS = ("en", "uz", "ru")


def _role(request):
    u = getattr(request, "user", None)
    return "owner" if (u is not None and u.is_authenticated and u.is_active and u.is_superuser) else "guest"


def _lang(request, value=""):
    value = (value or request.GET.get("lang") or get_language() or "en").split("-")[0]
    return value if value in LANGS else "en"


def _json(request):
    if request.content_type and request.content_type.startswith("application/json"):
        try:
            return json.loads(request.body.decode() or "{}")
        except ValueError:
            return {}
    return request.POST


@require_GET
@ensure_csrf_cookie
@never_cache
def status(request):
    role = _role(request)
    lang = _lang(request)
    data = {
        "enabled": gemini.enabled(), "role": role, "lang": lang,
        "greeting": prompts.pick(prompts.OWNER_GREETING if role == "owner" else prompts.GREETING, lang),
        "chips": prompts.pick(prompts.OWNER_CHIPS if role == "owner" else prompts.CHIPS, lang),
        "features": {"attach": True, "voice": True, "web": role == "owner",
                     "max_file_mb": (OWNER_FILE if role == "owner" else GUEST_FILE) // (1024 * 1024)},
    }
    if role == "owner":
        data["actions"] = [actions.as_dict(a) for a in actions.pending()]
    return JsonResponse(data)


@require_POST
@never_cache
def ask(request):
    role = _role(request)
    body = _json(request)
    lang = _lang(request, body.get("lang", ""))
    question = (body.get("q") or "").strip()[:MAX_QUESTION]
    mode = "web" if body.get("mode") == "web" else "local"
    session = (body.get("session") or "")[:40]
    page = (body.get("page") or "")[:300]
    try:
        history = json.loads(body.get("history") or "[]") if isinstance(body.get("history"), str) \
            else (body.get("history") or [])
    except ValueError:
        history = []
    if not isinstance(history, list):
        history = []

    if not gemini.enabled():
        return JsonResponse({"ok": False, "code": "no_key", "error": prompts.error_text("no_key", lang)})

    iph = ip_hash(request)
    if role == "guest":
        code = guest_allowed(iph)
        if code:
            return JsonResponse({"ok": False, "code": code, "error": prompts.error_text(code, lang)}, status=429)

    attachments, kind = [], "ask"
    upload = request.FILES.get("file")
    if upload is not None:
        limit = OWNER_FILE if role == "owner" else GUEST_FILE
        if upload.size > limit:
            return JsonResponse({"ok": False, "code": "file", "error": f"max {limit // (1024 * 1024)} MB"}, status=400)
        try:
            part, ftype = prepare(upload.read(), upload.content_type or "")
        except AiError as exc:
            return JsonResponse({"ok": False, "code": "file", "error": exc.detail}, status=400)
        attachments.append(part)
        kind = "file"
        if not question:
            question = {"uz": "Shu faylni ko'rib chiqing.", "ru": "Посмотрите этот файл.",
                        "en": "Please look at this file."}[lang]
        question = f"[{ftype}: {upload.name[:80]}] {question}"
    if not question and not attachments:
        return JsonResponse({"ok": False, "code": "empty", "error": "empty question"}, status=400)
    if role == "guest":
        count_guest(iph)

    box, flag = queue.Queue(), {"stop": False}

    def work():
        try:
            res = agent.ask(role=role, channel="site", lang=lang, question=question, history=history,
                            attachments=attachments, mode=mode, session=session, page=page,
                            ip_hash=iph, kind=kind,
                            on_text=lambda d: box.put(("t", d)), stop=lambda: flag["stop"])
            box.put(("done", res))
        except Exception as exc:
            logger.exception("ask failed")
            box.put(("done", {"ok": False, "code": "generic", "error": prompts.error_text("generic", lang),
                              "detail": type(exc).__name__}))
        finally:
            connection.close()

    def gen():
        yield json.dumps({"start": True}) + "\n"
        try:
            while True:
                try:
                    what, val = box.get(timeout=120)
                except queue.Empty:
                    yield json.dumps({"done": True, "ok": False, "code": "timeout",
                                      "error": prompts.error_text("timeout", lang)}) + "\n"
                    return
                if what == "t":
                    yield json.dumps({"reset": True} if val is None else {"t": val}) + "\n"
                else:
                    yield json.dumps({"done": True, **val}) + "\n"
                    return
        finally:
            flag["stop"] = True

    if getattr(settings, "AI_RUN_ASYNC", True):
        threading.Thread(target=work, daemon=True).start()
    else:
        work()
    resp = StreamingHttpResponse(gen(), content_type="text/event-stream; charset=utf-8")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp


@require_POST
@never_cache
def transcribe(request):
    role = _role(request)
    lang = _lang(request, request.POST.get("lang", ""))
    if not gemini.enabled():
        return JsonResponse({"ok": False, "code": "no_key", "error": prompts.error_text("no_key", lang)})
    upload = request.FILES.get("file")
    if upload is None:
        return JsonResponse({"ok": False, "error": "no file"}, status=400)
    if upload.size > (15 * 1024 * 1024 if role == "owner" else GUEST_AUDIO):
        return JsonResponse({"ok": False, "code": "file", "error": "too long"}, status=400)
    if role == "guest":
        iph = ip_hash(request)
        code = guest_allowed(iph)
        if code:
            return JsonResponse({"ok": False, "code": code, "error": prompts.error_text(code, lang)}, status=429)
        count_guest(iph)
    raw = upload.read()
    try:
        text = gemini.transcribe(raw, (upload.content_type or "audio/webm").split(";")[0])
    except AiError as exc:
        return JsonResponse({"ok": False, "code": exc.code, "error": prompts.error_text(exc.code, lang)})
    return JsonResponse({"ok": True, "text": text})


@require_GET
@never_cache
def actions_list(request):
    if _role(request) != "owner":
        return JsonResponse({"ok": False, "error": "owner only"}, status=403)
    return JsonResponse({"ok": True, "actions": [actions.as_dict(a) for a in actions.pending()]})


@require_POST
def action_confirm(request, pk):
    if _role(request) != "owner":
        return JsonResponse({"ok": False, "error": "owner only"}, status=403)
    try:
        a = actions.confirm(pk, channel="site")
    except ActionError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    return JsonResponse({"ok": a.status == "done", "action": actions.as_dict(a)})


@require_POST
def action_cancel(request, pk):
    if _role(request) != "owner":
        return JsonResponse({"ok": False, "error": "owner only"}, status=403)
    try:
        a = actions.cancel(pk, channel="site")
    except ActionError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    return JsonResponse({"ok": True, "action": actions.as_dict(a)})


@csrf_exempt
@require_POST
def tg_webhook(request):
    secret = (getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "") or "").strip()
    if not secret or request.headers.get("X-Telegram-Bot-Api-Secret-Token", "") != secret:
        return JsonResponse({"ok": False}, status=403)
    try:
        update = json.loads(request.body.decode() or "{}")
    except ValueError:
        return JsonResponse({"ok": False}, status=400)
    from . import telegram
    try:
        telegram.process_update(update)
    except Exception:
        logger.exception("telegram update failed")
    return JsonResponse({"ok": True})


def new_session_id():
    return uuid.uuid4().hex
