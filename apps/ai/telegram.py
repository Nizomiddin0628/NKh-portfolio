"""Telegram side of the assistant (owner only).

The existing notification bot (TELEGRAM_BOT_TOKEN) gets a webhook:
    https://khalilovn.uz/ai/tg/   with X-Telegram-Bot-Api-Secret-Token = TELEGRAM_WEBHOOK_SECRET

Flow of a message: quick checks in the webhook request, then the Gemini call
runs in a thread while a placeholder "writing..." message is edited about
once a second with the streamed text. Changes proposed by the assistant are
sent as a separate message with [confirm] [cancel] buttons.
"""
import html
import json
import logging
import threading
import time
import urllib.error
import urllib.request
import uuid

from django.conf import settings
from django.core.cache import cache
from django.db import connection, transaction
from django.utils import timezone

from . import actions, agent, gemini
from .actions import ActionError
from .files import prepare
from .gemini import AiError
from .models import AiChat, AiLog
from .render import split_telegram

logger = logging.getLogger(__name__)

API = "https://api.telegram.org/bot{token}/{method}"
FILE = "https://api.telegram.org/file/bot{token}/{path}"
EDIT_EVERY = 1.1
BUSY_TIMEOUT = 240
MAX_FILE = 20 * 1024 * 1024
LANG_NAMES = {"uz": "O'zbekcha", "ru": "Русский", "en": "English"}

