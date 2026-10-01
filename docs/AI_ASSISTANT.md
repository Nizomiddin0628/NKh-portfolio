# AI assistent — sayt chati va Telegram kotib

`apps/ai` — bitta agent, ikkita eshik. Saytga kirgan **mehmon** o'ng pastki burchakdagi
oynada faqat o'qiydigan assistentni oladi; **ega** (saytda superuser sessiyasi yoki
`.env` dagi Telegram id) Telegram'da va saytda to'liq kotibga ega bo'ladi.
Rol promptda emas, kodda aniqlanadi (`views._role`, `telegram.is_owner`).

## Sozlash (`.env`)

| Kalit | Nima uchun |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio kaliti. Bo'sh bo'lsa assistent o'chiq (tugma "vaqtincha band" deydi). |
| `GEMINI_MODELS` | Ixtiyoriy. Modellar zanjiri, vergul bilan. 404/429/503 bo'lsa keyingisi sinaladi. |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Oldingi xabarnoma boti — assistent shu botda ishlaydi. |
| `TELEGRAM_WEBHOOK_SECRET` | Webhook sarlavhasi (`X-Telegram-Bot-Api-Secret-Token`). Bo'sh bo'lsa webhook 403 qaytaradi. |
| `AI_OWNER_TELEGRAM_ID` | Ixtiyoriy. Bo'sh bo'lsa `TELEGRAM_CHAT_ID`. |
| `AI_OWNER_LANG` | Telegram'dagi standart til: `uz` (standart), `ru`, `en`. |
| `AI_GUEST_HOURLY` / `AI_GUEST_DAILY` / `AI_DAILY_LIMIT` | Mehmon limitlari: 20/soat, 60/kun, hamma mehmonlar uchun 400/kun. |

Tekshirish: `python manage.py ai_check` (kalit, modellar, Telegram, limitlar; bitta kichik so'rov yuboradi),
`python manage.py ai_check --models` — kalitga ochiq modellar ro'yxati.

## Buyruqlar

| Buyruq | Qachon |
|---|---|
| `manage.py ai_check` | Sozlamani tekshirish. |
| `manage.py tg_poll` | Botni laptopda webhook'siz sinash (server webhook'i o'rnatilgan bo'lsa rad etadi). |
| `manage.py tg_setup [--url https://...]` | Webhook va bot buyruqlarini ro'yxatdan o'tkazish. `deploy.sh` har deploy'da chaqiradi. |
| `manage.py ai_tick [--digest morning\|evening]` | Eslatmalar va 08:30 / 18:00 hisobot. systemd timer 15 daqiqada bir chaqiradi (`deploy/portfolio-ai-tick.timer`). |
| `manage.py ai_projects` | Ikkita AI loyiha sahifasining matnlarini `apps/ai/content/projects.py` dan qayta yozish (rasmlar saqlanadi). |

## Qanday ishlaydi

1. **Prompt.** `prompts.SYSTEM` + rol qoidalari + `state.state(lang)` — bazadan 5 daqiqada bir yangilanadigan
   qisqa "hozirgi holat" (loyihalar, rezyume, sertifikatlar, bandlik, kontaktlar) + `AiKnowledge` faktlari.
   Ko'p savolga tool chaqirmasdan javob beriladi.
2. **Aylanish** (`agent.ask`): Gemini → function call → `tools.run` → natija modelga → ko'pi bilan 8 qadam.
   Modelning javobi (`thoughtSignature` bilan) o'zgartirilmasdan qaytariladi.
3. **Tool'lar** (`tools.py`): mehmonga `projects`, `project_detail`, `resume`, `site_info`, `search_knowledge`,
   `technologies`, `save_lead`. Egaga qo'shimcha: `leads`, `lead_detail`, `messages`, `stats`, `guest_questions`,
   `report`, `reminders`, `knowledge_list` va o'zgartiruvchi tool'lar: `update_settings`, `update_project`,
   `set_project_visibility`, `project_technologies`, `update_item`, `add_item`, `remove_item`, `update_lead`,
   `reply_lead`, `mark_messages_read`, `remember_fact`, `forget_fact`, `add_reminder`, `remove_reminder`.
   `project_detail` va `resume` qatorlarga `id` beradi — `update_item`/`add_item`/`remove_item` shu id bilan ishlaydi
   (section, metric, experience, bullet, education, skill_group, skill, language, award, certificate, principle).
