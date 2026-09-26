"""Load the real project content into the database.

    python manage.py load_portfolio             # update projects, replace their images
    python manage.py load_portfolio --keep-images

Content comes from the internal work report (2026). Screenshots live in
content/portfolio/ and were redacted before commit: driver names, VINs,
plates, phone numbers, tax ids, addresses and revenue figures are blurred.

Safe to run more than once. Projects not listed here (Roadside Locator,
medical AI, drowsiness detector) are left untouched. Site settings and
anything edited only in the admin outside these projects are not changed.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.projects.models import CaseSection, Metric, Project, ProjectImage, Technology
from apps.resume.models import Experience, ExperienceBullet

ASSETS = Path(settings.BASE_DIR) / "content" / "portfolio"

NEW_TECH = [
    ("Matplotlib", "matplotlib", "data"),
    ("Seaborn", "seaborn", "data"),
    ("Jupyter", "jupyter", "data"),
    ("Genlogs API", "genlogs-api", "tool"),
    ("Google Sheets API", "google-sheets-api", "tool"),
]

# Merged into separate projects below; kept in the database but hidden.
RETIRED = ["driver-safety-and-toll-automation"]


def L(en, uz, ru):
    return {"en": en, "uz": uz, "ru": ru}


PROJECTS = [
    # ------------------------------------------------------------------
    {
        "slug": "smart-yard-gate-automation",
        "title": "Smart Yard — Computer Vision for the Truck Yard",
        "status": "wip", "order": 1, "is_featured": True,
        "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "tech": ["Python", "YOLOv11", "OpenCV", "PyTorch", "FMCSA API", "Django", "PostgreSQL", "RTSP"],
        "tagline": L(
            "Seven yard cameras, one pipeline: detect the vehicle, read its USDOT and unit numbers, check the carrier and open the gate.",
            "Hovlidagi 7 ta kamera, bitta tizim: transportni aniqlash, USDOT va unit raqamini o'qish, tashuvchini tekshirish va darvozani ochish.",
            "Семь камер на площадке и один конвейер: распознать транспорт, прочитать USDOT и номер юнита, проверить перевозчика и открыть ворота.",
        ),
        "role": L("Computer vision, model training, backend",
                  "Computer vision, model o'qitish, backend",
                  "Компьютерное зрение, обучение моделей, бэкенд"),
        "summary": L(
            "The yard's cameras produced thousands of photos but no answers: which truck is this, who does it belong to, should the gate open? "
            "I trained a set of YOLOv11 models on our own yard footage — vehicle type, colour, USDOT and unit numbers, trailer units — and joined "
            "their outputs into one case per vehicle, checked against the FMCSA registry.",
            "Hovli kameralari minglab rasm yuborardi, lekin savollarga javob bermasdi: bu qaysi mashina, kimga tegishli, darvoza ochilsinmi? "
            "Hovlining o'z kadrlarida YOLOv11 modellarini o'qitdim — transport turi, rangi, USDOT va unit raqamlari, tirkama raqami — va ularning "
            "natijalarini har bir mashina uchun bitta holatga (case) birlashtirib, FMCSA reyestri bilan tekshiradigan qildim.",
            "Камеры площадки присылали тысячи снимков, но не давали ответов: что это за грузовик, чей он, открывать ли ворота? "
            "Я обучил набор моделей YOLOv11 на кадрах с нашей же площадки — тип транспорта, цвет, номера USDOT и юнита, номер прицепа — "
            "и объединил их результаты в один кейс на каждую машину с проверкой по реестру FMCSA.",
        ),
        "context": L("Built alone inside a US-market logistics company; runs on the company's own yard cameras.",
                     "AQSH bozoridagi logistika kompaniyasida yakka o'zim qurganman; kompaniya hovlisidagi kameralarda ishlaydi.",
                     "Сделано в одиночку в логистической компании, работающей на рынке США; работает на камерах площадки компании."),
        "metrics": [
            {"label": L("Model accuracy", "Modellar aniqligi", "Точность моделей"), "after": "82–95%",
             "note": L("Detection, colour and number-reading models", "Aniqlash, rang va raqam o'qish modellari", "Детекция, цвет и чтение номеров")},
            {"label": L("Training images", "O'quv rasmlari", "Обучающих изображений"), "after": "1,500+",
             "note": L("Labelled from our own yard cameras", "Hovlining o'z kameralaridan belgilangan", "Размечены с камер нашей площадки")},
            {"label": L("Camera streams", "Kamera oqimlari", "Потоков с камер"), "after": "7",
             "note": L("Merged into one case per vehicle", "Har mashina uchun bitta holatga birlashtiriladi", "Сводятся в один кейс на машину")},
        ],
        "sections": [
            ("problem",
             L("Cameras that see everything and tell nothing",
               "Hamma narsani ko'radigan, lekin hech narsa aytmaydigan kameralar",
               "Камеры, которые всё видят и ничего не сообщают"),
             L("Seven cameras watch the yard and drop snapshots into an inbox in no particular order. One truck can produce a dozen photos "
               "from four angles, mixed with every other vehicle that passed at the same time.\n\n"
               "The off-the-shelf smart cameras could read licence plates, but not the **USDOT number** or the **unit number** painted on the "
               "cab — the two identifiers a logistics company actually works with. Ready-made colour models also failed on our footage: "
               "low sun, shadows and dirty trailers made a grey truck look white.",
               "Hovlida 7 ta kamera bor va ular rasmlarni pochtaga tartibsiz yuboradi. Bitta yuk mashinasi to'rt burchakdan o'nlab rasm beradi, "
               "ular esa shu vaqtda o'tgan boshqa mashinalar rasmlari bilan aralashib ketadi.\n\n"
               "Tayyor aqlli kameralar davlat raqamini o'qiy olardi, lekin kabinadagi **USDOT** va **unit raqamini** o'qimasdi — logistika "
               "kompaniyasi aynan shu ikkisi bilan ishlaydi. Tayyor rang aniqlash modellari ham bizning kadrlarda xato qilardi: past quyosh, "
               "soya va iflos tirkamalar tufayli kulrang mashina oq bo'lib ko'rinardi.",
               "Семь камер следят за площадкой и сбрасывают снимки в почтовый ящик вперемешку. Один грузовик даёт десяток кадров с четырёх "
               "ракурсов вперемешку с остальным транспортом, проехавшим в то же время.\n\n"
               "Готовые «умные» камеры читали госномер, но не **USDOT** и не **номер юнита** на кабине — а именно с ними работает логистическая "
               "компания. Готовые модели определения цвета тоже ошибались на наших кадрах: низкое солнце, тени и грязные прицепы превращали "
               "серый грузовик в белый.")),
            ("decision",
             L("Several narrow models instead of one clever one",
               "Bitta murakkab model o'rniga bir nechta aniq vazifali modellar",
               "Несколько узких моделей вместо одной «умной»"),
             L("- **Vehicle detection** — YOLOv11 separates *truck*, *truck with trailer* and *car* in real time.\n"
               "- **Colour** — a model trained on yard photos, because generic colour models broke on our lighting.\n"
               "- **USDOT and unit reading** — a detector finds the number on the cab, then the crop is read. The USDOT goes to the "
               "**FMCSA API**, which returns the company, its status and contact details.\n"
               "- **Trailer unit reading** — the new home cameras and plate cameras could not read trailer numbers, so a separate model does.\n"
               "- **Case summary** — everything above is joined into one case per vehicle: type, colour, USDOT, unit, plate and the photos "
               "that prove it.\n\n"
               "Small models are easier to retrain and to debug: when a number is misread, it is obvious which stage failed.",
               "- **Transportni aniqlash** — YOLOv11 real vaqtda *yuk mashinasi*, *tirkamali yuk mashinasi* va *yengil avtomobil*ni ajratadi.\n"
               "- **Rang** — hovli rasmlarida o'qitilgan alohida model, chunki umumiy modellar bizdagi yorug'likda ishlamadi.\n"
               "- **USDOT va unit raqamini o'qish** — model kabinadagi raqamni topadi, keyin kesilgan qism o'qiladi. USDOT **FMCSA API**ga "
               "yuboriladi va kompaniya nomi, holati hamda aloqa ma'lumotlari qaytadi.\n"
               "- **Tirkama raqamini o'qish** — yangi kameralar tirkama raqamini o'qimasdi, shuning uchun buni alohida model bajaradi.\n"
               "- **Case summary** — yuqoridagilarning hammasi har bir mashina uchun bitta holatga birlashadi: turi, rangi, USDOT, unit, "
               "davlat raqami va buni tasdiqlovchi rasmlar.\n\n"
               "Kichik modellarni qayta o'qitish va tekshirish oson: raqam noto'g'ri o'qilsa, qaysi bosqichda xato bo'lgani darhol ko'rinadi.",
               "- **Детекция транспорта** — YOLOv11 в реальном времени различает *тягач*, *тягач с прицепом* и *легковой автомобиль*.\n"
               "- **Цвет** — отдельная модель, обученная на снимках площадки: общие модели не справлялись с нашим освещением.\n"
               "- **Чтение USDOT и номера юнита** — детектор находит номер на кабине, затем фрагмент распознаётся. USDOT уходит в **FMCSA API**, "
               "которое возвращает компанию, её статус и контакты.\n"
               "- **Номер прицепа** — новые камеры не читали номера прицепов, поэтому этим занимается отдельная модель.\n"
               "- **Сводный кейс** — всё перечисленное объединяется в один кейс на машину: тип, цвет, USDOT, юнит, госномер и подтверждающие снимки.\n\n"
               "Маленькие модели проще переобучать и отлаживать: если номер прочитан неверно, сразу видно, на каком этапе ошибка.")),
            ("architecture",
             L("How it fits together", "Qismlar qanday bog'langan", "Как это устроено"),
             L("```\n7 cameras → vehicle detection (YOLOv11) → colour model\n"
               "                        ↓\n"
               "        USDOT / unit / trailer-unit reading\n"
               "                        ↓\n"
               "     FMCSA API (company, status, contacts)\n"
               "                        ↓\n"
               "  case per vehicle → gate rules → open / close\n"
               "                        ↓\n"
               "          event log (Django + PostgreSQL)\n```",
               "```\n7 ta kamera → transportni aniqlash (YOLOv11) → rang modeli\n"
               "                          ↓\n"
               "        USDOT / unit / tirkama raqamini o'qish\n"
               "                          ↓\n"
               "     FMCSA API (kompaniya, holat, kontaktlar)\n"
               "                          ↓\n"
               "  har mashina uchun case → darvoza qoidalari → ochish / yopish\n"
               "                          ↓\n"
               "         hodisalar jurnali (Django + PostgreSQL)\n```",
               "```\n7 камер → детекция транспорта (YOLOv11) → модель цвета\n"
               "                        ↓\n"
               "      чтение USDOT / юнита / номера прицепа\n"
               "                        ↓\n"
               "    FMCSA API (компания, статус, контакты)\n"
               "                        ↓\n"
               "  кейс на машину → правила ворот → открыть / закрыть\n"
               "                        ↓\n"
               "        журнал событий (Django + PostgreSQL)\n```")),
            ("result",
             L("Where it stands", "Hozirgi holati", "Текущее состояние"),
             L("Each model reaches **82–95% accuracy**, trained on more than **1,500** labelled images from the yard.\n\n"
               "The gate logic runs on two cameras: the outside camera detects an arriving vehicle and sends the open command; the inside "
               "camera sees it pass and sends the close command. Every decision is written to an event log. Right now cars pass automatically, "
               "while trucks wait for the payment step. The next stage is letting trucks with a monthly yard subscription through without a stop.",
               "Har bir model **82–95% aniqlik** beradi; hovlidan olingan **1 500** dan ortiq belgilangan rasmda o'qitilgan.\n\n"
               "Darvoza mantig'i ikki kamerada ishlaydi: tashqi kamera kelgan mashinani aniqlab, ochish buyrug'ini yuboradi; ichki kamera "
               "mashina o'tganini ko'rib, yopish buyrug'ini yuboradi. Har bir qaror hodisalar jurnaliga yoziladi. Hozir yengil avtomobillar "
               "avtomatik o'tadi, yuk mashinalari esa to'lov bosqichini kutadi. Keyingi bosqich — hovli uchun oylik to'lov qilgan yuk "
               "mashinalarini to'xtatmasdan o'tkazish.",
               "Каждая модель даёт **82–95% точности**; обучение шло на более чем **1 500** размеченных снимках с площадки.\n\n"
               "Логика ворот работает на двух камерах: внешняя замечает подъехавший транспорт и отправляет команду на открытие, внутренняя "
               "видит, что машина проехала, и отправляет команду на закрытие. Каждое решение пишется в журнал событий. Сейчас легковые машины "
               "проезжают автоматически, а грузовики ждут этапа оплаты. Следующий шаг — пропускать без остановки грузовики с месячной "
               "подпиской на стоянку.")),
            ("retro",
             L("What I would do differently", "Nimani boshqacha qilgan bo'lardim", "Что бы я сделал иначе"),
             L("I would start collecting the hard frames — glare, rain, night, a truck half out of view — from the first day. The models "
               "improved most when those cases went into the training set, and early on I was discarding them as noise.",
               "Qiyin kadrlarni — yarqirash, yomg'ir, tun, kadrdan yarim chiqib ketgan mashina — birinchi kundan yig'a boshlagan bo'lardim. "
               "Modellar aynan shu holatlar o'quv to'plamiga qo'shilganda eng ko'p yaxshilandi, men esa boshida ularni shovqin deb tashlab yuborardim.",
               "Я бы с первого дня собирал сложные кадры — блики, дождь, ночь, грузовик наполовину вне кадра. Модели сильнее всего улучшались, "
               "когда такие случаи попадали в обучающую выборку, а в начале я выбрасывал их как шум.")),
        ],
        "images": [
            ("smart-yard-gate-dashboard.jpg",
             L("Gate dashboard with inside and outside cameras and the event log",
               "Ichki va tashqi kameralar hamda hodisalar jurnali bilan darvoza paneli",
               "Панель ворот с внутренней и внешней камерой и журналом событий"),
             L("Gate control: outside camera opens, inside camera closes, every event is logged",
               "Darvoza boshqaruvi: tashqi kamera ochadi, ichki kamera yopadi, har bir hodisa yoziladi",
               "Управление воротами: внешняя камера открывает, внутренняя закрывает, каждое событие записывается")),
            ("smart-yard-case-summary.jpg",
             L("Case card that merges the photos of one truck with its USDOT number",
               "Bitta yuk mashinasi rasmlari va USDOT raqamini birlashtirgan case kartochkasi",
               "Карточка кейса, объединяющая снимки одного грузовика и его USDOT"),
             L("Case summary: one vehicle, all its photos, the proof frame and the carrier",
               "Case summary: bitta mashina, uning barcha rasmlari, tasdiqlovchi kadr va tashuvchi",
               "Сводный кейс: одна машина, все её снимки, подтверждающий кадр и перевозчик")),
            ("smart-yard-vehicle-detection.jpg",
             L("Grid of yard photos with truck, trailer and car detections",
               "Yuk mashinasi, tirkama va avtomobil aniqlangan hovli rasmlari",
               "Снимки площадки с распознанными тягачами, прицепами и легковыми машинами"),
             L("Vehicle detection on real yard footage", "Hovlining haqiqiy kadrlarida transportni aniqlash",
               "Детекция транспорта на реальных кадрах площадки")),
            ("smart-yard-usdot-read.jpg",
             L("Truck door with the USDOT number read and the carrier name returned",
               "USDOT raqami o'qilgan va tashuvchi nomi aniqlangan kabina eshigi",
               "Дверь кабины с прочитанным USDOT и найденным перевозчиком"),
             L("USDOT and unit number read from the cab, carrier found via FMCSA",
               "Kabinadan USDOT va unit raqami o'qildi, tashuvchi FMCSA orqali topildi",
               "USDOT и номер юнита прочитаны с кабины, перевозчик найден через FMCSA")),
            ("smart-yard-trailer-unit.jpg",
             L("Close-up of a trailer unit number read by the model",
               "Model o'qigan tirkama raqamining yaqin ko'rinishi",
               "Крупный план номера прицепа, прочитанного моделью"),
             L("Trailer unit reading where the stock cameras failed",
               "Oddiy kameralar o'qiy olmagan tirkama raqamini o'qish",
               "Чтение номера прицепа там, где штатные камеры не справлялись")),
            ("smart-yard-training-metrics.png",
             L("Training curves: losses falling, precision and recall rising",
               "O'qitish grafiklari: xatolik kamayib, precision va recall o'sib boradi",
               "Графики обучения: потери снижаются, precision и recall растут"),
             L("Training run of the detection model", "Aniqlash modelini o'qitish jarayoni",
               "Процесс обучения модели детекции")),
        ],
    },
    # ------------------------------------------------------------------
    {
        "slug": "fleet-asset-platform",
        "title": "FleetOps — Fleet & Asset Management Platform",
        "status": "production", "order": 2, "is_featured": True,
        "year_started": 2025, "year_finished": 2026, "team_size": 1,
        "tech": ["Django", "PostgreSQL", "Python", "JavaScript", "Pandas", "Google Sheets API", "REST API"],
        "tagline": L(
            "Five Google Sheets boards that ran a fleet of 3,400+ trucks and 800 trailers, rebuilt as one web platform.",
            "3 400 dan ortiq yuk mashinasi va 800 tirkamali parkni boshqargan beshta Google Sheets jadvali — bitta veb-platformaga aylandi.",
            "Пять таблиц Google Sheets, на которых держался парк из 3 400+ тягачей и 800 прицепов, — теперь одна веб-платформа.",
        ),
        "role": L("Backend, data model, dashboards", "Backend, ma'lumotlar modeli, dashboardlar",
                  "Бэкенд, модель данных, дашборды"),
        "summary": L(
            "The fleet and asset teams ran everything in shared spreadsheets: trucks, companies, the devices in each cab, inspections and "
            "trailer leases. I moved these boards to a Django platform one by one, kept them in sync with the sheets during the switch, and "
            "added what a spreadsheet cannot do: expiry alerts, status workflows and totals that recalculate with every filter.",
            "Fleet va asset jamoalari hamma narsani umumiy jadvallarda yuritardi: yuk mashinalari, kompaniyalar, har bir kabinadagi qurilmalar, "
            "texnik ko'riklar va tirkama ijaralari. Bu jadvallarni birma-bir Django platformasiga ko'chirdim, o'tish davrida Google Sheets bilan "
            "sinxron ushladim va jadval qila olmaydigan narsalarni qo'shdim: muddat tugashi haqida ogohlantirish, holatlar bo'yicha jarayon va har "
            "bir filtrda qayta hisoblanadigan summalar.",
            "Команды автопарка и активов вели всё в общих таблицах: тягачи, компании, устройства в каждой кабине, техосмотры и аренду прицепов. "
            "Я по очереди перенёс эти таблицы на платформу на Django, на время перехода держал их в синхронизации с Google Sheets и добавил то, "
            "чего таблица не умеет: предупреждения об истечении сроков, статусные процессы и суммы, пересчитываемые при каждом фильтре.",
        ),
        "context": L("Internal platform for the fleet, asset and accounting teams.",
                     "Fleet, asset va buxgalteriya jamoalari uchun ichki platforma.",
                     "Внутренняя платформа для отделов автопарка, активов и бухгалтерии."),
        "metrics": [
            {"label": L("Trucks", "Yuk mashinalari", "Тягачей"), "before": "Google Sheets", "after": "3,477",
             "note": L("Statuses, expiry alerts, export", "Holatlar, muddat ogohlantirishlari, eksport", "Статусы, сроки, экспорт")},
            {"label": L("Trailers under agreements", "Shartnomadagi tirkamalar", "Прицепов по договорам"), "after": "801",
             "note": L("48 agreements, 16 leasing companies", "48 ta shartnoma, 16 ta lizing kompaniyasi", "48 договоров, 16 лизинговых компаний")},
            {"label": L("Device assignments", "Qurilma biriktirishlari", "Привязок устройств"), "after": "6,400+",
             "note": L("Fuel cards, PrePass, ELD, tablets", "Yoqilg'i kartalari, PrePass, ELD, planshetlar", "Топливные карты, PrePass, ELD, планшеты")},
        ],
        "sections": [
            ("problem",
             L("The spreadsheet was the system", "Jadvalning o'zi tizim edi", "Таблица и была системой"),
             L("Each team had its own Google Sheets board, and several people edited them at once. The same truck lived in three sheets with "
               "slightly different data. Nobody got a warning when a lease or a registration was about to expire, and when a truck went "
               "inactive, its fuel card, PrePass and ELD often stayed assigned to it — paid for, but lost.",
               "Har bir jamoaning o'z Google Sheets jadvali bor edi va ularni bir vaqtning o'zida bir nechta odam tahrirlardi. Bitta yuk mashinasi "
               "uchta jadvalda bir-biridan biroz farq qiladigan ma'lumot bilan turardi. Ijara yoki ro'yxatdan o'tish muddati tugayotganini hech kim "
               "oldindan bilmasdi, mashina faol bo'lmay qolganda esa uning yoqilg'i kartasi, PrePass va ELD qurilmasi ko'pincha unga biriktirilgan "
               "holda qolib ketardi — puli to'lanadi, lekin qayerdaligi noma'lum.",
               "У каждой команды была своя таблица Google Sheets, и её одновременно правили несколько человек. Один и тот же тягач жил в трёх "
               "таблицах с немного разными данными. Никто не получал предупреждения об истечении аренды или регистрации, а когда машина "
               "становилась неактивной, её топливная карта, PrePass и ELD часто так и оставались за ней — оплачиваются, но потеряны.")),
            ("decision",
             L("Board by board, not a big-bang rewrite", "Hammasini birdan emas, jadvalma-jadval", "По одной таблице, а не всё сразу"),
             L("I moved one board at a time and checked each against its sheet before the team switched over:\n\n"
               "- **Trucks** — every truck with make, status and owner; filters by company, owner type and expiry alert; export.\n"
               "- **Companies** — the operating companies, linked to their trucks.\n"
               "- **Truck In Use** — which fuel card, PrePass, ELD and tablet sits in which truck, including devices rented from another company.\n"
               "- **Inactive → Charges** — when a truck goes inactive, its devices move to a return list. Unreturned devices become *Need to charge* "
               "and flow to a Charges board that accounting uses to recover the cost from the driver.\n"
               "- **Inspection** — PTI inspections moved out of the In Use sheet into their own board with the latest result per truck.\n"
               "- **Trailer Agreements** — owned and leased trailers with separate views for vans, flatbeds and reefers; every filter "
               "recalculates the payment totals.",
               "Jadvallarni bittadan ko'chirdim va jamoa o'tishidan oldin har birini asl jadval bilan solishtirib chiqdim:\n\n"
               "- **Trucks** — har bir yuk mashinasi: markasi, holati, egasi; kompaniya, egalik turi va muddat ogohlantirishi bo'yicha filtrlar; eksport.\n"
               "- **Companies** — ishlovchi kompaniyalar, ularning mashinalariga bog'langan.\n"
               "- **Truck In Use** — qaysi yoqilg'i kartasi, PrePass, ELD va planshet qaysi mashinada turibdi, boshqa kompaniyadan ijaraga olingan qurilmalar ham.\n"
               "- **Inactive → Charges** — mashina faol bo'lmay qolsa, qurilmalari qaytarish ro'yxatiga o'tadi. Qaytarilmaganlari *Need to charge* "
               "holatiga o'tib, Charges jadvaliga tushadi; buxgalteriya undan qurilma pulini haydovchidan undirish uchun foydalanadi.\n"
               "- **Inspection** — PTI texnik ko'riklari alohida jadvalga chiqarildi, har mashina bo'yicha oxirgi natija ko'rinadi.\n"
               "- **Trailer Agreements** — sotib olingan va ijaradagi tirkamalar; van, platforma va refrijerator uchun alohida bo'limlar; har bir "
               "filtrda to'lov summalari qayta hisoblanadi.",
               "Я переносил таблицы по одной и перед переходом команды сверял каждую с исходником:\n\n"
               "- **Trucks** — каждый тягач с маркой, статусом и владельцем; фильтры по компании, типу владения и срокам; экспорт.\n"
               "- **Companies** — операционные компании, связанные со своими машинами.\n"
               "- **Truck In Use** — какая топливная карта, PrePass, ELD и планшет стоят в какой машине, включая устройства, арендованные у другой компании.\n"
               "- **Inactive → Charges** — когда машина становится неактивной, её устройства попадают в список на возврат. Невозвращённые получают "
               "статус *Need to charge* и уходят в таблицу Charges, по которой бухгалтерия удерживает их стоимость с водителя.\n"
               "- **Inspection** — техосмотры PTI вынесены в отдельную таблицу с последним результатом по каждой машине.\n"
               "- **Trailer Agreements** — собственные и арендованные прицепы с отдельными разделами для фургонов, платформ и рефрижераторов; "
               "каждый фильтр пересчитывает суммы платежей.")),
            ("result",
             L("What changed", "Nima o'zgardi", "Что изменилось"),
             L("The fleet team works from one source of truth instead of several copies. Expiring documents surface before the date, not after. "
               "Devices that used to disappear with inactive trucks now follow a clear path — returned, or charged. The trailer board shows "
               "801 trailers across 48 agreements and 16 leasing companies, with totals that match whatever filter is applied.",
               "Fleet jamoasi endi bir nechta nusxa o'rniga bitta ishonchli manbadan ishlaydi. Muddati tugayotgan hujjatlar sanadan keyin emas, "
               "oldin ko'rinadi. Ilgari faol bo'lmagan mashinalar bilan yo'qolib ketadigan qurilmalar endi aniq yo'ldan o'tadi: qaytariladi yoki "
               "puli undiriladi. Tirkamalar bo'limida 48 ta shartnoma va 16 ta lizing kompaniyasi bo'yicha 801 ta tirkama ko'rinadi, summalar esa "
               "tanlangan filtrga mos hisoblanadi.",
               "Отдел автопарка работает с одним источником данных вместо нескольких копий. Истекающие документы видны до срока, а не после. "
               "Устройства, которые раньше терялись вместе с неактивными машинами, проходят понятный путь — возврат или удержание. В разделе "
               "прицепов видно 801 прицеп по 48 договорам и 16 лизинговым компаниям, а суммы соответствуют выбранному фильтру.")),
            ("retro",
             L("What I would do differently", "Nimani boshqacha qilgan bo'lardim", "Что бы я сделал иначе"),
             L("I would design device assignments as dated history from the first board. Retrofitting history later means the period before "
               "the change simply is not recorded.",
               "Qurilma biriktirishlarini birinchi jadvaldanoq sanali tarix sifatida loyihalagan bo'lardim. Tarixni keyin qo'shganda, o'zgarishdan "
               "oldingi davr shunchaki yozilmay qoladi.",
               "Я бы с первой же таблицы хранил привязки устройств как историю с датами. Если добавлять историю позже, период до изменения "
               "просто не сохраняется.")),
        ],
        "images": [
            ("fleet-trailer-agreements.png",
             L("Trailer agreements dashboard with totals by type, status and company",
               "Tur, holat va kompaniya bo'yicha jamlangan tirkama shartnomalari paneli",
               "Дашборд договоров на прицепы с итогами по типу, статусу и компании"),
             L("Trailer Agreements: 801 trailers by type, status and company (financial figures hidden)",
               "Trailer Agreements: tur, holat va kompaniya bo'yicha 801 ta tirkama (moliyaviy raqamlar yashirilgan)",
               "Trailer Agreements: 801 прицеп по типу, статусу и компании (финансовые данные скрыты)")),
            ("fleet-trucks-board.png",
             L("Trucks board with status counters and filters",
               "Holat hisoblagichlari va filtrlari bilan yuk mashinalari jadvali",
               "Таблица тягачей со счётчиками статусов и фильтрами"),
             L("Trucks: 3,477 trucks with status counters and expiry alerts (personal data blurred)",
               "Trucks: holat hisoblagichlari va muddat ogohlantirishlari bilan 3 477 ta mashina (shaxsiy ma'lumotlar xiralashtirilgan)",
               "Trucks: 3 477 тягачей со счётчиками статусов и сроками (личные данные размыты)")),
            ("fleet-in-use-board.png",
             L("Truck In Use board listing the devices assigned to each truck",
               "Har bir mashinaga biriktirilgan qurilmalar ko'rsatilgan Truck In Use jadvali",
               "Таблица Truck In Use с устройствами, закреплёнными за каждой машиной"),
             L("Truck In Use: fuel card, PrePass, ELD and tablet per truck (identifiers blurred)",
               "Truck In Use: har mashina bo'yicha yoqilg'i kartasi, PrePass, ELD va planshet (identifikatorlar xiralashtirilgan)",
               "Truck In Use: топливная карта, PrePass, ELD и планшет по каждой машине (идентификаторы размыты)")),
        ],
    },
    # ------------------------------------------------------------------
    {
        "slug": "driver-safety-events",
        "title": "Driver Safety Events Dashboard",
        "status": "production", "order": 3, "is_featured": True,
        "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "tech": ["Python", "Django", "PostgreSQL", "Motive API", "REST API"],
        "tagline": L(
            "Safety alerts for every driver, pulled from Motive and counted since the last conversation — so the camera team calls only the drivers who need it.",
            "Har bir haydovchi bo'yicha xavfsizlik ogohlantirishlari Motive'dan olinadi va oxirgi suhbatdan beri hisoblanadi — kamera jamoasi faqat kerakli haydovchilarga qo'ng'iroq qiladi.",
            "Сигналы безопасности по каждому водителю собираются из Motive и считаются с момента последнего разговора — команда звонит только тем, кому нужно.",
        ),
        "role": L("Backend, API integration, dashboard", "Backend, API integratsiya, dashboard",
                  "Бэкенд, интеграция API, дашборд"),
        "summary": L(
            "Every day the camera team copied safety alerts from a Telegram bot and from Motive into Google Sheets by hand, then tried to call "
            "every driver. The dashboard collects the alerts and safety scores through the Motive API and shows, per driver, only what has "
            "happened since the team last spoke to them.",
            "Kamera jamoasi har kuni xavfsizlik ogohlantirishlarini Telegram botdan va Motive'dan qo'lda Google Sheetsga ko'chirar, keyin barcha "
            "haydovchilarga qo'ng'iroq qilishga urinardi. Dashboard ogohlantirishlar va xavfsizlik ballarini Motive API orqali o'zi yig'adi va har "
            "bir haydovchi bo'yicha faqat jamoa u bilan oxirgi marta gaplashgandan keyin sodir bo'lgan hodisalarni ko'rsatadi.",
            "Каждый день команда камер вручную переносила сигналы безопасности из Telegram-бота и Motive в Google Sheets, а затем пыталась "
            "дозвониться всем водителям. Дашборд сам собирает сигналы и оценки безопасности через Motive API и показывает по каждому водителю "
            "только то, что произошло после последнего разговора с ним.",
        ),
        "context": L("Built for the camera (safety) team.", "Kamera (xavfsizlik) jamoasi uchun qurilgan.",
                     "Сделано для команды камер (безопасности)."),
        "metrics": [
            {"label": L("Daily manual copying", "Kunlik qo'lda ko'chirish", "Ежедневное ручное копирование"), "after": "0",
             "note": L("Alerts arrive through the Motive API", "Ogohlantirishlar Motive API orqali keladi", "Сигналы приходят через Motive API")},
            {"label": L("Events counted since", "Hodisalar hisobi boshlanadi", "События считаются с"), "after": "Last action",
             "note": L("Calls go only to drivers who need them", "Qo'ng'iroq faqat kerakli haydovchilarga", "Звонят только тем, кому нужно")},
        ],
        "sections": [
            ("problem",
             L("A daily routine that did not scale", "Kengaymaydigan kundalik ish", "Рутина, которая не масштабировалась"),
             L("Motive records every speeding event, hard brake, phone use and tailgating. The data existed; the process around it did not. "
               "The team sorted it by hand every morning, and with hundreds of drivers there was no way to call everyone — so calls went to "
               "whoever came first, not to whoever needed it most.",
               "Motive tezlikni oshirish, keskin tormoz, telefonga chalg'ish va juda yaqin yurish kabi har bir hodisani yozib boradi. Ma'lumot bor edi, "
               "lekin u bilan ishlash tartibi yo'q edi. Jamoa har kuni ertalab uni qo'lda saralardi, yuzlab haydovchi bo'lganda esa hammaga qo'ng'iroq "
               "qilishning iloji yo'q edi — qo'ng'iroq eng ko'p kerak bo'lgan haydovchiga emas, ro'yxatda birinchi turganga ketardi.",
               "Motive фиксирует каждое превышение скорости, резкое торможение, использование телефона и опасную дистанцию. Данные были, "
               "не было процесса вокруг них. Команда каждое утро разбирала их вручную, а при сотнях водителей дозвониться всем было невозможно — "
               "звонили тем, кто первый в списке, а не тем, кому это нужнее всего.")),
            ("decision",
             L("Count from the last conversation", "Oxirgi suhbatdan boshlab hisoblash", "Считать с последнего разговора"),
             L("The key field is **Last action**. When the team talks to a driver, they write the result in a note and close the case. "
               "From that date the dashboard counts only new events for that driver, grouped by type, next to the current safety score.\n\n"
               "An **Active** page shows who needs attention, with date and company filters. An **Archive** page shows every closed case and "
               "what the team did, with export for reporting.",
               "Asosiy maydon — **Last action**. Jamoa haydovchi bilan gaplashgach, natijani izohga yozadi va holatni yopadi. Shu sanadan boshlab "
               "dashboard o'sha haydovchi bo'yicha faqat yangi hodisalarni turlariga ajratib, joriy xavfsizlik bali yonida hisoblaydi.\n\n"
               "**Active** sahifasi sana va kompaniya filtrlari bilan kimga e'tibor kerakligini ko'rsatadi. **Archive** sahifasida barcha yopilgan "
               "holatlar va jamoa nima qilgani turadi, hisobot uchun eksport ham bor.",
               "Ключевое поле — **Last action**. Поговорив с водителем, команда записывает результат в заметку и закрывает кейс. С этой даты "
               "дашборд считает по водителю только новые события, сгруппированные по типам, рядом с текущей оценкой безопасности.\n\n"
               "Страница **Active** с фильтрами по дате и компании показывает, кому нужно внимание. Страница **Archive** хранит все закрытые кейсы "
               "и действия команды, с экспортом для отчётов.")),
            ("result",
             L("What changed", "Nima o'zgardi", "Что изменилось"),
             L("The morning copy-paste is gone. Calls are prioritised by what actually happened on the road, and the archive shows managers "
               "how each driver's record developed after a conversation.",
               "Ertalabki ko'chirib o'tkazish ishi yo'qoldi. Qo'ng'iroqlar yo'lda haqiqatda nima bo'lganiga qarab navbatga qo'yiladi, arxiv esa "
               "rahbarlarga suhbatdan keyin har bir haydovchining ko'rsatkichi qanday o'zgarganini ko'rsatadi.",
               "Утреннее копирование ушло. Звонки расставляются по приоритету исходя из того, что реально произошло на дороге, а архив показывает "
               "руководителям, как менялись показатели водителя после разговора.")),
        ],
        "images": [
            ("safety-events-active.png",
             L("Active safety events page with alert counts and scores per driver",
               "Haydovchilar bo'yicha ogohlantirishlar soni va ballar ko'rsatilgan Active sahifasi",
               "Страница Active с количеством сигналов и оценками по водителям"),
             L("Active: new events per driver since the last action (names blurred)",
               "Active: oxirgi harakatdan keyingi yangi hodisalar (ismlar xiralashtirilgan)",
               "Active: новые события по водителю после последнего действия (имена размыты)")),
            ("safety-events-archive.png",
             L("Archive page with closed cases and the team's actions",
               "Yopilgan holatlar va jamoa harakatlari ko'rsatilgan Archive sahifasi",
               "Страница Archive с закрытыми кейсами и действиями команды"),
             L("Archive: closed cases and export for reporting", "Archive: yopilgan holatlar va hisobot uchun eksport",
               "Archive: закрытые кейсы и экспорт для отчётов")),
        ],
    },
    # ------------------------------------------------------------------
    {
        "slug": "trailer-toll-allocation",
        "title": "Trailer Toll Allocation",
        "status": "production", "order": 4, "is_featured": False,
        "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "tech": ["Python", "Django", "Pandas", "PostgreSQL"],
        "tagline": L(
            "Upload the toll file — the system works out which leasing company owes each charge.",
            "Toll faylini yuklang — tizim har bir to'lovni qaysi ijarachi kompaniya to'lashi kerakligini o'zi hisoblaydi.",
            "Загрузите файл с платными дорогами — система сама определит, какая компания-арендатор должна оплатить каждый проезд.",
        ),
        "role": L("Backend, data processing", "Backend, ma'lumotlarni qayta ishlash", "Бэкенд, обработка данных"),
        "summary": L(
            "Brokerage trailers are leased to different companies, and toll invoices arrive per trailer, not per tenant. Splitting them was "
            "manual work. Now the toll file is uploaded, each charge is matched to whoever was using the trailer on that date, and the totals "
            "can be exported.",
            "Brokerage tirkamalari turli kompaniyalarga ijaraga beriladi, pullik yo'l hisob-fakturalari esa ijarachi bo'yicha emas, tirkama bo'yicha "
            "keladi. Ularni taqsimlash qo'lda bajarilardi. Endi toll fayli yuklanadi, har bir to'lov o'sha sanada tirkamadan kim foydalangani bilan "
            "moslashtiriladi va jami summalarni eksport qilish mumkin.",
            "Прицепы брокерского отдела сдаются в аренду разным компаниям, а счета за платные дороги приходят по прицепу, а не по арендатору. "
            "Распределение делалось вручную. Теперь файл загружается, каждый проезд сопоставляется с тем, кто пользовался прицепом в этот день, "
            "а итоги можно выгрузить.",
        ),
        "metrics": [
            {"label": L("Manual toll splitting", "Toll to'lovlarini qo'lda taqsimlash", "Ручное распределение проездов"), "after": "0",
             "note": L("Done automatically on file upload", "Fayl yuklanganda avtomatik bajariladi", "Выполняется автоматически при загрузке файла")},
        ],
        "sections": [
            ("decision",
             L("How it works", "Qanday ishlaydi", "Как это работает"),
             L("- A toll file is uploaded and parsed with Pandas.\n"
               "- Each charge is matched by trailer and date to the company that held the trailer at that time.\n"
               "- The detail view shows the full toll record, who used the trailer then and who uses it now.\n"
               "- Processed charges move to an archive; totals by owner and company can be exported to CSV.",
               "- Toll fayli yuklanadi va Pandas yordamida o'qiladi.\n"
               "- Har bir to'lov tirkama va sana bo'yicha o'sha paytda tirkamani ushlab turgan kompaniyaga moslashtiriladi.\n"
               "- Batafsil sahifada to'lovning to'liq ma'lumoti, o'sha kuni tirkamadan kim foydalangani va hozir kim foydalanayotgani ko'rinadi.\n"
               "- Ishlov berilgan to'lovlar arxivga o'tadi; egasi va kompaniya bo'yicha summalarni CSV qilib yuklab olish mumkin.",
               "- Загружается файл, Pandas разбирает его.\n"
               "- Каждый проезд по номеру прицепа и дате сопоставляется с компанией, у которой прицеп был в это время.\n"
               "- В карточке видно полную запись проезда, кто пользовался прицепом тогда и кто пользуется сейчас.\n"
               "- Обработанные проезды уходят в архив; итоги по владельцу и компании выгружаются в CSV.")),
        ],
        "images": [
            ("toll-report.png",
             L("Toll report table with amounts and the company responsible for each charge",
               "Summalar va har bir to'lov uchun mas'ul kompaniya ko'rsatilgan toll hisoboti",
               "Отчёт по платным дорогам с суммами и ответственной компанией по каждому проезду"),
             L("Toll report: every charge matched to the responsible company (plates blurred)",
               "Toll hisoboti: har bir to'lov mas'ul kompaniyaga biriktirilgan (raqamlar xiralashtirilgan)",
               "Отчёт: каждый проезд привязан к ответственной компании (номера размыты)")),
        ],
    },
    # ------------------------------------------------------------------
    {
        "slug": "fuel-discount-analytics",
        "title": "Fuel Discount Analytics",
        "status": "research", "order": 5, "is_featured": False,
        "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "tech": ["Python", "Pandas", "Matplotlib", "Seaborn", "Jupyter", "REST API"],
        "tagline": L(
            "Where in the US diesel discounts are worth the detour — fuel prices pulled by API and compared across states, weeks and stations.",
            "AQShning qayerida dizel chegirmasi yo'lni o'zgartirishga arziydi — API orqali olingan yoqilg'i narxlari shtatlar, haftalar va stansiyalar bo'yicha solishtirildi.",
            "Где в США скидка на дизель стоит крюка — цены на топливо получены через API и сравнены по штатам, неделям и заправкам.",
        ),
        "role": L("Data analysis", "Ma'lumotlar tahlili", "Анализ данных"),
        "summary": L(
            "Fuel is the largest variable cost of a trucking fleet, and discounts differ widely by state and even by station. I pulled US fuel "
            "prices and discounts through an API and analysed them in three cuts: discount differences between states, one state over the last "
            "month, and a single station week by week.",
            "Yoqilg'i — yuk tashish parkining eng katta o'zgaruvchan xarajati, chegirmalar esa shtatga va hatto stansiyaga qarab keskin farq qiladi. "
            "AQShdagi yoqilg'i narxlari va chegirmalarni API orqali olib, uch kesimda tahlil qildim: shtatlar orasidagi chegirma farqi, bitta shtatning "
            "oxirgi bir oydagi ko'rsatkichi va bitta stansiyaning haftalik narxlari.",
            "Топливо — главная переменная статья расходов автопарка, а скидки сильно различаются по штатам и даже по заправкам. Я получил цены и "
            "скидки на топливо в США через API и проанализировал их в трёх разрезах: разница скидок между штатами, один штат за последний месяц "
            "и одна заправка по неделям.",
        ),
        "metrics": [
            {"label": L("US average discount", "AQSh bo'yicha o'rtacha chegirma", "Средняя скидка по США"), "after": "$0.73/gal",
             "note": L("In the analysed period", "Tahlil qilingan davrda", "За анализируемый период")},
            {"label": L("Top vs. bottom state", "Eng yuqori va eng past shtat", "Лучший и худший штат"), "before": "~$0.25", "after": "~$1.25",
             "note": L("Discount per gallon", "Bir gallon uchun chegirma", "Скидка на галлон")},
        ],
        "sections": [
            ("result",
             L("What the data showed", "Ma'lumotlar nimani ko'rsatdi", "Что показали данные"),
             L("The gap between states is large: the best states gave around five times the discount of the weakest ones, against a national "
               "average of about $0.73 per gallon. Within one state the discount moved noticeably from day to day, which means the timing of a "
               "fill-up matters, not only the location.",
               "Shtatlar orasidagi farq katta: eng yaxshi shtatlarda chegirma eng zaif shtatlarga nisbatan taxminan besh baravar yuqori, mamlakat "
               "bo'yicha o'rtacha esa bir gallon uchun taxminan $0,73. Bitta shtat ichida ham chegirma kundan kunga sezilarli o'zgaradi — ya'ni faqat "
               "qayerda emas, qachon yoqilg'i quyish ham muhim.",
               "Разница между штатами велика: в лучших штатах скидка примерно в пять раз больше, чем в худших, при среднем по стране около $0,73 "
               "за галлон. Внутри одного штата скидка заметно меняется изо дня в день — значит, важно не только где заправляться, но и когда.")),
        ],
        "images": [
            ("fuel-discount-by-state.png",
             L("Line chart of daily fuel discounts in Texas, Missouri and Illinois over a month",
               "Texas, Missouri va Illinois shtatlarida bir oylik kunlik chegirmalar grafigi",
               "График ежедневных скидок в Техасе, Миссури и Иллинойсе за месяц"),
             L("Daily discount in three states over one month", "Uch shtatda bir oy davomidagi kunlik chegirma",
               "Ежедневная скидка в трёх штатах за месяц")),
            ("fuel-discount-states-ranked.png",
             L("Bar chart of average fuel discount by state with the US average line",
               "Shtatlar bo'yicha o'rtacha chegirma va AQSh o'rtacha chizig'i",
               "Средняя скидка по штатам и линия среднего по США"),
             L("Average discount by state against the US average", "Shtatlar bo'yicha o'rtacha chegirma va AQSh o'rtachasi",
               "Средняя скидка по штатам относительно среднего по США")),
        ],
    },
]

EXPERIENCE_SUMMARY = L(
    "I build the internal software of a fleet running 3,400+ trucks and 800 trailers: computer vision for the yard, web platforms that "
    "replaced the teams' spreadsheets, and data tools for safety, tolls and fuel. I also look after the office IT.",
    "3 400 dan ortiq yuk mashinasi va 800 tirkamali parkning ichki dasturlarini yarataman: hovli uchun computer vision, jamoalarning "
    "jadvallarini almashtirgan veb-platformalar hamda xavfsizlik, pullik yo'llar va yoqilg'i bo'yicha tahliliy vositalar. Ofisning IT "
    "infratuzilmasi ham menda.",
    "Разрабатываю внутреннее ПО для автопарка из 3 400+ тягачей и 800 прицепов: компьютерное зрение для площадки, веб-платформы, "
    "заменившие таблицы отделов, и инструменты анализа данных по безопасности, платным дорогам и топливу. Также отвечаю за IT в офисе.",
)

EXPERIENCE_BULLETS = [
    L("Trained YOLOv11 models for vehicle type, colour, USDOT, unit and trailer numbers (82–95% accuracy, 1,500+ images) and joined them into automated gate control.",
      "Transport turi, rangi, USDOT, unit va tirkama raqamlari uchun YOLOv11 modellarini o'qitdim (82–95% aniqlik, 1 500+ rasm) va ularni avtomatik darvoza boshqaruviga birlashtirdim.",
      "Обучил модели YOLOv11 для типа транспорта, цвета, USDOT, номеров юнита и прицепа (точность 82–95%, 1 500+ снимков) и объединил их в автоматическое управление воротами."),
    L("Moved the fleet and asset teams from Google Sheets to a Django platform: trucks, companies, devices in use, inactive and charges, inspections, trailer agreements.",
      "Fleet va asset jamoalarini Google Sheetsdan Django platformasiga o'tkazdim: yuk mashinalari, kompaniyalar, qurilmalar, faol bo'lmaganlar va undirishlar, texnik ko'rik, tirkama shartnomalari.",
      "Перевёл отделы автопарка и активов с Google Sheets на платформу на Django: тягачи, компании, устройства, неактивные и удержания, техосмотры, договоры на прицепы."),
    L("Built a safety events dashboard on the Motive API that counts each driver's alerts since the team's last action.",
      "Motive API asosida har bir haydovchining ogohlantirishlarini jamoaning oxirgi harakatidan beri hisoblaydigan xavfsizlik dashboardini qurdim.",
      "Сделал дашборд событий безопасности на Motive API, который считает сигналы водителя с последнего действия команды."),
    L("Automated splitting of trailer toll charges between leasing companies on file upload.",
      "Tirkamalarning pullik yo'l to'lovlarini fayl yuklanganda ijarachi kompaniyalar o'rtasida avtomatik taqsimlashni yo'lga qo'ydim.",
      "Автоматизировал распределение платы за проезд прицепов между компаниями-арендаторами при загрузке файла."),
    L("Analysed US diesel prices and discounts by state and station; built a weekly fleet movement report from the Genlogs API.",
      "AQShdagi dizel narxlari va chegirmalarini shtat va stansiya bo'yicha tahlil qildim; Genlogs API asosida parkning haftalik harakat hisobotini tayyorladim.",
      "Проанализировал цены и скидки на дизель в США по штатам и заправкам; сделал еженедельный отчёт о перемещениях парка на Genlogs API."),
    L("IT support: installed Windows and set up workstations, rolled out Krisp across the carrier sales office, and handled hardware issues.",
      "IT yordam: Windows o'rnatdim va ish joylarini sozladim, carrier sales ofisidagi barcha kompyuterlarga Krisp o'rnatdim, texnika nosozliklarini hal qildim.",
      "IT-поддержка: установка Windows и настройка рабочих мест, внедрение Krisp во всём офисе carrier sales, решение проблем с оборудованием."),
]


def lang_fields(prefix, value):
    """{"en": .., "uz": .., "ru": ..} or a plain string -> model field kwargs."""
    if isinstance(value, dict):
        return {f"{prefix}_{code}": text for code, text in value.items()}
    return {f"{prefix}_en": value}


class Command(BaseCommand):
    help = "Load real project content and redacted screenshots."

    def add_arguments(self, parser):
        parser.add_argument("--keep-images", action="store_true",
                            help="Do not replace the images of the updated projects.")

    @transaction.atomic
    def handle(self, *args, **options):
        missing = [img[0] for p in PROJECTS for img in p["images"] if not (ASSETS / img[0]).exists()]
        if missing:
            self.stderr.write(f"Missing files in {ASSETS}: {', '.join(missing)}")
            return

        for name, slug, category in NEW_TECH:
            Technology.objects.get_or_create(slug=slug, defaults={"name": name, "category": category})
        techs = {t.name: t for t in Technology.objects.all()}

        for data in PROJECTS:
            self._project(data, techs, options["keep_images"])

        hidden = Project.objects.filter(slug__in=RETIRED).update(is_published=False)
        if hidden:
            self.stdout.write(f"· hidden old combined project ({hidden})")

        # The remaining projects follow the new ones
        for offset, slug in enumerate(["roadside-service-locator", "medical-ai-cancer-detection",
                                       "driver-drowsiness-detector"]):
            Project.objects.filter(slug=slug).update(order=6 + offset)

        self._experience()
        self.stdout.write(self.style.SUCCESS("Done."))

    def _project(self, data, techs, keep_images):
        fields = {"title": data["title"], "status": data["status"], "order": data["order"],
                  "is_featured": data["is_featured"], "is_published": True, "is_confidential": True,
                  "repo_url": "", "year_started": data["year_started"],
                  "year_finished": data["year_finished"], "team_size": data["team_size"]}
        for key in ("tagline", "role", "summary", "context"):
            if key in data:
                fields.update(lang_fields(key, data[key]))

        project, created = Project.objects.update_or_create(slug=data["slug"], defaults=fields)
        if not project.organisation:
            project.organisation = "International logistics company"
            project.save(update_fields=["organisation"])
        project.technologies.set([techs[n] for n in data["tech"] if n in techs])

        project.sections.all().delete()
        for order, (kind, heading, body) in enumerate(data["sections"], 1):
            CaseSection.objects.create(project=project, kind=kind, order=order,
                                       **lang_fields("heading", heading), **lang_fields("body", body))

        project.metrics.all().delete()
        for order, m in enumerate(data["metrics"]):
            Metric.objects.create(
                project=project, order=order,
                value_before=m.get("before", ""), value_after=m["after"],
                **lang_fields("label", m["label"]), **lang_fields("note", m.get("note", "")),
            )

        if not keep_images:
            project.images.all().delete()
            for order, (filename, alt, caption) in enumerate(data["images"]):
                img = ProjectImage(project=project, order=order, is_primary=(order == 0),
                                   **lang_fields("alt_text", alt), **lang_fields("caption", caption))
                with open(ASSETS / filename, "rb") as fh:
                    img.image.save(filename, File(fh), save=False)
                img.save()

        self.stdout.write(f"· {'created' if created else 'updated'} {project.title} "
                          f"({project.sections.count()} sections, {project.images.count()} images)")

    def _experience(self):
        job = Experience.objects.filter(end_date__isnull=True).order_by("order").first()
        if not job:
            self.stdout.write("· no current job found, experience skipped")
            return
        for code, text in EXPERIENCE_SUMMARY.items():
            setattr(job, f"summary_{code}", text)
        job.save()
        job.bullets.all().delete()
        for order, bullet in enumerate(EXPERIENCE_BULLETS):
            ExperienceBullet.objects.create(experience=job, order=order, **lang_fields("text", bullet))
        self.stdout.write(f"· updated experience: {job.company} ({len(EXPERIENCE_BULLETS)} bullets)")