T = {
    "uz": {
        "start": "Salom, Nizomiddin! Men sizning AI assistentingizman. Yozing yoki gapiring: so'rovlar, "
                 "xabarlar, statistika, sayt matnlari, eslatmalar. Rasm yoki PDF yuborsangiz — o'qib beraman. "
                 "Har qanday o'zgarish faqat siz tasdiqlagandan keyin bajariladi.",
        "help": "Pastdagi menyu bo'limlari: 📊 Hisobot, 📥 So'rovlar, ✉️ Xabarlar, 📈 Statistika, ⏰ Eslatmalar, "
                "🧠 Bilim, ⚙️ Sozlamalar.\nIstalgan narsani oddiy yozing yoki ovozli xabar yuboring — AI bajaradi.\n"
                "Buyruqlar: /menu /report /leads /messages /stats /reminders /knowledge /settings /web /site /new",
        "menu": "Menyu ochildi.", "hide": "Menyu yig'ildi. Qayta ochish: /menu",
        "new": "Yangi suhbat boshlandi.", "busy": "⏳ Oldingi javob tayyorlanmoqda. Kuting yoki ⏹ bosing.",
        "writing": "✍️ Yozyapman…", "stop": "⏹ To'xtatish", "stopped": "⏹ To'xtatildi.",
        "heard": "\U0001f5e3 «{text}»", "web_on": "\U0001f310 Global rejim: internet qidiruvi yoqildi.",
        "web_off": "\U0001f3e0 Sayt rejimi: faqat sayt ma'lumotlari.", "lang_set": "Til: {name}",
        "lang_ask": "Tilni tanlang:", "confirm": "Tasdiqlaysizmi?", "yes": "✅ Tasdiqlash", "no": "✖️ Bekor",
        "done": "✅ Bajarildi: {result}", "cancelled": "✖️ Bekor qilindi.", "failed": "⚠️ Bajarilmadi: {result}",
        "expired": "⌛ Muddati o'tdi, qaytadan so'rang.", "no_leads": "Yangi so'rovlar yo'q.",
        "guest": "Bu bot faqat sayt egasi uchun. Sayt: https://khalilovn.uz", "file_bad": "Bu faylni o'qiy olmadim: {why}",
        "too_long": "Ovozli xabar juda uzun (3 daqiqadan ko'p).",
        "placeholder": "Savol yozing yoki \U0001f399 gapiring…",
    },
    "ru": {
        "start": "Здравствуйте, Низомиддин! Я ваш AI-ассистент. Пишите или говорите: заявки, сообщения, "
                 "статистика, тексты сайта, напоминания. Пришлите фото или PDF — прочитаю. "
                 "Любое изменение выполняется только после вашего подтверждения.",
        "help": "Разделы меню внизу: 📊 Отчёт, 📥 Заявки, ✉️ Сообщения, 📈 Статистика, ⏰ Напоминания, "
                "🧠 Знания, ⚙️ Настройки.\nЛюбую задачу просто напишите или скажите голосом — AI выполнит.\n"
                "Команды: /menu /report /leads /messages /stats /reminders /knowledge /settings /web /site /new",
        "menu": "Меню открыто.", "hide": "Меню скрыто. Открыть снова: /menu",
        "new": "Новый диалог начат.", "busy": "⏳ Предыдущий ответ ещё готовится. Подождите или нажмите ⏹.",
        "writing": "✍️ Пишу…", "stop": "⏹ Остановить", "stopped": "⏹ Остановлено.",
        "heard": "\U0001f5e3 «{text}»", "web_on": "\U0001f310 Глобальный режим: поиск в интернете включён.",
        "web_off": "\U0001f3e0 Режим сайта: только данные сайта.", "lang_set": "Язык: {name}",
        "lang_ask": "Выберите язык:", "confirm": "Подтвердить?", "yes": "✅ Подтвердить", "no": "✖️ Отмена",
        "done": "✅ Выполнено: {result}", "cancelled": "✖️ Отменено.", "failed": "⚠️ Не выполнено: {result}",
        "expired": "⌛ Срок истёк, попросите снова.", "no_leads": "Новых заявок нет.",
        "guest": "Этот бот только для владельца сайта. Сайт: https://khalilovn.uz", "file_bad": "Не смог прочитать файл: {why}",
        "too_long": "Голосовое сообщение слишком длинное (более 3 минут).",
        "placeholder": "Напишите вопрос или \U0001f399 говорите…",
    },
    "en": {
        "start": "Hi Nizomiddin! I'm your AI assistant. Type or talk: leads, messages, stats, site texts, "
                 "reminders. Send a photo or PDF and I'll read it. Every change runs only after you confirm it.",
        "help": "Menu sections below: 📊 Report, 📥 Leads, ✉️ Messages, 📈 Stats, ⏰ Reminders, 🧠 Knowledge, "
                "⚙️ Settings.\nFor anything else just type or send a voice note — the AI does it.\n"
                "Commands: /menu /report /leads /messages /stats /reminders /knowledge /settings /web /site /new",
        "menu": "Menu opened.", "hide": "Menu hidden. Open again: /menu",
        "new": "New conversation started.", "busy": "⏳ The previous answer is still being written. Wait or press ⏹.",
        "writing": "✍️ Writing…", "stop": "⏹ Stop", "stopped": "⏹ Stopped.",
        "heard": "\U0001f5e3 “{text}”", "web_on": "\U0001f310 Global mode: web search on.",
        "web_off": "\U0001f3e0 Site mode: site data only.", "lang_set": "Language: {name}",
        "lang_ask": "Choose a language:", "confirm": "Confirm?", "yes": "✅ Confirm", "no": "✖️ Cancel",
        "done": "✅ Done: {result}", "cancelled": "✖️ Cancelled.", "failed": "⚠️ Failed: {result}",
        "expired": "⌛ Expired, ask again.", "no_leads": "No new leads.",
        "guest": "This bot is for the site owner only. Site: https://khalilovn.uz", "file_bad": "Could not read the file: {why}",
        "too_long": "The voice message is too long (over 3 minutes).",
        "placeholder": "Type a question or \U0001f399 talk…",
    },
}


def t(lang):
    return T.get(lang) or T["uz"]


# ── Low-level API ───────────────────────────────────────────────────────────

def token():
    return (getattr(settings, "TELEGRAM_BOT_TOKEN", "") or "").strip()