4. **O'zgarishlar** (`actions.py`): o'zgartiruvchi tool `AiAction` yaratadi.
   - **Telegram (ega)** — standart holatda ⚡ *avto-tasdiq*: o'zgarish darhol bajariladi, xabar ostida
     ↩️ *Qaytarish* tugmasi (48 soat ichida, `actions.undo`). ⚙️ Sozlamalar → "Avto-tasdiqni almashtirish" bilan
     eski ✅/✖ tasdiq rejimiga qaytish mumkin (`AiChat.auto_confirm`). `reply_lead` (mijozga email) har doim tasdiq so'raydi.
   - **Sayt (superuser)** — avvalgidek tasdiq kartasi; 30 daqiqada eskiradi.
   - Tasdiqda/avto rejimda qayta tekshiriladi, bajariladi, `AiLog` ga yoziladi, "hozirgi holat" keshi tozalanadi.
   Kodda ruxsat etilgan maydonlar: sayt (headline, intro, about, availability_note, work_philosophy, meta_description,
   job_title, location, availability, full_name, email, phone, github_username), loyiha (tagline, role, summary,
   context, title, status, organisation, order, is_featured, live_url, repo_url, is_confidential, year_started,
   year_finished, team_size, technologies, ko'rsatish/yashirish), case-study bo'limlari va metrikalar, rezyume
   qatorlari (tajriba, bullet, ta'lim, ko'nikma guruhi/ko'nikma, til, mukofot, sertifikat), tamoyillar, lead
   holati/izohi, lead'ga email, xabarlarni o'qilgan qilish, fakt, eslatma. Foydalanuvchilar, parollar, kalitlar,
   domen va deploy — hech qachon.
5. **Lead** (`save_lead`): mehmon ehtiyoj + kontakt bersa → `Lead` + egaga Telegram xabar + suhbat matni.
6. **Bilim halqasi**: assistent javob topa olmagan savol `[[NOINFO]]` belgisi bilan `AiLog.unanswered=True`
   bo'ladi → kechki hisobotda ko'rinadi → Telegram'da "eslab qol: ..." → ✅ → `AiKnowledge`.
7. **Telegram menyu** (`tgmenu.py`): pastki klaviatura — 📊 Hisobot, 📥 So'rovlar, ✉️ Xabarlar, 📈 Statistika,
   ⏰ Eslatmalar, 🧠 Bilim, 🌐 Global, ⚙️ Sozlamalar, 🆕 Yangi suhbat, ⬇️ Yig'ish. Bo'limlar AI'siz, bitta xabarni
   inline tugmalar bilan tahrirlaydi (so'rov holati, xabarni o'qildi qilish, eslatma/faktni o'chirish, til, rejim,
   avto-tasdiq, hisobotni yoqish/o'chirish). "✍️ Javob tayyorla" AI'ga yuboradi. Yangi so'rov xabari tugmalar bilan keladi.
   Mehmonlar ham saytda 🎙 ovoz (≤3 MB) va 📎 rasm/PDF (≤8 MB) yubora oladi — soatlik limitga kiradi.
8. **Telegram** (`telegram.py`): webhook `/ai/tg/`. Faqat ega. Matn, ovoz (avval matnga o'giriladi), rasm
   (kichraytiriladi), PDF. Javob bitta xabarda ~1 s da bir tahrirlanadi, ⏹ tugmasi. Buyruqlar: `/new`, `/report`,
   `/leads`, `/web`, `/site`, `/lang`, `/menu`. Klaviatura yig'iladigan.
9. **Sayt oynasi**: `templates/ai/widget.html` (tugma inline uslub bilan), `static/ai/widget.css` va `widget.js`
   birinchi bosishda yoki 3 soniya bo'shlikdan keyin yuklanadi. Telefonda oyna `visualViewport` ga moslanadi:
   klaviatura ochilganda sarlavha va yozish maydoni ko'rinib turadi; birinchi ochilishda klaviatura o'zi chiqmaydi. NDJSON oqim, ⏹, tarix `sessionStorage` da,
   tayyor savollar, ega rejimida 📎 rasm/PDF, 🎙 ovoz, Sayt/Global rejim va tasdiq kartalari. `href="#ai"`
   havola yoki `data-ai-ask="savol"` atributi oynani ochadi.

## Server

- `gunicorn.conf.py`: `gthread`, 6 thread — streaming javob worker'ni bloklamasligi uchun. systemd unit'da
  `--worker-class` yoki `--threads` yozilgan bo'lsa, u ustun.
- Caddy `text/event-stream` ni buferlamaydi, qo'shimcha sozlama shart emas.
- `AiLog` 90 kundan keyin tozalanadi (`AI_LOG_RETENTION_DAYS`).

## Xavfsizlik

- Kalit va token faqat `.env` da; javobdagi token/kalit ko'rinishidagi satrlar `render.scrub` bilan o'chiriladi.
- Mehmon o'zgartiruvchi tool'larni ko'rmaydi ham, chaqira olmaydi ham (`tools.run` qayta tekshiradi).
- Fayllar ≤ 20 MB, faqat rasm/PDF/ovoz (`files.prepare`). Mehmon fayl yubora olmaydi.
- Barcha model matni `render.clean` dan o'tadi: faqat `<b>`, `<i>`, `<code>` va havolalar qoladi.

## Testlar

`pytest tests/test_ai.py` — Gemini va Telegram soxtalashtirilgan, tarmoq kerak emas.
