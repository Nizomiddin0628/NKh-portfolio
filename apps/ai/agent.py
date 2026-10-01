"""The agent: question -> (tools ...) -> answer.

    res = ask(role="guest", channel="site", lang="uz", question="...", history=[...])

One call to Gemini with the tool declarations; when the model asks for a
tool, it is run and the result is sent back, at most MAX_STEPS times. The
model's own turn (with thought signatures) is returned verbatim, as the API
requires. In web mode Google Search grounding replaces the tools.
"""
import logging
import time

from django.utils import timezone

from . import gemini, prompts, state, tools
from .actions import as_dict
from .gemini import AiError
from .models import AiLog
from .render import clean, strip_marker, text_only

logger = logging.getLogger(__name__)
MAX_STEPS = 8
HISTORY_TURNS = 8


def _now_text():
    now = timezone.localtime()
    return f"{now:%A, %d %B %Y, %H:%M} ({now.tzname()})"


def _system(ctx, mode):
    if ctx.is_owner:
        rules = prompts.OWNER_RULES + "\n" + (prompts.AUTO_RULES if ctx.auto else prompts.CONFIRM_RULES)
        if mode == "web":
            rules += "\n\n" + prompts.WEB_RULES
        who = "Nizomiddin Khalilov (the site owner)"
    else:
        rules = prompts.GUEST_RULES
        who = "a site visitor (guest)"
    return prompts.SYSTEM.format(who=who, role=ctx.role, channel=ctx.channel, now=_now_text(),
                                 lang=ctx.lang, state=state.state(ctx.lang),
                                 knowledge=state.knowledge(), role_rules=rules)


def _history_contents(history):
    out = []
    for m in list(history or [])[-HISTORY_TURNS:]:
        text = text_only(m.get("text", ""))[:2000]
        if not text:
            continue
        role = "model" if m.get("role") == "model" else "user"
        if not out and role == "model":
            continue  # a conversation must start with the user
        if out and out[-1]["role"] == role:
            out[-1]["parts"][0]["text"] += "\n" + text
        else:
            out.append({"role": role, "parts": [{"text": text}]})
    return out


def ask(*, role="guest", channel="site", lang="en", question="", history=(), attachments=(),
        on_text=None, stop=None, mode="local", session="", page="", ip_hash="", chat_id=None,
        kind="ask", auto=False):
    started = time.time()
    lang = lang if lang in ("en", "uz", "ru") else "en"
    mode = "web" if (mode == "web" and role == "owner") else "local"
    ctx = tools.Ctx(role=role, channel=channel, lang=lang, session=session, page=page,
                    ip_hash=ip_hash, history=list(history or []), question=question,
                    auto=bool(auto and role == "owner"))
    log = AiLog(channel=channel, role=role, kind=kind, lang=lang, mode=mode, question=question[:4000],
                ip_hash=ip_hash, session=session, chat_id=chat_id)

    decls = tools.available(ctx)
    system = _system(ctx, mode)
    user_parts = list(attachments) + [{"text": question or ("Describe what you see." if attachments else "Hello")}]
    contents = _history_contents(history) + [{"role": "user", "parts": user_parts}]

    answer, model_name, steps, tin, tout, sources = "", "", 0, 0, 0, []
    try:
        for step in range(MAX_STEPS + 1):
            final = step == MAX_STEPS
            if mode == "web":
                tl = [{"google_search": {}}]
            else:
                tl = None if final else [{"function_declarations": decls}]
            res = gemini.generate(contents, system=system, tools=tl, on_text=on_text, stop=stop,
                                  temperature=0.4 if role == "owner" else 0.3)
            data, model_name = res["data"], res["model"]
            steps += 1
            a, b = gemini.usage_of(data)
            tin, tout = tin + a, tout + b
            calls = [] if (final or mode == "web") else gemini.calls_of(data)
            if not calls:
                answer = gemini.text_of(data)
                if mode == "web":
                    sources = gemini.sources_of(data)
                break
            if on_text:
                on_text(None)  # the streamed draft is void: the model chose a tool
            contents.append({"role": "model", "parts": gemini.parts_of(data)})
            contents.append({"role": "user", "parts": [
                {"functionResponse": {"name": c["name"], "response": {"result": tools.run(ctx, c["name"], c.get("args"))}}}
                for c in calls[:6]]})
    except AiError as exc:
        log.ok, log.error, log.model, log.steps = False, exc.code, model_name, steps
        log.ms = int((time.time() - started) * 1000)
        if exc.code != "stopped":
            log.save()
        return {"ok": False, "code": exc.code, "error": prompts.error_text(exc.code, lang),
                "actions": [as_dict(a) for a in ctx.actions]}

    answer, noinfo = strip_marker(answer)
    if not answer:
        answer = prompts.error_text("generic", lang)
    html_answer = clean(answer, channel)

    log.answer, log.model, log.steps, log.tokens_in, log.tokens_out = answer[:6000], model_name, steps, tin, tout
    log.tools_used = ",".join(ctx.used)[:200]
    log.unanswered = noinfo and role == "guest"
    log.ms = int((time.time() - started) * 1000)
    log.save()

    return {"ok": True, "answer": html_answer, "text": answer, "model": model_name, "steps": steps,
            "sources": sources, "actions": [as_dict(a) for a in ctx.actions],
            "lead_saved": bool(ctx.leads), "unanswered": noinfo, "ms": log.ms}