def call(method, _timeout=15, **payload):
    """Call the Bot API; returns the `result` or None (never raises)."""
    tok = token()
    if not tok:
        return None
    req = urllib.request.Request(API.format(token=tok, method=method), data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=_timeout) as resp:
            data = json.loads(resp.read().decode())
            return data.get("result") if data.get("ok") else None
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode()[:200]
        except Exception:
            pass
        if exc.code == 429:
            time.sleep(1.5)
        if "message is not modified" not in body:
            logger.warning("telegram %s -> %s %s", method, exc.code, body)
        return None
    except Exception as exc:
        logger.warning("telegram %s failed: %s", method, exc)
        return None


def send(chat_id, text, **kw):
    kw.setdefault("parse_mode", "HTML")
    kw.setdefault("disable_web_page_preview", True)
    return call("sendMessage", chat_id=chat_id, text=text, **kw)


def edit(chat_id, message_id, text, **kw):
    kw.setdefault("parse_mode", "HTML")
    kw.setdefault("disable_web_page_preview", True)
    return call("editMessageText", chat_id=chat_id, message_id=message_id, text=text, **kw)


def download(file_id):
    info = call("getFile", file_id=file_id)
    if not info or not info.get("file_path"):
        return None
    if int(info.get("file_size") or 0) > MAX_FILE:
        return None
    url = FILE.format(token=token(), path=info["file_path"])
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            return resp.read(MAX_FILE + 1)[:MAX_FILE]
    except Exception as exc:
        logger.warning("telegram download failed: %s", exc)
        return None


def owner_id():
    raw = (getattr(settings, "AI_OWNER_TELEGRAM_ID", "") or getattr(settings, "TELEGRAM_CHAT_ID", "") or "").strip()
    try:
        return int(raw)
    except ValueError:
        return None


def is_owner(chat_id):
    oid = owner_id()
    return oid is not None and int(chat_id) == oid


def keyboard(lang, mode="local"):
    from .tgmenu import keyboard as menu_keyboard
    kb = menu_keyboard(lang, mode)
    kb["input_field_placeholder"] = t(lang)["placeholder"]
    return kb


def show(chat_id, text, kb=None, message_id=None):
    markup = {"inline_keyboard": kb} if kb else None
    kw = {"reply_markup": markup} if markup else {}
    if message_id and edit(chat_id, message_id, text, **kw):
        return
    send(chat_id, text, **kw)


def stop_markup(lang, run):
    return {"inline_keyboard": [[{"text": t(lang)["stop"], "callback_data": f"aistop:{run}"}]]}


def confirm_markup(lang, action_id):
    return {"inline_keyboard": [[{"text": t(lang)["yes"], "callback_data": f"aiact:ok:{action_id}"},
                                 {"text": t(lang)["no"], "callback_data": f"aiact:no:{action_id}"}]]}


# ── Update handling ─────────────────────────────────────────────────────────

def process_update(update):
    if "callback_query" in update:
        return handle_callback(update["callback_query"])
    msg = update.get("message") or update.get("edited_message")
    if msg:
        return handle_message(msg)


def _chat(chat_id):
    chat, _ = AiChat.objects.get_or_create(chat_id=chat_id, defaults={"lang": getattr(settings, "AI_OWNER_LANG", "uz")})
    if chat.state == "busy" and chat.busy_since and (timezone.now() - chat.busy_since).total_seconds() > BUSY_TIMEOUT:
        chat.state, chat.run = "idle", ""
        chat.save(update_fields=["state", "run"])
    return chat


