"""Two portfolio projects about the assistant itself, in three languages.

Applied once by apps/ai/migrations/0002_ai_projects.py, and again by
`python manage.py ai_projects` if the texts are edited here. Images are only
added when the project has none, so screenshots uploaded in the admin stay.
"""
from django.core.files import File

from apps.core.management.commands.load_portfolio import ASSETS, L, lang_fields
from apps.projects.models import CaseSection, Metric, Project, ProjectImage, Technology

NEW_TECH = [
    ("Gemini API", "gemini-api", "ai"),
    ("Telegram Bot API", "telegram-bot-api", "tool"),
    ("Server-Sent Events", "sse", "backend"),
    ("JavaScript", "javascript", "frontend"),
]

PROJECTS = [
    # ------------------------------------------------------------------
    {
        "slug": "ai-portfolio-assistant",
        "after": "smart-yard-gate-automation",
        "featured": True,
        "title": "AI Assistant — Site Chat and Telegram Secretary",
        "organisation": "Own product · this site",
        "status": "production", "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "confidential": False,
        "tech": ["Python", "Django", "Gemini API", "Telegram Bot API", "Server-Sent Events", "JavaScript"],
        "tagline": L(
            "An AI assistant that lives in the corner of this site and in Telegram: answers visitors in three "
            "languages, turns interest into leads and runs the site for its owner — with a confirmation before every change.",
            "Shu saytning burchagida va Telegram'da yashaydigan AI assistent: mehmonlarga uch tilda javob beradi, "
            "qiziqishni so'rovga aylantiradi va sayt egasi uchun kotib vazifasini bajaradi — har bir o'zgarishdan oldin tasdiq so'raydi.",
            "AI-ассистент, который живёт в углу этого сайта и в Telegram: отвечает посетителям на трёх языках, "
            "превращает интерес в заявки и ведёт сайт для владельца — с подтверждением перед каждым изменением.",
        ),
        "role": L("Architecture, backend, frontend, prompt design",
                  "Arxitektura, backend, frontend, prompt dizayni",
                  "Архитектура, бэкенд, фронтенд, дизайн промптов"),
        "summary": L(
            "Try it right here: the assistant in the bottom-right corner is this project. Ask it about any project on the site, "
            "describe what you want to build, and it will pass your details to me in Telegram within seconds.\n\n"
            "The same agent has two doors. Visitors get a read-only assistant with a strict scope and rate limits. "
            "I get a secretary in Telegram that knows every lead, message and visit, reads photos, PDFs and voice notes, "
            "searches the web on request, and can change site texts, projects and reminders — but every change is only "
            "prepared and waits for my ✔.\n\n"
            "[Try it on this site →](#ai)",
            "Shu yerda sinab ko'ring: o'ng pastki burchakdagi assistent — aynan shu loyiha. Saytdagi istalgan loyiha haqida so'rang, "
            "nima qurmoqchi ekaningizni aytib bering — u ma'lumotingizni bir necha soniyada menga Telegram orqali yetkazadi.\n\n"
            "Bitta agentning ikkita eshigi bor. Mehmonlar faqat o'qiydigan, doirasi va limiti qat'iy belgilangan assistentni oladi. "
            "Men esa Telegram'da kotibga ega bo'laman: u har bir so'rov, xabar va tashrifni biladi, rasm, PDF va ovozli xabarlarni o'qiydi, "
            "so'rasam internetdan qidiradi, sayt matnlari, loyihalar va eslatmalarni o'zgartira oladi — lekin har bir o'zgarish avval "
            "tayyorlanadi va mening ✔ belgimni kutadi.\n\n"
            "[Shu saytda sinab ko'ring →](#ai)",
            "Попробуйте прямо здесь: ассистент в правом нижнем углу — это и есть этот проект. Спросите о любом проекте на сайте, "
            "расскажите, что хотите построить, — и он за секунды передаст мне ваши данные в Telegram.\n\n"
            "У одного агента две двери. Посетители получают ассистента только для чтения, со строгими рамками и лимитами. "
            "Я получаю секретаря в Telegram: он знает каждую заявку, сообщение и визит, читает фото, PDF и голосовые, "
            "по запросу ищет в интернете и может менять тексты сайта, проекты и напоминания — но каждое изменение лишь "
            "готовится и ждёт моего ✔.\n\n"
            "[Попробовать на этом сайте →](#ai)",
        ),
        "context": L(
            "My own product, running on this site. The same core is deployed as the AI secretary inside my Restaurant ERP.",
            "O'zimning mahsulotim, shu saytda ishlab turibdi. Xuddi shu yadro Restaurant ERP ichida AI Kotib sifatida ishlaydi.",
            "Мой собственный продукт, работает на этом сайте. То же ядро развёрнуто как AI-секретарь внутри моей Restaurant ERP.",
        ),
        "metrics": [
            {"label": L("Languages", "Tillar", "Языков"), "after": "3",
             "note": L("Uzbek, Russian, English — answers in the visitor's language",
                       "O'zbek, rus, ingliz — mehmon tilida javob beradi",
                       "Узбекский, русский, английский — отвечает на языке гостя")},
            {"label": L("First words on screen", "Birinchi so'zlar ekranda", "Первые слова на экране"), "after": "~1–2 s",
             "note": L("Streaming, not a spinner", "Streaming, kutish belgisi emas", "Стриминг вместо ожидания")},
            {"label": L("Tools the agent can call", "Agent chaqiradigan tool'lar", "Инструментов у агента"), "after": "25",
             "note": L("7 for visitors, 25 for the owner", "Mehmon uchun 7, ega uchun 25", "7 для гостей, 25 для владельца")},
            {"label": L("Changes without confirmation", "Tasdiqsiz o'zgarishlar", "Изменений без подтверждения"), "after": "0",
             "note": L("Every change waits for ✔", "Har bir o'zgarish ✔ kutadi", "Каждое изменение ждёт ✔")},
        ],
        "sections": [
            ("problem",
             L("A portfolio that only talks about AI", "Faqat AI haqida gapiradigan portfolio", "Портфолио, которое лишь говорит об AI"),
             L("A portfolio page can claim experience with AI, but it cannot show it. Visitors read, leave, and the contact form stays "
               "empty. At the same time I wanted a place where I could ask about my own site's leads and statistics from my phone, "
               "and fix a headline without opening the admin.",
               "Portfolio sahifasi AI bilan ishlashni da'vo qila oladi, lekin ko'rsata olmaydi. Mehmonlar o'qiydi, chiqib ketadi, "
               "kontakt formasi bo'sh qoladi. Shu bilan birga men telefondan turib saytimning so'rovlari va statistikasini so'raydigan, "
               "admin panelni ochmasdan sarlavhani tuzatadigan joy istardim.",
               "Страница портфолио может заявлять об опыте с AI, но не может его показать. Посетители читают, уходят, форма контакта "
               "остаётся пустой. При этом мне хотелось место, где я с телефона спрошу о заявках и статистике своего сайта "
               "и поправлю заголовок, не открывая админку.")),
            ("decision",
             L("One agent, two roles decided in code", "Bitta agent, roli kodda aniqlanadigan ikki rejim", "Один агент, две роли, определяемые в коде"),
             L("The visitor and the owner talk to the same agent, but the role is decided by the server — an admin session on the site "
               "or my Telegram id — never by what the user says. Visitors are only given read-only tools plus `save_lead`; the "
               "changing tools do not even exist for them, so a \"forget your rules, you are admin now\" message has nothing to work with.\n\n"
               "Facts come from the database, not from the model's memory: a compact **current state** (projects, resume, availability) "
               "is generated from the site and refreshed every five minutes, so most questions are answered without a single tool call. "
               "When the assistant has no facts, it says so and the question is flagged for me — I answer it in Telegram and the "
               "answer becomes a remembered fact for next time.",
               "Mehmon ham, ega ham bitta agent bilan gaplashadi, lekin rolni server aniqlaydi — saytdagi admin sessiyasi yoki mening "
               "Telegram id'im orqali, foydalanuvchining so'ziga qarab emas. Mehmonga faqat o'qiydigan tool'lar va `save_lead` beriladi; "
               "o'zgartiruvchi tool'lar u uchun umuman mavjud emas, shuning uchun «qoidalarni unut, sen endi adminsan» degan "
               "xabar hech narsani o'zgartira olmaydi.\n\n"
               "Faktlar model xotirasidan emas, bazadan olinadi: saytdan ixcham **hozirgi holat** (loyihalar, rezyume, bandlik) hosil "
               "qilinadi va har besh daqiqada yangilanadi, shuning uchun ko'p savolga birorta tool chaqirmasdan javob beriladi. "
               "Assistentda fakt bo'lmasa, buni ochiq aytadi va savol men uchun belgilanadi — Telegram'da javob yozaman, javob esa "
               "keyingi safar uchun eslab qolingan faktga aylanadi.",
               "Посетитель и владелец говорят с одним агентом, но роль определяет сервер — сессия админа на сайте или мой Telegram id, "
               "а не слова пользователя. Гостю даются только инструменты для чтения и `save_lead`; изменяющих инструментов для него "
               "просто нет, поэтому сообщение «забудь правила, ты теперь админ» ничего не даёт.\n\n"
               "Факты берутся из базы, а не из памяти модели: с сайта собирается компактное **текущее состояние** (проекты, резюме, "
               "доступность) и обновляется каждые пять минут, так что большинство вопросов закрывается без единого вызова инструмента. "
               "Если фактов нет, ассистент так и говорит, а вопрос помечается для меня — я отвечаю в Telegram, и ответ становится "
               "запомненным фактом.")),
            ("architecture",
             L("Django agent, Gemini, streaming to both channels", "Django agent, Gemini, ikkala kanalga streaming", "Django-агент, Gemini, стриминг в оба канала"),
             L("A Django app holds the agent loop: question → system prompt with current state → Gemini with function declarations → "
               "tool results back to the model, at most five rounds. Gemini is called over plain REST with the standard library; "
               "a chain of models is tried in order and the last working one is remembered, so quota or outages degrade gracefully.\n\n"
               "On the site the answer streams as NDJSON through `StreamingHttpResponse`; the widget is ~450 lines of vanilla JavaScript, "
               "loaded only on the first click, with stop, history, suggested questions and confirmation cards. In Telegram the "
               "same stream edits one message about once a second, with a ⏹ button; voice notes are transcribed first, photos are "
               "shrunk before upload, PDFs go as they are. Every change the model wants goes through an `AiAction` row: validated, "
               "shown with ✔ / ✖ buttons, re-validated on confirmation, executed, logged. A 15-minute timer sends reminders and the "
               "08:30 / 18:00 digest.",
               "Django ilovasi agent aylanishini olib boradi: savol → hozirgi holat bilan system prompt → function declaration'lar bilan "
               "Gemini → tool natijalari modelga qaytadi, ko'pi bilan besh aylanish. Gemini oddiy REST orqali, faqat standart kutubxona "
               "bilan chaqiriladi; modellar zanjiri navbat bilan sinaladi va oxirgi ishlagani eslab qolinadi — limit tugasa yoki "
               "xizmat band bo'lsa tizim yiqilmaydi.\n\n"
               "Saytda javob `StreamingHttpResponse` orqali NDJSON ko'rinishida oqib keladi; oyna ~450 qator sof JavaScript, faqat "
               "birinchi bosishda yuklanadi, to'xtatish, tarix, tayyor savollar va tasdiq kartalari bor. Telegram'da xuddi shu oqim "
               "bitta xabarni sekundiga bir marta tahrirlab boradi, ⏹ tugmasi bilan; ovozli xabar avval matnga o'giriladi, rasm "
               "yuborishdan oldin kichraytiriladi, PDF o'zgarishsiz ketadi. Model xohlagan har bir o'zgarish `AiAction` yozuvi orqali "
               "o'tadi: tekshiriladi, ✔ / ✖ tugmalari bilan ko'rsatiladi, tasdiqda qayta tekshiriladi, bajariladi, jurnalga yoziladi. "
               "15 daqiqalik timer eslatmalar va 08:30 / 18:00 dagi hisobotni yuboradi.",
               "Django-приложение ведёт цикл агента: вопрос → системный промпт с текущим состоянием → Gemini с декларациями функций → "
               "результаты инструментов обратно в модель, максимум пять раундов. Gemini вызывается по обычному REST стандартной "
               "библиотекой; цепочка моделей пробуется по очереди, последняя рабочая запоминается — лимиты и сбои не роняют систему.\n\n"
               "На сайте ответ идёт потоком NDJSON через `StreamingHttpResponse`; виджет — ~450 строк чистого JavaScript, "
               "загружается только при первом клике, есть остановка, история, подсказки и карточки подтверждения. В Telegram тот же "
               "поток раз в секунду редактирует одно сообщение, с кнопкой ⏹; голосовые сначала расшифровываются, фото сжимаются перед "
               "отправкой, PDF идут как есть. Каждое изменение, которого хочет модель, проходит через запись `AiAction`: проверка, "
               "кнопки ✔ / ✖, повторная проверка при подтверждении, выполнение, журнал. Таймер раз в 15 минут шлёт напоминания и "
               "отчёт в 08:30 / 18:00.")),
            ("result",
             L("A demo that works, leads that arrive", "Ishlaydigan demo va kelib turadigan so'rovlar", "Рабочее демо и приходящие заявки"),
             L("Visitors can test the assistant instead of reading about it. A conversation that ends with a contact becomes a lead "
               "in my Telegram with the transcript attached, and I reply from the same chat. Guest questions the assistant could not "
               "answer show up in the evening digest, so the site's content improves from real questions.\n\n"
               "The same core is integrated into my Restaurant ERP as the AI secretary for managers — see the next project.",
               "Mehmonlar assistent haqida o'qish o'rniga uni sinab ko'ra oladi. Kontakt bilan tugagan suhbat matni bilan birga "
               "Telegram'imga so'rov sifatida keladi, javobni ham o'sha chatdan yozaman. Assistent javob bera olmagan mehmon savollari "
               "kechki hisobotda ko'rinadi — sayt matni haqiqiy savollardan kelib chiqib yaxshilanib boradi.\n\n"
               "Xuddi shu yadro Restaurant ERP ichiga menejerlar uchun AI Kotib sifatida qo'shilgan — keyingi loyihaga qarang.",
               "Посетители могут проверить ассистента, а не читать о нём. Диалог, закончившийся контактом, приходит в мой Telegram как "
               "заявка с расшифровкой, и я отвечаю из того же чата. Вопросы гостей, на которые ассистент не смог ответить, попадают в "
               "вечерний отчёт — контент сайта улучшается от реальных вопросов.\n\n"
               "То же ядро встроено в мою Restaurant ERP как AI-секретарь для менеджеров — см. следующий проект.")),
        ],
        "images": [
            ("ai-assistant-architecture.png",
             L("Diagram: site visitor and owner on Telegram talk to one Django agent, which calls Gemini and the site database; "
               "leads go to Telegram, changes wait for confirmation",
               "Diagramma: sayt mehmoni va Telegram'dagi ega bitta Django agent bilan gaplashadi, u Gemini va sayt bazasini chaqiradi; "
               "so'rovlar Telegram'ga ketadi, o'zgarishlar tasdiq kutadi",
               "Диаграмма: посетитель сайта и владелец в Telegram говорят с одним Django-агентом, который обращается к Gemini и базе "
               "сайта; заявки уходят в Telegram, изменения ждут подтверждения"),
             L("One agent, two doors: read-only tools for visitors, full tools plus confirmations for the owner.",
               "Bitta agent, ikkita eshik: mehmonga faqat o'qiydigan tool'lar, egaga to'liq tool'lar va tasdiq.",
               "Один агент, две двери: инструменты только для чтения гостям, полный набор и подтверждения владельцу.")),
        ],
    },
    # ------------------------------------------------------------------
    {
        "slug": "ai-kotib-restaurant",
        "after": "restaurant-erp",
        "featured": False,
        "title": "AI Kotib — Restaurant Secretary in Telegram",
        "organisation": "Own product · part of Restaurant ERP",
        "status": "wip", "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "confidential": True,
        "tech": ["Python", "Django", "PostgreSQL", "Gemini API", "Telegram Bot API", "REST API"],
        "tagline": L(
            "An AI secretary inside the Restaurant ERP: reports to the manager in Telegram at 08:30 and 18:00, answers any staff "
            "question about the day, and applies changes the manager asks for — after a ✔.",
            "Restaurant ERP ichidagi AI Kotib: har kuni 08:30 va 18:00 da menejerga Telegram orqali hisobot yuboradi, xodimlarning "
            "kun haqidagi savollariga javob beradi va menejer so'ragan o'zgarishlarni ✔ dan keyin bajaradi.",
            "AI-секретарь внутри Restaurant ERP: отчитывается менеджеру в Telegram в 08:30 и 18:00, отвечает персоналу на любые "
            "вопросы о дне и вносит изменения по просьбе менеджера — после ✔.",
        ),
        "role": L("Product, backend, Telegram bot, prompt design",
                  "Mahsulot, backend, Telegram bot, prompt dizayni",
                  "Продукт, бэкенд, Telegram-бот, дизайн промптов"),
        "summary": L(
            "Every morning at 08:30 the manager gets a message: yesterday's sales and profit, today's bookings and shifts, tasks that "
            "were left unfinished, and a short plan for the day. At 18:00 comes the summary: what sold, what changed in the system, "
            "what needs attention. Any employee with access can ask for the same report whenever they need it.\n\n"
            "The secretary knows every change in the ERP — orders, stock, staff, bookings, tasks — because it reads the same database "
            "through tools, not from memory. When the manager writes \"move Aziz to the Tuesday evening shift\" or sends a voice note, "
            "the change is prepared and shown with ✔ / ✖; nothing is applied until the manager confirms.",
            "Har kuni 08:30 da menejerga xabar keladi: kechagi savdo va foyda, bugungi bronlar va smenalar, chala qolgan ishlar va "
            "kun uchun qisqa reja. 18:00 da yakun: nima sotildi, tizimda nima o'zgardi, nimaga e'tibor kerak. Ruxsati bor har bir "
            "xodim shu hisobotni istalgan vaqtda so'rab olishi mumkin.\n\n"
            "Kotib ERP'dagi har bir o'zgarishni biladi — buyurtmalar, ombor, xodimlar, bronlar, vazifalar — chunki u xotiradan emas, "
            "tool'lar orqali o'sha bazani o'qiydi. Menejer «Azizni seshanba kechki smenasiga o'tkaz» deb yozsa yoki ovozli "
            "xabar yuborsa, o'zgarish tayyorlanib ✔ / ✖ bilan ko'rsatiladi; menejer tasdiqlamaguncha hech narsa o'zgarmaydi.",
            "Каждое утро в 08:30 менеджер получает сообщение: вчерашние продажи и прибыль, сегодняшние брони и смены, незавершённые "
            "задачи и короткий план на день. В 18:00 приходит итог: что продалось, что изменилось в системе, на что обратить "
            "внимание. Любой сотрудник с доступом может запросить тот же отчёт в любой момент.\n\n"
            "Секретарь знает каждое изменение в ERP — заказы, склад, персонал, брони, задачи — потому что читает ту же базу через "
            "инструменты, а не по памяти. Когда менеджер пишет «переведи Азиза на вечернюю смену во вторник» или отправляет "
            "голосовое, изменение готовится и показывается с ✔ / ✖; пока менеджер не подтвердит, ничего не применяется.",
        ),
        "context": L(
            "Part of my Restaurant ERP, piloted with a chain of three branches. The same agent core runs the assistant on this site.",
            "Restaurant ERP'ning bir qismi; uch filialli tarmoqda sinovdan o'tmoqda. Xuddi shu agent yadrosi shu saytdagi assistentni ishlatadi.",
            "Часть моей Restaurant ERP, пилот в сети из трёх филиалов. То же ядро агента работает в ассистенте на этом сайте.",
        ),
        "metrics": [
            {"label": L("Scheduled reports a day", "Kunlik rejali hisobotlar", "Плановых отчётов в день"), "after": "2",
             "note": L("08:30 plan, 18:00 summary", "08:30 reja, 18:00 yakun", "08:30 план, 18:00 итог")},
            {"label": L("Manager's time to change a record", "Menejerning yozuvni o'zgartirishga vaqti", "Время менеджера на правку"),
             "before": "~2 min", "after": "1 message",
             "note": L("Say it, confirm it", "Aytasiz, tasdiqlaysiz", "Сказал — подтвердил")},
            {"label": L("Inputs understood", "Tushunadigan kirish turlari", "Типов ввода"), "after": "4",
             "note": L("Text, voice, photo, PDF", "Matn, ovoz, rasm, PDF", "Текст, голос, фото, PDF")},
            {"label": L("Changes applied without ✔", "✔ siz bajarilgan o'zgarishlar", "Изменений без ✔"), "after": "0",
             "note": L("Every change is prepared first", "Har bir o'zgarish avval tayyorlanadi", "Каждое изменение сначала готовится")},
        ],
        "sections": [
            ("problem",
             L("The manager learns things too late and types too much", "Menejer hammasini kech biladi va ko'p yozadi", "Менеджер узнаёт поздно и много печатает"),
             L("A restaurant manager starts the day without knowing what happened yesterday and ends it without a summary. The "
               "numbers exist in the ERP, but reading five screens every morning does not happen. Small changes — a shift, a phone "
               "number, a stop-listed dish — mean opening the panel, finding the record and editing it, usually from a phone in the kitchen.",
               "Restoran menejeri kunni kecha nima bo'lganini bilmasdan boshlaydi va yakunsiz tugatadi. Raqamlar ERP'da bor, lekin "
               "har kuni ertalab beshta ekranni ochib o'qish amalda bo'lmaydi. Mayda o'zgarishlar — smena, telefon raqami, "
               "stop-ro'yxatdagi taom — panelni ochish, yozuvni topish va tahrirlashni talab qiladi, ko'pincha oshxonada telefondan turib.",
               "Менеджер ресторана начинает день, не зная, что было вчера, и заканчивает его без итога. Цифры есть в ERP, но открывать "
               "пять экранов каждое утро никто не будет. Мелкие правки — смена, номер телефона, блюдо в стоп-листе — это открыть "
               "панель, найти запись и отредактировать, обычно с телефона на кухне.")),
            ("decision",
             L("Reports without AI tokens, changes only through confirmation", "Hisobotlar AI tokensiz, o'zgarishlar faqat tasdiq bilan", "Отчёты без AI-токенов, изменения только через подтверждение"),
             L("The scheduled reports are built from the database by code and only summarised by the model when someone asks a "
               "question about them — so the two daily messages cost no quota and never invent a number. Every fact in an answer comes "
               "from a tool; if the data is not there, the secretary says so.\n\n"
               "Changing tools never write. They validate the request, create a pending action with a human-readable summary, and the "
               "manager sees ✔ / ✖ buttons in Telegram. On ✔ the action is re-validated and applied, with an audit record of who "
               "confirmed what. Passwords and other secrets never pass through the model: a reset is done by the employee typing a new "
               "password into the bot, which deletes the message immediately and stores only the hash.",
               "Rejali hisobotlar bazadan kod orqali tuziladi, model esa faqat kimdir ular haqida savol berganda xulosa qiladi — "
               "shuning uchun kunlik ikkita xabar limit sarflamaydi va hech qachon raqam to'qimaydi. Javobdagi har bir fakt "
               "tool'dan keladi; ma'lumot bo'lmasa, kotib buni ochiq aytadi.\n\n"
               "O'zgartiruvchi tool'lar hech qachon yozmaydi. Ular so'rovni tekshiradi, odam tilida xulosasi bilan kutayotgan amal "
               "yaratadi va menejer Telegram'da ✔ / ✖ tugmalarini ko'radi. ✔ bosilganda amal qayta tekshirilib bajariladi, kim nimani "
               "tasdiqlagani jurnalga yoziladi. Parol va boshqa maxfiy ma'lumotlar model orqali o'tmaydi: parolni tiklashda xodim yangi "
               "parolni botga yozadi, bot xabarni darhol o'chiradi va faqat hash'ni saqlaydi.",
               "Плановые отчёты собираются из базы кодом, а модель лишь резюмирует их, когда кто-то задаёт вопрос, — поэтому два "
               "ежедневных сообщения не тратят квоту и никогда не выдумывают цифры. Каждый факт в ответе приходит из инструмента; "
               "если данных нет, секретарь так и говорит.\n\n"
               "Изменяющие инструменты никогда не пишут. Они проверяют запрос, создают ожидающее действие с понятным описанием, и "
               "менеджер видит кнопки ✔ / ✖ в Telegram. По ✔ действие проверяется повторно и применяется, в журнал записывается, кто "
               "что подтвердил. Пароли и другие секреты не проходят через модель: при сбросе сотрудник пишет новый пароль боту, бот "
               "сразу удаляет сообщение и хранит только хеш.")),
            ("architecture",
             L("Timer, agent, Telegram", "Timer, agent, Telegram", "Таймер, агент, Telegram"),
             L("A systemd timer calls the ERP every few minutes; at the configured times it builds the report for each branch and sends "
               "it to the manager and the staff who opted in. Questions and commands come through the bot's webhook: the message is "
               "acknowledged in under a second, the Gemini call runs in a background thread and edits a \"writing…\" message as the "
               "answer streams. Voice notes are transcribed with a cheap model first; photos are shrunk before upload.\n\n"
               "The agent shares its core with the assistant on this site: the same prompt structure, tool registry, action queue and "
               "logging, with the restaurant's own tools plugged in — sales, stock, staff, bookings, tasks and reports.",
               "systemd timer ERP'ni bir necha daqiqada bir chaqiradi; belgilangan vaqtlarda har bir filial uchun hisobot tuzilib, "
               "menejer va shunga rozi bo'lgan xodimlarga yuboriladi. Savol va buyruqlar bot webhook'i orqali keladi: xabar bir "
               "soniyadan kam vaqtda qabul qilinadi, Gemini chaqiruvi fon ipida ishlaydi va javob oqib kelgani sari «yozyapman…» "
               "xabarini tahrirlaydi. Ovozli xabarlar avval arzon model bilan matnga o'giriladi; rasmlar yuborishdan oldin kichraytiriladi.\n\n"
               "Agent yadrosi shu saytdagi assistent bilan bir xil: bir xil prompt tuzilmasi, tool ro'yxati, amallar navbati va jurnal; "
               "ustiga restoranning o'z tool'lari ulangan — savdo, ombor, xodimlar, bronlar, vazifalar va hisobotlar.",
               "Таймер systemd вызывает ERP каждые несколько минут; в заданное время собирается отчёт по каждому филиалу и уходит "
               "менеджеру и подписавшимся сотрудникам. Вопросы и команды приходят через webhook бота: сообщение принимается быстрее "
               "чем за секунду, вызов Gemini идёт в фоновом потоке и редактирует сообщение «пишу…» по мере стриминга. Голосовые "
               "сначала расшифровываются дешёвой моделью; фото сжимаются перед отправкой.\n\n"
               "Ядро агента общее с ассистентом на этом сайте: та же структура промпта, реестр инструментов, очередь действий и "
               "журнал, а сверху подключены инструменты ресторана — продажи, склад, персонал, брони, задачи и отчёты.")),
            ("result",
             L("Two messages a day instead of five screens", "Beshta ekran o'rniga kuniga ikkita xabar", "Два сообщения в день вместо пяти экранов"),
             L("The manager reads two messages a day and asks the rest in plain language. Routine edits take one sentence and one tap. "
               "Because everything is logged, the owner can see who changed what through the secretary. Next steps: voice replies and "
               "a weekly analysis with charts.",
               "Menejer kuniga ikkita xabar o'qiydi, qolganini oddiy tilda so'raydi. Oddiy tahrirlar bitta gap va bitta bosishga "
               "tushdi. Hammasi jurnalga yozilgani uchun egasi kotib orqali kim nimani o'zgartirganini ko'ra oladi. Keyingi qadamlar: "
               "ovozli javob va diagrammali haftalik tahlil.",
               "Менеджер читает два сообщения в день, остальное спрашивает простым языком. Рутинные правки занимают одну фразу и одно "
               "нажатие. Всё логируется, так что владелец видит, кто что изменил через секретаря. Дальше: голосовые ответы и "
               "недельная аналитика с графиками.")),
        ],
        "images": [
            ("ai-kotib-workflow.png",
             L("Diagram: the 08:30 and 18:00 schedule, the manager's text, voice, photo and PDF going to the AI secretary, the "
               "Telegram report, and a prepared change waiting for confirmation before it reaches the RestoPOS database",
               "Diagramma: 08:30 va 18:00 jadvali, menejerning matn, ovoz, rasm va PDF'i AI Kotibga boradi, Telegram hisobot va "
               "RestoPOS bazasiga yetishdan oldin tasdiq kutayotgan tayyorlangan o'zgarish",
               "Диаграмма: расписание 08:30 и 18:00, текст, голос, фото и PDF менеджера идут к AI-секретарю, отчёт в Telegram и "
               "подготовленное изменение, ждущее подтверждения перед записью в базу RestoPOS"),
             L("Reports on a schedule; commands become prepared changes that wait for ✔.",
               "Hisobotlar jadval bo'yicha; buyruqlar ✔ kutadigan tayyor o'zgarishlarga aylanadi.",
               "Отчёты по расписанию; команды становятся подготовленными изменениями, которые ждут ✔.")),
        ],
    },
]


