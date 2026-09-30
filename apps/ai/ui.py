"""Widget texts in the three site languages (no .po round-trip needed)."""

UI = {
    "en": {
        "open": "Ask AI", "title": "Assistant", "subtitle": "Nizomiddin's AI assistant",
        "owner": "Owner mode", "placeholder": "Type a question…", "send": "Send", "stop": "Stop",
        "new": "New chat", "close": "Close", "attach": "Image or PDF", "voice": "Voice question",
        "mode_site": "Site", "mode_web": "Global", "confirm": "Confirm", "cancel": "Cancel",
        "pending": "Waiting for your confirmation", "sources": "Sources", "recording": "Recording… tap to send",
        "cancel_rec": "Cancel", "thinking": "Thinking…", "retry": "Try again",
        "disabled": "The assistant is off at the moment. Use the contact form instead.",
        "offline": "No connection. Check the network and try again.",
        "contact": "Contact form", "note": "Answers are written by AI and may contain mistakes.",
        "done": "Done", "cancelled": "Cancelled", "failed": "Failed", "file_big": "The file is too large (max 8 MB).",
        "mic_denied": "Microphone access was denied.", "you": "You", "assistant": "Assistant",
    },
    "uz": {
        "open": "AI assistent", "title": "Assistent", "subtitle": "Nizomiddinning AI assistenti",
        "owner": "Ega rejimi", "placeholder": "Savol yozing…", "send": "Yuborish", "stop": "To'xtatish",
        "new": "Yangi suhbat", "close": "Yopish", "attach": "Rasm yoki PDF", "voice": "Ovozli savol",
        "mode_site": "Sayt", "mode_web": "Global", "confirm": "Tasdiqlash", "cancel": "Bekor",
        "pending": "Tasdiqingiz kutilmoqda", "sources": "Manbalar", "recording": "Yozilmoqda… yuborish uchun bosing",
        "cancel_rec": "Bekor", "thinking": "O'ylayapman…", "retry": "Qayta urinish",
        "disabled": "Assistent hozircha o'chiq. Kontakt formasidan yozing.",
        "offline": "Ulanish yo'q. Tarmoqni tekshirib, qayta urinib ko'ring.",
        "contact": "Kontakt formasi", "note": "Javoblarni AI yozadi, xatolik bo'lishi mumkin.",
        "done": "Bajarildi", "cancelled": "Bekor qilindi", "failed": "Bajarilmadi",
        "file_big": "Fayl juda katta (eng ko'pi 8 MB).", "mic_denied": "Mikrofonga ruxsat berilmadi.",
        "you": "Siz", "assistant": "Assistent",
    },
    "ru": {
        "open": "AI-ассистент", "title": "Ассистент", "subtitle": "AI-ассистент Низомиддина",
        "owner": "Режим владельца", "placeholder": "Напишите вопрос…", "send": "Отправить", "stop": "Остановить",
        "new": "Новый диалог", "close": "Закрыть", "attach": "Фото или PDF", "voice": "Голосовой вопрос",
        "mode_site": "Сайт", "mode_web": "Глобальный", "confirm": "Подтвердить", "cancel": "Отмена",
        "pending": "Ждёт вашего подтверждения", "sources": "Источники", "recording": "Запись… нажмите, чтобы отправить",
        "cancel_rec": "Отмена", "thinking": "Думаю…", "retry": "Повторить",
        "disabled": "Ассистент пока выключен. Напишите через форму контакта.",
        "offline": "Нет соединения. Проверьте сеть и попробуйте снова.",
        "contact": "Форма контакта", "note": "Ответы пишет AI, возможны ошибки.",
        "done": "Выполнено", "cancelled": "Отменено", "failed": "Не выполнено",
        "file_big": "Файл слишком большой (максимум 8 МБ).", "mic_denied": "Нет доступа к микрофону.",
        "you": "Вы", "assistant": "Ассистент",
    },
}


def texts(lang):
    return UI.get(lang) or UI["en"]