def handle_callback(cb):
    data = cb.get("data") or ""
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    user_id = cb.get("from", {}).get("id")
    call("answerCallbackQuery", callback_query_id=cb.get("id"))
    if chat_id is None or not is_owner(user_id):
        return
    chat = _chat(chat_id)
    if data.startswith("m:"):
        from . import tgmenu
        mid = cb.get("message", {}).get("message_id")
        res = tgmenu.on_callback(chat, data)
        if not res:
            return
        if res[0] == "edit":
            show(chat_id, res[1], res[2], mid)
        elif res[0] == "keyboard":        # language or mode changed: refresh the bottom keyboard too
            show(chat_id, res[1], res[2], mid)
            send(chat_id, t(chat.lang)["menu"], reply_markup=keyboard(chat.lang, chat.mode))
        elif res[0] == "ai":
            run_ai(chat, res[1], [], "ask")
        return
    if data.startswith("aistop:"):
        run = data.split(":", 1)[1]
        AiChat.objects.filter(pk=chat.pk, run=run).update(run="")
        return
    if data.startswith("ailang:"):
        code = data.split(":", 1)[1]
        if code in LANG_NAMES:
            chat.lang = code
            chat.save(update_fields=["lang"])
            send(chat_id, t(code)["lang_set"].format(name=LANG_NAMES[code]), reply_markup=keyboard(code, chat.mode))
        return
    if data.startswith("aiact:"):
        _, verb, action_id = data.split(":", 2)
        try:
            if verb == "ok":
                actions.confirm(int(action_id), channel="telegram")
            else:
                actions.cancel(int(action_id), channel="telegram")
        except ActionError as exc:
            mid = cb.get("message", {}).get("message_id")
            if mid:
                edit(chat_id, mid, f"{cb['message'].get('text', '')}\n\n⚠️ {html.escape(str(exc))}")
        return


def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    if chat_id is None:
        return
    if not is_owner(msg.get("from", {}).get("id", chat_id)):
        key = f"ai:tgguest:{chat_id}"
        if not cache.get(key):
            cache.set(key, 1, 3600)
            send(chat_id, T["uz"]["guest"] + "\n" + T["en"]["guest"])
        return

    chat = _chat(chat_id)
    tt = t(chat.lang)
    text = (msg.get("text") or msg.get("caption") or "").strip()

    # Commands and menu buttons never go through the model
    from . import tgmenu
    cmd = text.split("@")[0].split(" ")[0].lower() if text.startswith("/") else ""
    if cmd == "/start" or cmd == "/help":
        send(chat_id, tt["start"] if cmd == "/start" else tt["help"], reply_markup=keyboard(chat.lang, chat.mode))
        return
    if cmd == "/menu":
        send(chat_id, tt["menu"], reply_markup=keyboard(chat.lang, chat.mode))
        return
    if cmd == "/lang":
        code = text.split(" ", 1)[1].strip().lower() if " " in text else ""
        if code in LANG_NAMES:
            chat.lang = code
            chat.save(update_fields=["lang"])
            send(chat_id, t(code)["lang_set"].format(name=LANG_NAMES[code]), reply_markup=keyboard(code, chat.mode))
        else:
            show(chat_id, *tgmenu.settings_view(chat))
        return
    action = tgmenu.BUTTONS.get(text) or tgmenu.COMMANDS.get(cmd)
    if action == "hide":
        send(chat_id, tt["hide"], reply_markup={"remove_keyboard": True})
        return
    if action == "new":
        chat.history = []
        chat.save(update_fields=["history"])
        send(chat_id, tt["new"], reply_markup=keyboard(chat.lang, chat.mode))
        return
    if action in ("web", "site"):
        chat.mode = "web" if action == "web" else "local"
        chat.save(update_fields=["mode"])
        send(chat_id, tt["web_on"] if action == "web" else tt["web_off"], reply_markup=keyboard(chat.lang, chat.mode))
        return
    if action in tgmenu.SECTIONS:
        show(chat_id, *tgmenu.SECTIONS[action](chat))
        return

    # Content for the model
    attachments, kind, question = [], "ask", text
    if msg.get("voice") or msg.get("audio"):
        media = msg.get("voice") or msg.get("audio")
        if int(media.get("duration") or 0) > 180:
            send(chat_id, tt["too_long"])
            return
        raw = download(media.get("file_id"))
        if not raw:
            send(chat_id, tt["file_bad"].format(why="download"))
            return
        try:
            heard = gemini.transcribe(raw, media.get("mime_type") or "audio/ogg")
        except AiError as exc:
            send(chat_id, _error(exc.code, chat.lang))
            return
        if not heard:
            send(chat_id, tt["file_bad"].format(why="silence"))
            return
        send(chat_id, tt["heard"].format(text=html.escape(heard[:900])))
        question, kind = (f"{text}\n{heard}" if text else heard), "voice"
    elif msg.get("photo") or msg.get("document"):
        if msg.get("photo"):
            file_id, hint = msg["photo"][-1].get("file_id"), "image/jpeg"
        else:
            file_id, hint = msg["document"].get("file_id"), msg["document"].get("mime_type") or ""
        raw = download(file_id)
        if not raw:
            send(chat_id, tt["file_bad"].format(why="download"))
            return
        try:
            part, _ftype = prepare(raw, hint)
        except AiError as exc:
            send(chat_id, tt["file_bad"].format(why=html.escape(exc.detail)))
            return
        attachments, kind = [part], "file"
    if not question and not attachments:
        return
    run_ai(chat, question, attachments, kind)


