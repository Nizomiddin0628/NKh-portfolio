"""AI assistant tests. Gemini and Telegram are faked: no network, no key."""
import json

import pytest
from django.contrib.auth.models import User
from django.test import Client, override_settings
from django.utils import timezone

from apps.ai import actions, agent, digest, gemini, render, telegram, tools
from apps.ai.models import AiAction, AiChat, AiKnowledge, AiLog, Lead, Reminder
from apps.core.models import SiteSettings
from apps.projects.models import Project

AI = {"GEMINI_API_KEY": "test-key", "AI_RUN_ASYNC": False, "TELEGRAM_BOT_TOKEN": "1:x",
      "TELEGRAM_CHAT_ID": "777", "TELEGRAM_WEBHOOK_SECRET": "s3cret", "AI_GUEST_HOURLY": 3}


def fake_gemini(monkeypatch, script):
    """Scripted model: each step is {"call": (name, args)} or {"text": "..."}."""
    steps = list(script)

    def generate(contents, *, on_text=None, stop=None, **kw):
        step = steps.pop(0) if steps else {"text": "ok"}
        if "call" in step:
            name, args = step["call"]
            parts = [{"functionCall": {"name": name, "args": args}, "thoughtSignature": "sig"}]
        else:
            if on_text:
                on_text(step["text"])
            parts = [{"text": step["text"]}]
        return {"model": "fake-model", "data": {
            "candidates": [{"content": {"role": "model", "parts": parts}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5}}}

    monkeypatch.setattr(gemini, "generate", generate)
    return steps


def fake_telegram(monkeypatch):
    sent = []

    def call(method, **payload):
        sent.append((method, payload))
        return {"message_id": len(sent), "chat": {"id": payload.get("chat_id")}}

    monkeypatch.setattr(telegram, "call", call)
    monkeypatch.setattr("apps.core.notify.telegram_send", lambda text, chat_id=None: sent.append(("notify", {"text": text, "chat": chat_id})) or True)
    monkeypatch.setattr("apps.ai.notify.telegram_send", lambda text, chat_id=None: sent.append(("notify", {"text": text, "chat": chat_id})) or True)
    return sent


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def owner(db):
    return User.objects.create_superuser("nizom", "n@example.com", "pw")


@pytest.fixture
def project(db):
    return Project.objects.create(title="Smart Yard", slug="smart-yard", tagline_en="Gate automation",
                                  tagline_uz="Darvoza avtomatikasi", is_published=True)


# ── Roles and tools ──────────────────────────────────────────────────────────

def test_guest_never_sees_owner_tools(db):
    guest = {d["name"] for d in tools.available(tools.Ctx(role="guest"))}
    owner_tools = {d["name"] for d in tools.available(tools.Ctx(role="owner"))}
    assert "save_lead" in guest and "projects" in guest
    assert not guest & {"leads", "update_settings", "remember_fact", "stats"}
    assert {"leads", "update_settings", "remember_fact", "stats"} <= owner_tools


def test_guest_cannot_run_owner_tool(db):
    res = tools.run(tools.Ctx(role="guest"), "leads", {})
    assert res == {"ok": False, "error": "not allowed"}


def test_projects_tool_returns_language(project):
    res = tools.run(tools.Ctx(role="guest", lang="uz"), "projects", {"query": "yard"})
    assert res["count"] == 1
    assert res["projects"][0]["tagline"] == "Darvoza avtomatikasi"
    assert res["projects"][0]["url"].endswith("/uz/work/smart-yard/")


# ── Agent loop ───────────────────────────────────────────────────────────────

@override_settings(**AI)
def test_agent_calls_tool_then_answers(db, project, monkeypatch):
    fake_gemini(monkeypatch, [{"call": ("projects", {"query": "yard"})},
                              {"text": "He built **Smart Yard**: https://khalilovn.uz/en/work/smart-yard/"}])
    res = agent.ask(role="guest", channel="site", lang="en", question="what did he build?")
    assert res["ok"] and res["steps"] == 2
    assert "<b>Smart Yard</b>" in res["answer"]
    assert '<a href="https://khalilovn.uz/en/work/smart-yard/">' in res["answer"]
    log = AiLog.objects.get()
    assert log.tools_used == "projects" and log.role == "guest" and log.ok


@override_settings(**AI)
def test_agent_marks_unanswered(db, monkeypatch):
    fake_gemini(monkeypatch, [{"text": "I don't know that. [[NOINFO]]"}])
    res = agent.ask(role="guest", channel="site", lang="en", question="favourite food?")
    assert res["unanswered"] and "[[NOINFO]]" not in res["answer"]
    assert AiLog.objects.get().unanswered


@override_settings(**AI)
def test_agent_error_is_localised(db, monkeypatch):
    def boom(*a, **k):
        raise gemini.AiError("quota")
    monkeypatch.setattr(gemini, "generate", boom)
    res = agent.ask(role="guest", channel="site", lang="uz", question="salom")
    assert not res["ok"] and res["code"] == "quota" and "limit" in res["error"].lower()


# ── Leads ────────────────────────────────────────────────────────────────────

@override_settings(**AI)
def test_lead_saved_and_owner_notified(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    fake_gemini(monkeypatch, [
        {"call": ("save_lead", {"name": "Aziz", "contact": "aziz@mail.com", "need": "Telegram bot for a shop"})},
        {"text": "Rahmat, Nizomiddin siz bilan bog'lanadi."}])
    res = agent.ask(role="guest", channel="site", lang="uz", question="aziz@mail.com", session="s1",
                    history=[{"role": "user", "text": "Menga bot kerak"}, {"role": "model", "text": "Qanday?"}])
    assert res["ok"] and res["lead_saved"]
    lead = Lead.objects.get()
    assert lead.contact == "aziz@mail.com" and "Menga bot kerak" in lead.transcript
    assert any(k == "sendMessage" and "aziz@mail.com" in p["text"] and "inline_keyboard" in p["reply_markup"]
               for k, p in sent)


def test_lead_rejects_bad_contact(db):
    res = tools.run(tools.Ctx(role="guest"), "save_lead", {"contact": "later", "need": "a big project please"})
    assert not res["ok"] and not Lead.objects.exists()


# ── Actions ──────────────────────────────────────────────────────────────────

def test_change_needs_confirmation(db):
    ctx = tools.Ctx(role="owner", channel="site")
    res = tools.run(ctx, "update_settings", {"field": "headline", "lang": "uz", "value": "Yangi sarlavha"})
    assert res["ok"] and "PENDING" in res["status"]
    assert SiteSettings.load().headline_uz != "Yangi sarlavha"
    action = AiAction.objects.get()
    assert action.status == "proposed"
    actions.confirm(action.pk)
    assert SiteSettings.load().headline_uz == "Yangi sarlavha"
    assert AiAction.objects.get().status == "done"
    with pytest.raises(actions.ActionError):
        actions.confirm(action.pk)


def test_guest_cannot_propose(db):
    res = tools.run(tools.Ctx(role="guest"), "update_settings", {"field": "headline", "lang": "uz", "value": "x"})
    assert res == {"ok": False, "error": "not allowed"} and not AiAction.objects.exists()


def test_unknown_field_refused(db):
    res = tools.run(tools.Ctx(role="owner"), "update_settings", {"field": "email", "value": "x@y.z"})
    assert not res["ok"] and not AiAction.objects.exists()


def test_cancel_and_expiry(db):
    ctx = tools.Ctx(role="owner")
    tools.run(ctx, "remember_fact", {"text": "Freelance loyihalar ham olaman"})
    a = AiAction.objects.get()
    actions.cancel(a.pk)
    assert AiAction.objects.get().status == "cancelled" and not AiKnowledge.objects.exists()
    tools.run(ctx, "remember_fact", {"text": "Ikkinchi fakt"})
    b = AiAction.objects.latest("pk")
    AiAction.objects.filter(pk=b.pk).update(expires_at=timezone.now() - timezone.timedelta(minutes=1))
    with pytest.raises(actions.ActionError):
        actions.confirm(b.pk)
    assert AiAction.objects.get(pk=b.pk).status == "expired"


def test_reminder_action(db):
    ctx = tools.Ctx(role="owner")
    due = (timezone.localtime() + timezone.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M")
    res = tools.run(ctx, "add_reminder", {"due": due, "text": "Call the client"})
    assert res["ok"]
    actions.confirm(AiAction.objects.get().pk)
    assert Reminder.objects.get().text == "Call the client"


# ── Rendering ────────────────────────────────────────────────────────────────

def test_clean_is_safe():
    out = render.clean('<script>alert(1)</script> **bold** `x` <b>ok</b> <img src=x onerror=1> see https://khalilovn.uz/uz/work/')
    assert "<script" not in out and "<img" not in out and "&lt;script&gt;" in out
    assert "<b>bold</b>" in out and "<code>x</code>" in out and "<b>ok</b>" in out
    assert '<a href="https://khalilovn.uz/uz/work/">' in out


def test_clean_scrubs_secrets():
    out = render.clean("token 123456789:AAHfiFhfjeKdkdjfkdjfkdjfkdjfkdjfkdjfkdj and key AIzaSyA1234567890abcdefghijklmnopqrstuv")
    assert "AAHfi" not in out and "AIzaSy" not in out


def test_split_telegram():
    parts = render.split_telegram("\n".join(f"line {i}" for i in range(2000)))
    assert len(parts) > 1 and all(len(p) <= 4000 for p in parts)


# ── HTTP ─────────────────────────────────────────────────────────────────────

@override_settings(**AI)
def test_status_and_stream(db, project, monkeypatch):
    fake_gemini(monkeypatch, [{"text": "Hello **there**"}])
    c = Client()
    st = c.get("/ai/status/?lang=uz").json()
    assert st["enabled"] and st["role"] == "guest" and st["chips"]
    r = c.post("/ai/ask/", {"q": "salom", "lang": "uz", "history": "[]"})
    assert r.status_code == 200
    lines = [json.loads(ln) for ln in b"".join(r.streaming_content).decode().strip().split("\n")]
    assert lines[0] == {"start": True}
    assert any("t" in ln for ln in lines)
    assert lines[-1]["done"] and lines[-1]["ok"] and "<b>there</b>" in lines[-1]["answer"]


@override_settings(**AI)
def test_guest_rate_limit(db, monkeypatch):
    fake_gemini(monkeypatch, [{"text": "a"}, {"text": "b"}, {"text": "c"}, {"text": "d"}])
    c = Client()
    for _ in range(3):
        r = c.post("/ai/ask/", {"q": "hi", "history": "[]"})
        list(r.streaming_content)
    r = c.post("/ai/ask/", {"q": "hi", "history": "[]"})
    assert r.status_code == 429 and r.json()["code"] == "limit"


@override_settings(**AI)
def test_guest_can_send_file_but_not_confirm(db, monkeypatch):
    import io

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image
    seen = {}

    def generate(contents, **kw):
        seen["parts"] = contents[-1]["parts"]
        return {"model": "fake", "data": {"candidates": [{"content": {"parts": [{"text": "A spec for a bot."}]}}]}}
    monkeypatch.setattr(gemini, "generate", generate)
    buf = io.BytesIO()
    Image.new("RGB", (40, 40), "red").save(buf, "PNG")
    c = Client()
    assert c.get("/ai/status/").json()["features"] == {"attach": True, "voice": True, "web": False, "max_file_mb": 8}
    r = c.post("/ai/ask/", {"q": "", "file": SimpleUploadedFile("brief.png", buf.getvalue(), "image/png")})
    done = json.loads(b"".join(r.streaming_content).decode().strip().split("\n")[-1])
    assert done["ok"] and "inline_data" in seen["parts"][0]
    assert AiLog.objects.get().kind == "file" and "brief.png" in AiLog.objects.get().question
    big = SimpleUploadedFile("big.pdf", b"%PDF" + b"0" * (9 * 1024 * 1024), "application/pdf")
    assert c.post("/ai/ask/", {"q": "x", "file": big}).status_code == 400
    assert c.get("/ai/actions/").status_code == 403
    assert c.post("/ai/actions/1/confirm/").status_code == 403


@override_settings(**AI)
def test_guest_voice_is_rate_limited(db, monkeypatch):
    from django.core.files.uploadedfile import SimpleUploadedFile
    monkeypatch.setattr(gemini, "transcribe", lambda raw, mime: "salom")
    c = Client()
    for _ in range(3):
        r = c.post("/ai/transcribe/", {"file": SimpleUploadedFile("v.webm", b"\x1aE\xdf\xa3abc", "audio/webm")})
        assert r.json() == {"ok": True, "text": "salom"}
    r = c.post("/ai/transcribe/", {"file": SimpleUploadedFile("v.webm", b"\x1aE\xdf\xa3abc", "audio/webm")})
    assert r.status_code == 429


@override_settings(**AI)
def test_owner_confirms_on_site(owner, monkeypatch):
    fake_gemini(monkeypatch, [{"call": ("update_settings", {"field": "location", "value": "Fergana"})},
                              {"text": "Ready, please confirm."}])
    c = Client()
    c.force_login(owner)
    assert c.get("/ai/status/").json()["role"] == "owner"
    r = c.post("/ai/ask/", {"q": "change location to Fergana", "history": "[]"})
    done = json.loads(b"".join(r.streaming_content).decode().strip().split("\n")[-1])
    assert done["actions"][0]["status"] == "proposed"
    r = c.post(f"/ai/actions/{done['actions'][0]['id']}/confirm/")
    assert r.json()["ok"] and SiteSettings.load().location == "Fergana"


@override_settings(**AI)
def test_webhook_secret(db):
    c = Client()
    assert c.post("/ai/tg/", data="{}", content_type="application/json").status_code == 403
    r = c.post("/ai/tg/", data="{}", content_type="application/json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="s3cret")
    assert r.status_code == 200


# ── Telegram ─────────────────────────────────────────────────────────────────

@override_settings(**AI)
def test_telegram_guest_is_refused(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    telegram.process_update({"message": {"chat": {"id": 5}, "from": {"id": 5}, "text": "hi"}})
    assert sent and sent[0][0] == "sendMessage" and "khalilovn.uz" in sent[0][1]["text"]
    assert not AiLog.objects.exists()


@override_settings(**AI)
def test_telegram_owner_gets_answer_and_confirm_buttons(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    fake_gemini(monkeypatch, [{"call": ("remember_fact", {"text": "I also take freelance work"})},
                              {"text": "Tayyor, tasdiqlang."}])
    telegram.process_update({"message": {"chat": {"id": 777}, "from": {"id": 777}, "text": "eslab qol: freelance ham olaman"}})
    methods = [m for m, _ in sent]
    assert "sendMessage" in methods and "editMessageText" in methods
    confirm_msg = next(p for m, p in sent if m == "sendMessage" and "reply_markup" in p and "inline_keyboard" in p["reply_markup"]
                       and p["reply_markup"]["inline_keyboard"][0][0]["callback_data"].startswith("aiact:ok"))
    action_id = int(confirm_msg["reply_markup"]["inline_keyboard"][0][0]["callback_data"].split(":")[-1])
    assert AiChat.objects.get(chat_id=777).history[-1]["role"] == "model"
    telegram.process_update({"callback_query": {"id": "1", "from": {"id": 777}, "data": f"aiact:ok:{action_id}",
                                                "message": {"chat": {"id": 777}, "message_id": 9, "text": "x"}}})
    assert AiKnowledge.objects.get().text == "I also take freelance work"
    assert AiAction.objects.get().status == "done"


@override_settings(**AI)
def test_telegram_commands(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    telegram.process_update({"message": {"chat": {"id": 777}, "from": {"id": 777}, "text": "/web"}})
    assert AiChat.objects.get(chat_id=777).mode == "web"
    telegram.process_update({"message": {"chat": {"id": 777}, "from": {"id": 777}, "text": "/lang ru"}})
    assert AiChat.objects.get(chat_id=777).lang == "ru"
    telegram.process_update({"message": {"chat": {"id": 777}, "from": {"id": 777}, "text": "/report"}})
    assert "Отчёт" in sent[-1][1]["text"]


# ── Digest ───────────────────────────────────────────────────────────────────

@override_settings(**AI)
def test_report_and_reminders(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    Lead.objects.create(name="Aziz", contact="+998901234567", need="Bot kerak")
    Reminder.objects.create(text="Ping client", due_at=timezone.now() - timezone.timedelta(minutes=1))
    rep = digest.build_report("today", "uz")
    assert rep["leads"] and "Aziz" in rep["text"]
    done = digest.tick(force="morning")
    assert done["reminders"] == 1 and done["digest"] == "morning"
    assert Reminder.objects.get().sent_at is not None
    assert AiLog.objects.filter(kind="digest").exists()
    assert any("Ping client" in p["text"] for k, p in sent if k == "notify")


# ── Telegram menu ────────────────────────────────────────────────────────────

def _owner_msg(text):
    return {"message": {"chat": {"id": 777}, "from": {"id": 777}, "text": text}}


def _press(data, mid=5):
    return {"callback_query": {"id": "1", "from": {"id": 777}, "data": data,
                               "message": {"chat": {"id": 777}, "message_id": mid, "text": "x"}}}


@override_settings(**AI)
def test_menu_keyboard_and_sections(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    telegram.process_update(_owner_msg("/start"))
    kb = sent[-1][1]["reply_markup"]["keyboard"]
    labels = [b["text"] for row in kb for b in row]
    assert "📥 So'rovlar" in labels and "⚙️ Sozlamalar" in labels and len(kb) == 5
    lead = Lead.objects.create(name="Aziz", contact="+998901234567", need="Restoran uchun bot kerak")
    telegram.process_update(_owner_msg("📥 So'rovlar"))
    assert "Aziz" in sent[-1][1]["text"] and not AiLog.objects.exists()   # menus never call the model
    telegram.process_update(_press(f"m:ls:{lead.pk}:contacted"))
    assert Lead.objects.get().status == "contacted"
    assert sent[-1][0] == "editMessageText"
    for label in ("📊 Hisobot", "✉️ Xabarlar", "📈 Statistika", "⏰ Eslatmalar", "🧠 Bilim"):
        telegram.process_update(_owner_msg(label))
        assert sent[-1][0] == "sendMessage" and "inline_keyboard" in sent[-1][1].get("reply_markup", {"inline_keyboard": 1})
    telegram.process_update(_press("m:st:30"))
    assert "30" in sent[-1][1]["text"]


@override_settings(**AI)
def test_menu_settings_toggle(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    telegram.process_update(_owner_msg("⚙️ Sozlamalar"))
    telegram.process_update(_press("m:dig"))
    assert AiChat.objects.get(chat_id=777).digest_on is False
    assert digest.send_digest("morning") is True and not any(k == "notify" for k, _ in sent)
    telegram.process_update(_press("m:lang:en"))
    assert AiChat.objects.get(chat_id=777).lang == "en"
    assert any("Report" in b["text"] for m, p in sent if m == "sendMessage" and "keyboard" in p.get("reply_markup", {})
               for row in p["reply_markup"]["keyboard"] for b in row)


@override_settings(**AI)
def test_lead_message_has_buttons_and_draft_goes_to_ai(db, monkeypatch):
    sent = fake_telegram(monkeypatch)
    fake_gemini(monkeypatch, [{"text": "Assalomu alaykum, Aziz!"}])
    from apps.ai.notify import lead_created
    lead = Lead.objects.create(name="Aziz", contact="aziz@mail.com", need="Bot", lang="uz")
    lead_created(lead)
    msg = next(p for m, p in sent if m == "sendMessage" and "Yangi so'rov" in p["text"])
    datas = [b["callback_data"] for row in msg["reply_markup"]["inline_keyboard"] for b in row]
    assert f"m:ldraft:{lead.pk}" in datas
    telegram.process_update(_press(f"m:ldraft:{lead.pk}"))
    assert AiLog.objects.get().role == "owner" and f"#{lead.pk}" in AiLog.objects.get().question
