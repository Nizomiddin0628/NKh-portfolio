"""Second content update (September 2026).

    python manage.py load_portfolio_update

Touches only:
  - restaurant-erp          (new project)
  - live-truck-map          (new project)
  - medical-ai-cancer-detection  (rewritten from the graduation thesis)
  - fleet-asset-platform    (the Trucks board screenshot is removed)
  - project order

Everything else edited in the admin stays as it is. Safe to run again:
it only rewrites the three projects above.
"""
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.projects.models import CaseSection, Metric, Project, ProjectImage, Technology

from .load_portfolio import ASSETS, L, lang_fields

NEW_TECH = [
    ("Leaflet", "leaflet", "frontend"),
    ("Telegram Bot API", "telegram-bot-api", "tool"),
    ("Tkinter", "tkinter", "frontend"),
]

ORDER = [
    "smart-yard-gate-automation",
    "restaurant-erp",
    "fleet-asset-platform",
    "live-truck-map",
    "driver-safety-events",
    "medical-ai-cancer-detection",
    "trailer-toll-allocation",
    "fuel-discount-analytics",
    "roadside-service-locator",
    "driver-drowsiness-detector",
]
FEATURED = {"smart-yard-gate-automation", "restaurant-erp", "fleet-asset-platform"}

PROJECTS = [
    # ------------------------------------------------------------------
    {
        "slug": "restaurant-erp",
        "title": "Restaurant ERP — Sales, Kitchen, Stock & Team",
        "organisation": "Own product",
        "status": "wip", "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "confidential": True,
        "tech": ["Python", "Django", "PostgreSQL", "JavaScript", "Telegram Bot API", "REST API"],
        "tagline": L(
            "One system for a restaurant chain: till, kitchen screen, menu and cost price, stock, staff, bookings, loyalty and reports — for every branch.",
            "Restoranlar tarmog'i uchun yagona tizim: kassa, oshxona ekrani, menyu va tannarx, ombor, xodimlar, bron, bonuslar va hisobotlar — barcha filiallar uchun.",
            "Одна система для сети ресторанов: касса, экран кухни, меню и себестоимость, склад, персонал, бронь, бонусы и отчёты — по всем филиалам.",
        ),
        "role": L("Product, backend, frontend", "Mahsulot, backend, frontend", "Продукт, бэкенд, фронтенд"),
        "summary": L(
            "Restaurants usually run on four or five disconnected tools: a till, a notebook for stock, a spreadsheet for salaries, a chat for tasks. "
            "This ERP puts them in one place. The owner opens one screen and sees today's sales, orders, average bill, food cost, labour cost and "
            "net profit for every branch, compared with the same time yesterday.",
            "Restoranlar odatda bir-biriga bog'lanmagan 4–5 ta vosita bilan ishlaydi: kassa, ombor uchun daftar, ish haqi uchun jadval, vazifalar uchun chat. "
            "Bu ERP ularni bir joyga jamlaydi. Egasi bitta ekranni ochib, har bir filial bo'yicha bugungi savdo, buyurtmalar, o'rtacha chek, food cost, "
            "mehnat xarajati va sof foydani kechagi shu vaqt bilan solishtirib ko'radi.",
            "Рестораны обычно работают в 4–5 разрозненных инструментах: касса, тетрадь для склада, таблица для зарплат, чат для задач. "
            "Эта ERP собирает всё в одном месте. Владелец открывает один экран и видит по каждому филиалу сегодняшние продажи, заказы, средний чек, "
            "food cost, расходы на персонал и чистую прибыль в сравнении с тем же временем вчера.",
        ),
        "context": L("My own product, piloted with a restaurant chain of three branches.",
                     "O'zimning mahsulotim; uch filialli restoranlar tarmog'ida sinovdan o'tmoqda.",
                     "Мой собственный продукт; проходит пилот в сети из трёх ресторанов."),
        "metrics": [
            {"label": L("Modules", "Modullar", "Модулей"), "after": "18",
             "note": L("From the till to staff training", "Kassadan xodimlarni o'qitishgacha", "От кассы до обучения персонала")},
            {"label": L("Branches in the pilot", "Sinovdagi filiallar", "Филиалов в пилоте"), "after": "3",
             "note": L("One dashboard for all of them", "Hammasi uchun bitta panel", "Один дашборд на все")},
            {"label": L("Owner's key numbers", "Egasi uchun asosiy ko'rsatkichlar", "Ключевые показатели"), "after": "6",
             "note": L("Sales, orders, bill, food cost, labour, profit", "Savdo, buyurtma, chek, food cost, mehnat, foyda", "Продажи, заказы, чек, food cost, персонал, прибыль")},
        ],
        "sections": [
            ("problem",
             L("Numbers the owner sees too late", "Egasi kech ko'radigan raqamlar", "Цифры, которые владелец видит слишком поздно"),
             L("A restaurant owner with several branches usually learns about food cost or a slow day at the end of the month, when it is too late to "
               "fix. Sales sit in the till, stock in a notebook, salaries in a spreadsheet and tasks in a group chat — and nobody puts them together.",
               "Bir nechta filiali bor restoran egasi food cost oshganini yoki savdo pasayganini odatda oy oxirida, tuzatishga kech bo'lganda biladi. "
               "Savdo kassada, ombor daftarda, ish haqi jadvalda, vazifalar esa guruh chatida turadi — va ularni hech kim bir-biriga bog'lamaydi.",
               "Владелец с несколькими филиалами обычно узнаёт о росте food cost или слабом дне в конце месяца, когда исправлять уже поздно. "
               "Продажи — в кассе, склад — в тетради, зарплаты — в таблице, задачи — в групповом чате, и никто не сводит их вместе.")),
            ("decision",
             L("What is inside", "Tizim ichida nimalar bor", "Что внутри"),
             L("- **Sales** — till, menu and prices, halls and tables, bookings and queue, a kitchen screen for the cooks and a TV screen for the hall.\n"
               "- **Stock and cost** — ingredients with minimum levels, cost price per dish and live food cost; the dashboard warns when an item runs low.\n"
               "- **Customers and marketing** — loyalty and bonuses, a Telegram bot for orders, the restaurant's own website and brand page.\n"
               "- **Team (HR)** — staff, roles and access, labour cost, and a training module for new employees.\n"
               "- **Tasks** — a board where issues and tasks move through stages, from *new* to *done*, like a Trello board.\n"
               "- **Reports** — every metric per branch and for the whole chain: today, yesterday, 7 days, month, year.",
               "- **Savdo** — kassa, menyu va narxlar, zal va stollar, bron va navbat, oshpazlar uchun oshxona ekrani va zal uchun TV ekran.\n"
               "- **Ombor va tannarx** — minimal zaxirasi belgilangan mahsulotlar, har bir taom tannarxi va jonli food cost; mahsulot kamayganda panel ogohlantiradi.\n"
               "- **Mijozlar va marketing** — bonus tizimi, buyurtma uchun Telegram bot, restoranning o'z sayti va brend sahifasi.\n"
               "- **Xodimlar (HR)** — xodimlar, rollar va huquqlar, mehnat xarajati, yangi xodimlar uchun o'qitish moduli.\n"
               "- **Vazifalar** — muammo va topshiriqlar *yangi* bosqichidan *bajarildi*gacha o'tadigan Trello uslubidagi doska.\n"
               "- **Hisobotlar** — har bir ko'rsatkich filial va butun tarmoq bo'yicha: bugun, kecha, 7 kun, oy, yil.",
               "- **Продажи** — касса, меню и цены, залы и столы, бронь и очередь, экран кухни для поваров и TV-экран для зала.\n"
               "- **Склад и себестоимость** — продукты с минимальным остатком, себестоимость каждого блюда и живой food cost; дашборд предупреждает, когда продукт заканчивается.\n"
               "- **Клиенты и маркетинг** — бонусная система, Telegram-бот для заказов, собственный сайт и страница бренда.\n"
               "- **Персонал (HR)** — сотрудники, роли и доступы, расходы на персонал, модуль обучения новичков.\n"
               "- **Задачи** — доска в стиле Trello, где задачи и проблемы проходят этапы от *новой* до *выполнено*.\n"
               "- **Отчёты** — каждый показатель по филиалу и по всей сети: сегодня, вчера, 7 дней, месяц, год.")),
            ("result",
             L("Where it stands", "Hozirgi holati", "Текущее состояние"),
             L("The system runs in a pilot with three branches. The owner's day now starts with one screen: sales against yesterday, orders by status, "
               "best-selling dishes, branch comparison and the list of ingredients to reorder.",
               "Tizim uch filialda sinovdan o'tmoqda. Egasining kuni endi bitta ekrandan boshlanadi: kechagiga nisbatan savdo, holatlar bo'yicha "
               "buyurtmalar, eng ko'p sotilgan taomlar, filiallar solishtiruvi va buyurtma qilinishi kerak bo'lgan mahsulotlar ro'yxati.",
               "Система работает в пилоте на трёх филиалах. День владельца теперь начинается с одного экрана: продажи в сравнении со вчера, заказы по "
               "статусам, самые продаваемые блюда, сравнение филиалов и список продуктов к дозаказу.")),
        ],
        "images": [
            ("restaurant-erp-dashboard.png",
             L("Owner dashboard with sales, orders, food cost and branch comparison",
               "Savdo, buyurtmalar, food cost va filiallar solishtiruvi ko'rsatilgan boshqaruv paneli",
               "Панель владельца с продажами, заказами, food cost и сравнением филиалов"),
             L("Owner's dashboard: today against yesterday, across three branches",
               "Egasining paneli: uch filial bo'yicha bugun va kecha solishtiruvi",
               "Панель владельца: сегодня против вчера по трём филиалам")),
        ],
    },
    # ------------------------------------------------------------------
    {
        "slug": "live-truck-map",
        "title": "Live Truck Map",
        "organisation": "International logistics company",
        "status": "production", "year_started": 2026, "year_finished": 2026, "team_size": 1,
        "confidential": True,
        "tech": ["Django", "JavaScript", "Leaflet", "Motive API", "PostgreSQL"],
        "tagline": L(
            "All 575 trucks on one map, live: where each one is, how fast it moves, and which ones report a fault or low fuel.",
            "Barcha 575 ta yuk mashinasi bitta xaritada, jonli: har biri qayerda, qanday tezlikda ketyapti va qaysilarida nosozlik yoki yoqilg'i kam.",
            "Все 575 тягачей на одной карте в реальном времени: где каждый, с какой скоростью едет и у кого неисправность или мало топлива.",
        ),
        "role": L("Backend, map interface", "Backend, xarita interfeysi", "Бэкенд, интерфейс карты"),
        "summary": L(
            "Dispatch needed to answer simple questions fast: where is truck 1112, which trucks are moving in Texas, who is about to run out of fuel. "
            "The map pulls the position of every truck, refreshes every few seconds and groups nearby trucks into clusters, so 575 vehicles stay readable.",
            "Dispetcherlarga oddiy savollarga tez javob kerak edi: 1112-mashina qayerda, Texasda qaysi mashinalar harakatda, kimning yoqilg'isi tugay "
            "deb qoldi. Xarita har bir mashinaning joylashuvini olib, bir necha soniyada yangilaydi va yaqin mashinalarni guruhlab ko'rsatadi — shuning "
            "uchun 575 ta mashina ham chalkashmasdan o'qiladi.",
            "Диспетчерам нужно было быстро отвечать на простые вопросы: где тягач 1112, какие машины едут по Техасу, у кого заканчивается топливо. "
            "Карта получает позицию каждой машины, обновляется каждые несколько секунд и группирует соседние машины в кластеры — поэтому 575 машин "
            "остаются читаемыми.",
        ),
        "metrics": [
            {"label": L("Trucks on the map", "Xaritadagi mashinalar", "Машин на карте"), "after": "575"},
            {"label": L("Refresh", "Yangilanish", "Обновление"), "after": "~10 s",
             "note": L("Positions sync automatically", "Joylashuvlar avtomatik sinxronlanadi", "Позиции синхронизируются автоматически")},
        ],
        "sections": [
            ("decision",
             L("What dispatch can do", "Dispetcher nima qila oladi", "Что может диспетчер"),
             L("- See every truck with its unit, speed, nearest town and time of the last signal.\n"
               "- Filter by company and status, or show only trucks with **fault codes** or **low fuel**.\n"
               "- Search by unit, driver or VIN and jump straight to the truck.\n"
               "- Read the counters at the top: how many trucks are on the map, how many are moving and how many are sending live data.",
               "- Har bir mashinani unit raqami, tezligi, eng yaqin shahar va oxirgi signal vaqti bilan ko'rish.\n"
               "- Kompaniya va holat bo'yicha filtrlash yoki faqat **nosozlik kodi** bor yoki **yoqilg'isi kam** mashinalarni ko'rsatish.\n"
               "- Unit, haydovchi yoki VIN bo'yicha qidirib, darhol mashinaga o'tish.\n"
               "- Yuqoridagi hisoblagichlar: xaritada nechta mashina bor, nechtasi harakatda va nechtasi jonli ma'lumot yuboryapti.",
               "- Видеть каждую машину с номером юнита, скоростью, ближайшим городом и временем последнего сигнала.\n"
               "- Фильтровать по компании и статусу или показывать только машины с **кодами неисправностей** или **низким уровнем топлива**.\n"
               "- Искать по юниту, водителю или VIN и сразу переходить к машине.\n"
               "- Смотреть счётчики сверху: сколько машин на карте, сколько в движении и сколько передают данные в реальном времени.")),
        ],
        "images": [
            ("truck-map-live.jpg",
             L("Map of the United States with truck clusters and a list of moving trucks",
               "Yuk mashinalari guruhlari va harakatdagi mashinalar ro'yxati bilan AQSh xaritasi",
               "Карта США с кластерами грузовиков и списком машин в движении"),
             L("575 trucks live, with fault-code and low-fuel filters (driver names blurred)",
               "575 ta mashina jonli, nosozlik va yoqilg'i filtrlari bilan (haydovchi ismlari xiralashtirilgan)",
               "575 машин в реальном времени с фильтрами неисправностей и топлива (имена водителей размыты)")),
        ],
    },
    # ------------------------------------------------------------------
    {
        "slug": "medical-ai-cancer-detection",
        "title": "Prostate Cancer Detection & Gleason Grading",
        "organisation": "Fergana State Technical University · graduation thesis",
        "status": "research", "year_started": 2023, "year_finished": 2024, "team_size": 1,
        "confidential": False,
        "tech": ["Python", "YOLOv5", "PyTorch", "OpenCV", "Tkinter", "NumPy"],
        "tagline": L(
            "A YOLOv5 model that finds cancer regions in prostate biopsy images and grades them on the Gleason scale — in about 0.1 s per image.",
            "Prostata biopsiyasi tasvirlarida saraton o'choqlarini topib, ularni Gleason shkalasi bo'yicha darajalaydigan YOLOv5 modeli — bitta tasvirga taxminan 0,1 soniya.",
            "Модель YOLOv5, которая находит очаги рака на снимках биопсии простаты и оценивает их по шкале Глисона — около 0,1 с на снимок.",
        ),
        "role": L("Research, dataset, model training, desktop app", "Tadqiqot, dataset, model o'qitish, desktop ilova",
                  "Исследование, датасет, обучение модели, десктоп-приложение"),
        "summary": L(
            "My graduation thesis. A pathologist grades prostate cancer by looking at tissue under a microscope, and telling Grade 3 from Grade 4 is "
            "hard even for specialists. I built a detector that marks suspicious regions on a histopathology image and assigns each one a class — "
            "Benign, Grade 3, Grade 4 or Grade 5 — with a confidence score, as a second opinion for the doctor.",
            "Bitiruv malakaviy ishim. Patolog prostata saratoni darajasini mikroskop ostida to'qimaga qarab aniqlaydi, Grade 3 ni Grade 4 dan ajratish "
            "esa mutaxassislar uchun ham qiyin. Gistopatologik tasvirdagi shubhali hududlarni belgilab, har biriga sinf — Benign, Grade 3, Grade 4 "
            "yoki Grade 5 — va ishonch darajasini beradigan detektor yaratdim. U shifokor uchun ikkinchi fikr vazifasini bajaradi.",
            "Моя дипломная работа. Патолог определяет степень рака простаты, глядя на ткань под микроскопом, и отличить Grade 3 от Grade 4 сложно "
            "даже специалистам. Я сделал детектор, который отмечает подозрительные участки на гистологическом снимке и присваивает каждому класс — "
            "Benign, Grade 3, Grade 4 или Grade 5 — с уровнем уверенности, как второе мнение для врача.",
        ),
        "context": L("Supported by a Silk Road Health Data Science grant.",
                     "Silk Road Health Data Science granti bilan qo'llab-quvvatlangan.",
                     "Поддержано грантом Silk Road Health Data Science."),
        "metrics": [
            {"label": L("Accuracy on unseen images", "Yangi tasvirlardagi aniqlik", "Точность на новых снимках"), "after": "89%",
             "note": L("97% on the training set", "O'quv to'plamida 97%", "97% на обучающей выборке")},
            {"label": L("Grade 3 vs Grade 4", "Grade 3 va Grade 4", "Grade 3 против Grade 4"), "after": "85%+",
             "note": L("The hardest pair to tell apart", "Ajratish eng qiyin bo'lgan juftlik", "Самая сложная пара")},
            {"label": L("Time per image", "Bitta tasvirga vaqt", "Время на снимок"), "after": "~0.1 s"},
        ],
        "sections": [
            ("problem",
             L("A decision made by eye", "Ko'z bilan qabul qilinadigan qaror", "Решение, принимаемое на глаз"),
             L("The Gleason grade decides how a patient is treated. It is set by a pathologist reading glass slides, which is slow and subjective: "
               "two specialists can disagree on the same sample, especially between Grade 3 (glands still formed) and Grade 4 (glands fused).",
               "Gleason darajasi bemor qanday davolanishini belgilaydi. Uni patolog shisha slaydlarni ko'rib aniqlaydi — bu sekin va sub'ektiv jarayon: "
               "ikki mutaxassis bitta namuna bo'yicha turli xulosaga kelishi mumkin, ayniqsa Grade 3 (bezlar hali shakllangan) va Grade 4 (bezlar "
               "birlashib ketgan) orasida.",
               "Степень по Глисону определяет, как будут лечить пациента. Её ставит патолог, просматривая стёкла, — это медленно и субъективно: "
               "два специалиста могут разойтись во мнении по одному образцу, особенно между Grade 3 (железы ещё сформированы) и Grade 4 (железы слиты).")),
            ("decision",
             L("How it was built", "Qanday qurildi", "Как это сделано"),
             L("- **Data.** 500+ high-resolution biopsy images, each region labelled with one of four classes: Benign, Grade 3, Grade 4, Grade 5.\n"
               "- **Preparation.** Images resized to 640×640 and expanded with mosaic and other augmentations to **1,776** training images.\n"
               "- **Model.** YOLOv5m, chosen because it both *locates* a region and *classifies* it in one pass — a doctor needs to see where, not just a yes/no.\n"
               "- **Validation.** Two test sets: 50 images similar to the training data, and a second set of completely new images.\n"
               "- **App.** A Tkinter desktop program: load an image, get the marked regions with class and confidence, and a short written conclusion.",
               "- **Ma'lumotlar.** 500 dan ortiq yuqori aniqlikdagi biopsiya tasviri; har bir hudud to'rt sinfdan biri bilan belgilandi: Benign, Grade 3, Grade 4, Grade 5.\n"
               "- **Tayyorlash.** Tasvirlar 640×640 o'lchamga keltirildi va mosaic hamda boshqa augmentatsiyalar bilan **1 776** ta o'quv tasviriga ko'paytirildi.\n"
               "- **Model.** YOLOv5m — chunki u hududni bir o'tishda ham *topadi*, ham *sinflaydi*. Shifokorga shunchaki ha/yo'q emas, aynan qayerda ekani kerak.\n"
               "- **Tekshirish.** Ikki test to'plami: o'quv ma'lumotlariga o'xshash 50 ta tasvir va mutlaqo yangi tasvirlardan iborat ikkinchi to'plam.\n"
               "- **Ilova.** Tkinter'dagi desktop dastur: tasvir yuklanadi, sinf va ishonch darajasi bilan belgilangan hududlar hamda qisqa xulosa chiqadi.",
               "- **Данные.** 500+ снимков биопсии высокого разрешения; каждый участок размечен одним из четырёх классов: Benign, Grade 3, Grade 4, Grade 5.\n"
               "- **Подготовка.** Снимки приведены к 640×640 и расширены мозаичной и другими аугментациями до **1 776** обучающих изображений.\n"
               "- **Модель.** YOLOv5m — за один проход она и *находит* участок, и *классифицирует* его. Врачу нужно видеть, где именно, а не просто да/нет.\n"
               "- **Проверка.** Два тестовых набора: 50 снимков, похожих на обучающие, и второй набор из совершенно новых снимков.\n"
               "- **Приложение.** Десктоп-программа на Tkinter: загрузил снимок — получил отмеченные участки с классом, уверенностью и короткое заключение.")),
            ("result",
             L("Outcome", "Natija", "Результат"),
             L("On images it had never seen, the model reached **89%** accuracy. It separates healthy tissue from Grade 5 almost perfectly, and "
               "tells Grade 3 from Grade 4 — the pair that troubles pathologists most — with over 85% accuracy. One image takes about 0.1 seconds.\n\n"
               "The thesis was defended at Fergana State Technical University and received a grant from the Silk Road Health Data Science community.",
               "Model ilgari ko'rmagan tasvirlarda **89%** aniqlikka erishdi. U sog'lom to'qimani Grade 5 dan deyarli xatosiz ajratadi, patologlarni "
               "eng ko'p qiynaydigan Grade 3 va Grade 4 juftligini esa 85% dan yuqori aniqlikda farqlaydi. Bitta tasvirga taxminan 0,1 soniya ketadi.\n\n"
               "Ish Farg'ona davlat texnika universitetida himoya qilindi va Silk Road Health Data Science hamjamiyatining grantiga sazovor bo'ldi.",
               "На снимках, которых модель раньше не видела, точность составила **89%**. Здоровую ткань от Grade 5 она отличает почти безошибочно, а "
               "пару Grade 3 и Grade 4, которая сложнее всего для патологов, — с точностью выше 85%. Один снимок обрабатывается примерно за 0,1 секунды.\n\n"
               "Работа защищена в Ферганском государственном техническом университете и получила грант сообщества Silk Road Health Data Science.")),
            ("retro",
             L("What I would do differently", "Nimani boshqacha qilgan bo'lardim", "Что бы я сделал иначе"),
             L("The gap between 97% on training images and 89% on new ones is the most honest number in this project: the model learned part of "
               "the training set by heart. Today I would collect slides from more laboratories and scanners before training longer, and I would report "
               "the confusion matrix first instead of a single accuracy figure.",
               "O'quv tasvirlaridagi 97% va yangi tasvirlardagi 89% orasidagi farq — bu loyihadagi eng halol raqam: model o'quv to'plamining bir qismini "
               "yodlab olgan. Bugun uzoqroq o'qitishdan oldin ko'proq laboratoriya va skanerlardan slayd yig'gan bo'lardim, natijani esa bitta aniqlik "
               "raqami bilan emas, avvalo confusion matrix bilan ko'rsatgan bo'lardim.",
               "Разрыв между 97% на обучающих снимках и 89% на новых — самая честная цифра этого проекта: часть обучающей выборки модель просто "
               "запомнила. Сегодня я бы до более долгого обучения собрал стёкла из большего числа лабораторий и сканеров, а результат показывал бы "
               "сначала матрицей ошибок, а не одной цифрой точности.")),
        ],
        "images": [
            ("prostate-gleason-app.png",
             L("Desktop app showing a biopsy image with detected Grade 3 regions and a written conclusion",
               "Grade 3 hududlari aniqlangan biopsiya tasviri va xulosasi ko'rsatilgan desktop dastur",
               "Десктоп-приложение со снимком биопсии, найденными участками Grade 3 и заключением"),
             L("The diagnosis app: original image, detected regions and the conclusion",
               "Tashxis dasturi: asl tasvir, aniqlangan hududlar va xulosa",
               "Программа диагностики: исходный снимок, найденные участки и заключение")),
            ("prostate-gleason-dataset.jpg",
             L("Grid of labelled biopsy images with Gleason grade boxes",
               "Gleason darajasi bilan belgilangan biopsiya tasvirlari",
               "Размеченные снимки биопсии с рамками степеней Глисона"),
             L("Part of the labelled dataset", "Belgilangan datasetning bir qismi", "Часть размеченного датасета")),
            ("prostate-gleason-labels.png",
             L("Bar chart of instances per class and scatter plots of box positions and sizes",
               "Sinflar bo'yicha namunalar soni va ramkalar joylashuvi hamda o'lchamlari grafiklari",
               "Количество примеров по классам и распределение положения и размеров рамок"),
             L("Label statistics: examples per class, box positions and sizes",
               "Belgilar statistikasi: har sinfdagi namunalar, ramkalar joylashuvi va o'lchami",
               "Статистика разметки: примеры по классам, положение и размеры рамок")),
        ],
    },
]