def _error(code, lang):
    from .prompts import error_text
    return "⚠️ " + error_text(code, lang)


# ── Running the model with a live-edited message ────────────────────────────

def run_ai(chat, question, attachments, kind):
    tt = t(chat.lang)
    run = uuid.uuid4().hex
    with transaction.atomic():
        fresh = AiChat.objects.select_for_update().get(pk=chat.pk)
        if fresh.state == "busy" and fresh.busy_since and \
                (timezone.now() - fresh.busy_since).total_seconds() < BUSY_TIMEOUT:
            send(chat.chat_id, tt["busy"])
            return
        fresh.state, fresh.run, fresh.busy_since = "busy", run, timezone.now()
        fresh.save(update_fields=["state", "run", "busy_since"])
    call("sendChatAction", chat_id=chat.chat_id, action="typing")
    placeholder = send(chat.chat_id, tt["writing"], reply_markup=stop_markup(chat.lang, run))
    mid = placeholder.get("message_id") if placeholder else None
    args = (chat.pk, run, question, attachments, kind, mid)
    if getattr(settings, "AI_RUN_ASYNC", True):
        threading.Thread(target=_run, args=args, daemon=True).start()
    else:
        _run(*args)


def _run(chat_pk, run, question, attachments, kind, mid):
    chat = AiChat.objects.get(pk=chat_pk)
    tt = t(chat.lang)
    chat_id = chat.chat_id
    buf, last_edit, last_check = [], time.time(), {"t": 0.0, "stop": False}

    def stop():
        now = time.time()
        if now - last_check["t"] > 1.0:
            last_check["t"] = now
            last_check["stop"] = not AiChat.objects.filter(pk=chat_pk, run=run).exists()
        return last_check["stop"]

    def on_text(delta):
        nonlocal last_edit
        if delta is None:
            buf.clear()
            return
        buf.append(delta)
        if mid and time.time() - last_edit > EDIT_EVERY:
            last_edit = time.time()
            draft = html.escape("".join(buf))[-3800:]
            edit(chat_id, mid, draft + " ▍", reply_markup=stop_markup(chat.lang, run))

    try:
        res = agent.ask(role="owner", channel="telegram", lang=chat.lang, question=question,
                        history=chat.history, attachments=attachments, mode=chat.mode,
                        chat_id=chat_id, kind=kind, on_text=on_text, stop=stop)
        if not res.get("ok"):
            if res.get("code") == "stopped":
                text = f"{tt['stopped']}\n<code>{html.escape(question[:1000])}</code>" if question else tt["stopped"]
            else:
                text = _error(res.get("code", "generic"), chat.lang)
            if mid:
                edit(chat_id, mid, text)
            else:
                send(chat_id, text)
            return
        answer = res["answer"]
        if res.get("sources"):
            answer += "\n\n" + "\n".join(f'• <a href="{html.escape(s["url"], quote=True)}">{html.escape(s["title"])}</a>'
                                        for s in res["sources"])
        chunks = split_telegram(answer)
        if mid:
            if not edit(chat_id, mid, chunks[0]):
                send(chat_id, chunks[0])
        else:
            send(chat_id, chunks[0])
        for extra in chunks[1:]:
            send(chat_id, extra)
        for a in res.get("actions", []):
            ask_confirmation(chat_id, chat.lang, a["id"], a["summary"])
        hist = (chat.history or []) + [{"role": "user", "text": question[:2000]},
                                       {"role": "model", "text": res["text"][:2000]}]
        AiChat.objects.filter(pk=chat_pk).update(history=hist[-16:])
    except Exception:
        logger.exception("telegram run failed")
        if mid:
            edit(chat_id, mid, _error("generic", chat.lang))
    finally:
        AiChat.objects.filter(pk=chat_pk).update(state="idle", run="", busy_since=None)
        connection.close()