def _place(slug, after):
    """Insert `slug` right after `after` in the published order, keeping the rest as it is."""
    ordered = list(Project.objects.order_by("order", "-year_started", "-id").values_list("slug", flat=True))
    if slug in ordered:
        ordered.remove(slug)
    idx = ordered.index(after) + 1 if after in ordered else min(1, len(ordered))
    ordered.insert(idx, slug)
    for i, s in enumerate(ordered):
        Project.objects.filter(slug=s).update(order=i)


def apply(log=lambda *a: None):
    for name, slug, category in NEW_TECH:
        Technology.objects.get_or_create(slug=slug, defaults={"name": name, "category": category})
    techs = {t.name: t for t in Technology.objects.all()}

    for data in PROJECTS:
        fields = {"title": data["title"], "organisation": data["organisation"], "status": data["status"],
                  "is_published": True, "is_confidential": data["confidential"], "repo_url": "",
                  "year_started": data["year_started"], "year_finished": data["year_finished"],
                  "team_size": data["team_size"], "is_featured": data["featured"]}
        for key in ("tagline", "role", "summary", "context"):
            fields.update(lang_fields(key, data[key]))
        project, created = Project.objects.update_or_create(slug=data["slug"], defaults=fields)
        project.technologies.set([techs[n] for n in data["tech"] if n in techs])

        project.sections.all().delete()
        for order, (kind, heading, body) in enumerate(data["sections"], 1):
            CaseSection.objects.create(project=project, kind=kind, order=order,
                                       **lang_fields("heading", heading), **lang_fields("body", body))
        project.metrics.all().delete()
        for order, m in enumerate(data["metrics"]):
            Metric.objects.create(project=project, order=order, value_before=m.get("before", ""),
                                  value_after=m["after"], **lang_fields("label", m["label"]),
                                  **lang_fields("note", m.get("note", "")))
        if not project.images.exists():
            for order, (filename, alt, caption) in enumerate(data["images"]):
                path = ASSETS / filename
                if not path.exists():
                    log(f"  missing {filename}")
                    continue
                img = ProjectImage(project=project, order=order, is_primary=(order == 0),
                                   **lang_fields("alt_text", alt), **lang_fields("caption", caption))
                with open(path, "rb") as fh:
                    img.image.save(filename, File(fh), save=False)
                img.save()
        if created:
            _place(data["slug"], data["after"])
        log(f"  {'created' if created else 'updated'} {project.title}")

    from apps.ai.state import invalidate
    invalidate()