class Command(BaseCommand):
    help = "Add the restaurant ERP and live truck map, rewrite the medical AI project."

    @transaction.atomic
    def handle(self, *args, **options):
        missing = [i[0] for p in PROJECTS for i in p["images"] if not (ASSETS / i[0]).exists()]
        if missing:
            self.stderr.write(f"Missing files in {ASSETS}: {', '.join(missing)}")
            return

        for name, slug, category in NEW_TECH:
            Technology.objects.get_or_create(slug=slug, defaults={"name": name, "category": category})
        techs = {t.name: t for t in Technology.objects.all()}

        for data in PROJECTS:
            self._project(data, techs)

        removed = ProjectImage.objects.filter(project__slug="fleet-asset-platform",
                                              image__contains="fleet-trucks-board").delete()[0]
        self.stdout.write(f"· FleetOps: removed Trucks board screenshot ({removed})")

        for i, slug in enumerate(ORDER, 1):
            Project.objects.filter(slug=slug).update(order=i, is_featured=slug in FEATURED)
        self.stdout.write(self.style.SUCCESS("Done."))

    def _project(self, data, techs):
        fields = {"title": data["title"], "organisation": data["organisation"], "status": data["status"],
                  "is_published": True, "is_confidential": data["confidential"], "repo_url": "",
                  "year_started": data["year_started"], "year_finished": data["year_finished"],
                  "team_size": data["team_size"]}
        for key in ("tagline", "role", "summary", "context"):
            if key in data:
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

        project.images.all().delete()
        for order, (filename, alt, caption) in enumerate(data["images"]):
            img = ProjectImage(project=project, order=order, is_primary=(order == 0),
                               **lang_fields("alt_text", alt), **lang_fields("caption", caption))
            with open(ASSETS / filename, "rb") as fh:
                img.image.save(filename, File(fh), save=False)
            img.save()
        self.stdout.write(f"· {'created' if created else 'updated'} {project.title}")