def ask_confirmation(chat_id, lang, action_id, summary):
    msg = send(chat_id, f"❓ <b>{t(lang)['confirm']}</b>\n{html.escape(summary)}",
               reply_markup=confirm_markup(lang, action_id))
    if msg:
        from .models import AiAction
        AiAction.objects.filter(pk=action_id).update(tg_msgs=[[chat_id, msg.get("message_id")]])


def update_action_messages(action):
    """Rewrite the confirmation message(s) after a decision was made anywhere."""
    lang = getattr(settings, "AI_OWNER_LANG", "uz")
    for chat_id, mid in action.tg_msgs or []:
        chat = AiChat.objects.filter(chat_id=chat_id).first()
        tt = t(chat.lang if chat else lang)
        if action.status == "done":
            tail = tt["done"].format(result=html.escape(action.result))
        elif action.status == "cancelled":
            tail = tt["cancelled"]
        elif action.status == "expired":
            tail = tt["expired"]
        else:
            tail = tt["failed"].format(result=html.escape(action.result))
        edit(chat_id, mid, f"{html.escape(action.summary)}\n\n{tail}")


# ── One-time setup (manage.py tg_setup) ─────────────────────────────────────

COMMAND_LIST = [
    {"command": "menu", "description": "Menyu / Menu"},
    {"command": "report", "description": "Hisobot / Report"},
    {"command": "leads", "description": "So'rovlar / Leads"},
    {"command": "messages", "description": "Xabarlar / Messages"},
    {"command": "stats", "description": "Statistika / Stats"},
    {"command": "reminders", "description": "Eslatmalar / Reminders"},
    {"command": "knowledge", "description": "Bilim / Knowledge"},
    {"command": "settings", "description": "Sozlamalar / Settings"},
    {"command": "web", "description": "Global rejim / Web search"},
    {"command": "site", "description": "Sayt rejimi / Site only"},
    {"command": "new", "description": "Yangi suhbat / New chat"},
    {"command": "help", "description": "Yordam / Help"},
]

def setup(base_url):
    secret = (getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "") or "").strip()
    if not token():
        return "TELEGRAM_BOT_TOKEN is empty"
    if not secret:
        return "TELEGRAM_WEBHOOK_SECRET is empty"
    ok = call("setWebhook", url=f"{base_url.rstrip('/')}/ai/tg/", secret_token=secret,
              allowed_updates=["message", "edited_message", "callback_query"], drop_pending_updates=True)
    call("setMyCommands", commands=COMMAND_LIST)
    call("setChatMenuButton", menu_button={"type": "commands"})
    info = call("getWebhookInfo") or {}
    return f"webhook: {info.get('url', '?')} (set={'ok' if ok else 'failed'}, pending={info.get('pending_update_count', '?')})"


def log_system(text):
    AiLog.objects.create(channel="system", role="owner", kind="ask", question=text[:200], model="-")
