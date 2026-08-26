"""Boshlang'ich kontent.

MUHIM: bu yerdagi matnlar — siz bergan ma'lumotlar asosida yozilgan qoralama.
Sanalar, kompaniya nomi va ba'zi raqamlar (TODO bilan belgilangan) sizda
aniqroq. Ularni admin panelda tuzatib chiqing — kodga qaytish shart emas.
"""

SITE = {
    "full_name": "Nizomiddin Xalilov",
    "job_title": "Backend & Computer Vision Engineer",
    "location": "Tashkent, Uzbekistan",
    "email": "",           # TODO: admin panelda to'ldiring
    "phone": "",           # TODO
    "github_username": "",  # TODO
    "availability": "open",
    "headline_en": "I build systems that watch, decide and act — without a human in the loop.",
    "headline_uz": "Men kuzatadigan, qaror qabul qiladigan va inson aralashuvisiz ishlaydigan tizimlar quraman.",
    "headline_de": "Ich baue Systeme, die beobachten, entscheiden und handeln — ohne menschliches Zutun.",
    "headline_ru": "Я строю системы, которые наблюдают, принимают решения и действуют без участия человека.",
    "intro_en": (
        "Python and Django on the backend, YOLO and OpenCV on the camera side. "
        "Today I run the internal platforms of a US-market logistics operation: 3,400 trucks, "
        "800 trailers, seven live camera feeds and a gate that opens by itself."
    ),
    "intro_uz": (
        "Backend tomonda Python va Django, kamera tomonda YOLO va OpenCV. "
        "Hozir AQSH bozorida ishlaydigan logistika kompaniyasining ichki platformalarini olib boraman: "
        "3 400 yuk mashinasi, 800 tirkama, 7 ta jonli kamera oqimi va o'zi ochiladigan shlagbaum."
    ),
    "intro_de": (
        "Python und Django im Backend, YOLO und OpenCV auf der Kameraseite. "
        "Aktuell betreue ich die internen Plattformen eines Logistikunternehmens für den US-Markt: "
        "3.400 Lkw, 800 Auflieger und sieben Live-Kamerastreams."
    ),
    "intro_ru": (
        "Python и Django на бэкенде, YOLO и OpenCV на стороне камер. "
        "Сейчас веду внутренние платформы логистической компании, работающей на рынке США: "
        "3 400 тягачей, 800 прицепов и семь живых видеопотоков."
    ),
    "availability_note_en": "Open to backend and computer vision roles",
    "availability_note_uz": "Backend va computer vision yo'nalishidagi takliflarga ochiq",
    "availability_note_de": "Offen für Backend- und Computer-Vision-Rollen",
    "availability_note_ru": "Открыт к предложениям в backend и computer vision",
    "meta_description_en": (
        "Nizomiddin Xalilov — backend and computer vision engineer. Django, PostgreSQL, "
        "YOLO and OpenCV systems running in production for US logistics."
    ),
    "meta_description_uz": (
        "Nizomiddin Xalilov — backend va computer vision muhandisi. Django, PostgreSQL, "
        "YOLO va OpenCV asosidagi tizimlar."
    ),
    "about_en": """I am a backend engineer who ended up in computer vision because the problems in front of me needed both.

My daily work is inside a logistics company serving the US market. The trucks are real, the yard is real, and when a system misfires a driver waits at a closed gate. That constraint shaped how I build: I care less about elegant abstractions than about what happens at 3 a.m. when nobody is watching the dashboard.

**Where I am strongest.** Django and PostgreSQL for systems that hold operational truth — fleets, assets, contracts, invoices. Python and YOLO/OpenCV when the input is a camera instead of a form. The interesting part is usually where the two meet: a model reads a plate, an API confirms the carrier, a barrier opens.

**How I got here.** Computer Engineering at Fergana State Technical University, graduating with a 4.5/5.0 GPA. My thesis was a YOLOv5 model for detecting cancer markers in medical scans — work that later received a grant from the Silk Road Health Data Science community. Medical imaging taught me something logistics reinforced: a false negative and a false positive are not the same mistake, and the threshold is a business decision, not a technical one.

**What I am working on now.** Deepening my systems side — deployment, observability, making sure the thing I built can be handed to someone else. And German, slowly.""",
    "about_uz": """Men backend muhandisiman, computer vision'ga esa oldimdagi masalalar ikkovini ham talab qilgani uchun kelib qoldim.

Kundalik ishim — AQSH bozorida ishlaydigan logistika kompaniyasi ichida. Yuk mashinalari haqiqiy, hovli haqiqiy, va tizim xato qilsa haydovchi yopiq shlagbaum oldida turib qoladi. Shu cheklov meni shakllantirdi: men chiroyli abstraksiyalardan ko'ra, kechasi soat 3 da hech kim panelga qaramayotganda nima bo'lishi haqida ko'proq o'ylayman.

**Eng kuchli tomonim.** Operatsion haqiqatni saqlaydigan tizimlar uchun Django va PostgreSQL — parklar, aktivlar, shartnomalar, hisob-fakturalar. Kirish ma'lumoti forma emas, kamera bo'lganda — Python va YOLO/OpenCV. Eng qiziq joyi odatda shu ikkisi uchrashadigan nuqta: model raqamni o'qiydi, API tashuvchini tasdiqlaydi, to'siq ochiladi.

**Qanday keldim.** Farg'ona davlat texnika universitetida "Kompyuter injiniringi", 4.5/5.0 GPA bilan. Bitiruv ishim — tibbiy skanerlarda saraton belgilarini aniqlash uchun YOLOv5 modeli; keyinchalik bu ish Silk Road Health Data Science hamjamiyati grantiga sazovor bo'ldi. Tibbiy tasvirlar menga logistika keyinchalik takrorlagan narsani o'rgatdi: false negative va false positive bir xil xato emas, va chegara qiymati texnik emas, biznes qarori.

**Hozir nima ustida ishlayapman.** Tizim tomonimni chuqurlashtiryapman — deploy, observability, qurgan narsamni boshqa odamga topshira olish. Va sekin-asta nemis tili.""",
    "work_philosophy_en": (
        "Three habits that survived contact with production."
    ),
    "work_philosophy_uz": (
        "Ishlab chiqarish bilan to'qnashuvdan omon qolgan uchta odat."
    ),
}

PRINCIPLES = [
    {
        "title_en": "Measure before you optimise",
        "title_uz": "Optimallashdan oldin o'lchang",
        "body_en": "Every performance claim in these case studies started as a number I wrote down before touching the code. Without a baseline, 'faster' is an opinion.",
        "body_uz": "Bu case study'lardagi har bir tezlik da'vosi kodga tegishdan oldin yozib olingan raqamdan boshlangan. Boshlang'ich o'lchovsiz 'tezroq' — bu shunchaki fikr.",
    },
    {
        "title_en": "Design for the failure, not the demo",
        "title_uz": "Demo uchun emas, nosozlik uchun loyihalang",
        "body_en": "A camera goes dark, an API times out, a plate is covered in mud. The interesting engineering is what the system does then — not what it does on a clear day.",
        "body_uz": "Kamera o'chadi, API javob bermaydi, raqam loyga belangan. Qiziqarli muhandislik — tizim aynan shunda nima qilishi, ochiq kunda nima qilishida emas.",
    },
    {
        "title_en": "Hand it over cleanly",
        "title_uz": "Toza qilib topshiring",
        "body_en": "If a system needs me in the room to keep running, it is not finished. Admin panels, README files and honest logs are part of the deliverable.",
        "body_uz": "Agar tizim ishlashi uchun men xonada bo'lishim kerak bo'lsa — u tugallanmagan. Admin panel, README va halol loglar ham topshiriq qismi.",
    },
]

TECHNOLOGIES = [
    ("Python", "python", "language"), ("JavaScript", "javascript", "language"),
    ("SQL", "sql", "language"),
    ("Django", "django", "backend"), ("Django REST Framework", "drf", "backend"),
    ("REST API", "rest-api", "backend"), ("Celery", "celery", "backend"),
    ("PostgreSQL", "postgresql", "data"), ("Pandas", "pandas", "data"),
    ("NumPy", "numpy", "data"), ("Redis", "redis", "data"),
    ("YOLOv11", "yolov11", "ai"), ("YOLOv5", "yolov5", "ai"),
    ("OpenCV", "opencv", "ai"), ("PyTorch", "pytorch", "ai"),
    ("MediaPipe", "mediapipe", "ai"), ("RTSP", "rtsp", "ai"),
    ("Docker", "docker", "infra"), ("Linux", "linux", "infra"),
    ("Nginx", "nginx", "infra"), ("Git", "git", "tool"),
    ("FMCSA API", "fmcsa-api", "tool"), ("Motive API", "motive-api", "tool"),
    ("Google Maps API", "google-maps-api", "tool"),
]

SKILL_GROUPS = [
    {
        "name_en": "Backend", "name_uz": "Backend", "name_de": "Backend", "name_ru": "Бэкенд",
        "note_en": "Where I spend most of my time",
        "note_uz": "Vaqtimning katta qismi shu yerda",
        "skills": [("Python", "core"), ("Django", "core"), ("Django REST Framework", "core"),
                   ("PostgreSQL", "core"), ("REST API design", "strong"), ("Celery", "strong"),
                   ("Redis", "strong")],
    },
    {
        "name_en": "Computer vision & AI", "name_uz": "Computer vision va AI",
        "name_de": "Computer Vision & KI", "name_ru": "Computer vision и ИИ",
        "note_en": "Production, not notebooks",
        "note_uz": "Notebook emas, ishlab chiqarish",
        "skills": [("YOLOv5 / YOLOv11", "core"), ("OpenCV", "core"), ("PyTorch", "strong"),
                   ("MediaPipe", "strong"), ("OCR / plate recognition", "strong"),
                   ("RTSP stream handling", "strong")],
    },
    {
        "name_en": "Data", "name_uz": "Ma'lumotlar", "name_de": "Daten", "name_ru": "Данные",
        "skills": [("Pandas", "core"), ("NumPy", "strong"), ("SQL optimisation", "strong"),
                   ("ETL pipelines", "strong")],
    },
    {
        "name_en": "Infrastructure", "name_uz": "Infratuzilma",
        "name_de": "Infrastruktur", "name_ru": "Инфраструктура",
        "note_en": "Also my day job as sysadmin",
        "note_uz": "Bu ayni paytda tizim administratori sifatidagi ishim ham",
        "skills": [("Linux", "core"), ("Docker", "strong"), ("Nginx", "strong"),
                   ("Gunicorn", "strong"), ("Networking / VPN", "working"),
                   ("Windows Server", "working")],
    },
    {
        "name_en": "Frontend", "name_uz": "Frontend", "name_de": "Frontend", "name_ru": "Фронтенд",
        "note_en": "Enough to ship a full product alone",
        "note_uz": "Mahsulotni yolg'iz yetkazishga yetadigan darajada",
        "skills": [("JavaScript (ES6+)", "strong"), ("HTML / CSS", "strong"),
                   ("Django templates", "strong")],
    },
]

LANGUAGES = [
    {"name_en": "Uzbek", "name_uz": "O'zbek", "name_de": "Usbekisch", "name_ru": "Узбекский",
     "level_en": "Native", "level_uz": "Ona tili", "level_de": "Muttersprache", "level_ru": "Родной"},
    {"name_en": "English", "name_uz": "Ingliz", "name_de": "Englisch", "name_ru": "Английский",
     "level_en": "IELTS 6.0 · B2", "level_uz": "IELTS 6.0 · B2",
     "level_de": "IELTS 6.0 · B2", "level_ru": "IELTS 6.0 · B2"},
    {"name_en": "Russian", "name_uz": "Rus", "name_de": "Russisch", "name_ru": "Русский",
     "level_en": "Fluent", "level_uz": "Erkin", "level_de": "Fließend", "level_ru": "Свободно"},
    {"name_en": "German", "name_uz": "Nemis", "name_de": "Deutsch", "name_ru": "Немецкий",
     "level_en": "A2 → B1, in progress", "level_uz": "A2 → B1, o'rganilmoqda",
     "level_de": "A2 → B1, im Aufbau", "level_ru": "A2 → B1, изучаю"},
]

EDUCATION = [
    {
        "institution": "Fergana State Technical University",
        "location": "Fergana, Uzbekistan",
        "degree_en": "BSc, Computer Engineering",
        "degree_uz": "Bakalavr, Kompyuter injiniringi",
        "degree_de": "B.Sc. Technische Informatik",
        "degree_ru": "Бакалавр, компьютерная инженерия",
        "field_of_study_en": "Computer Engineering",
        "field_of_study_uz": "Kompyuter injiniringi",
        "grade": "GPA 4.5 / 5.0",
        "start_year": 2020,  # TODO: aniq yilni tekshiring
        "end_year": 2024,    # TODO
        "note_en": "Thesis: a YOLOv5-based detector for cancer markers in medical scans.",
        "note_uz": "Bitiruv ishi: tibbiy skanerlarda saraton belgilarini aniqlovchi YOLOv5 modeli.",
    },
]

AWARDS = [
    {
        "title_en": "Research grant — Silk Road Health Data Science",
        "title_uz": "Ilmiy grant — Silk Road Health Data Science",
        "title_de": "Forschungsstipendium — Silk Road Health Data Science",
        "title_ru": "Исследовательский грант — Silk Road Health Data Science",
        "issuer": "Silk Road Health Data Science",
        "year": 2024,  # TODO
        "description_en": "Awarded for the graduation project on automated cancer marker detection in medical imaging.",
        "description_uz": "Tibbiy tasvirlarda saraton belgilarini avtomatik aniqlash bo'yicha bitiruv loyihasi uchun.",
    },
]

EXPERIENCE = [
    {
        "company": "International logistics company (US market)",  # TODO: haqiqiy nom
        "location": "Remote · US market",
        "role_en": "Python Developer · System Administrator · IT Support",
        "role_uz": "Python dasturchi · Tizim administratori · IT Support",
        "role_de": "Python-Entwickler · Systemadministrator · IT-Support",
        "role_ru": "Python-разработчик · Системный администратор · IT-поддержка",
        "employment_type_en": "Full-time",
        "employment_type_uz": "To'liq stavka",
        "employment_type_de": "Vollzeit",
        "employment_type_ru": "Полная занятость",
        "start_date": "2024-01-01",  # TODO: aniq sana
        "end_date": None,
        "summary_en": (
            "I own the internal engineering of a fleet operating 3,400+ trucks and 800+ trailers: "
            "the asset platform, the yard automation, the safety scoring and the toll reconciliation. "
            "Alongside that I keep the office infrastructure running."
        ),
        "summary_uz": (
            "3 400 dan ortiq yuk mashinasi va 800 dan ortiq tirkamali parkning ichki muhandisligi "
            "menda: aktivlar platformasi, hovli avtomatikasi, xavfsizlik ballari va yo'l to'lovlari "
            "hisob-kitobi. Shu bilan birga ofis infratuzilmasini ham olib boraman."
        ),
        "bullets": [
            {"text_en": "Built the automated gate system: seven live camera feeds, YOLOv11 detection, plate/USDOT/unit OCR and FMCSA carrier verification — the barrier opens with no operator involved.",
             "text_uz": "Avtomatik shlagbaum tizimini qurdim: 7 ta jonli kamera oqimi, YOLOv11 aniqlash, davlat raqami/USDOT/unit OCR va FMCSA orqali tashuvchini tekshirish — to'siq operatorsiz ochiladi."},
            {"text_en": "Replaced the fleet's Google Sheets workflow with a Django + PostgreSQL platform covering trucks, trailers, ELDs, fuel cards and tablets.",
             "text_uz": "Parkning Google Sheets jarayonini Django + PostgreSQL platformasi bilan almashtirdim: yuk mashinalari, tirkamalar, ELD, yoqilg'i kartalari va planshetlar."},
            {"text_en": "Integrated the Motive API to collect daily driver safety events and compute safety scores in near real time.",
             "text_uz": "Motive API'ni integratsiya qilib, haydovchilarning kunlik xavfsizlik hodisalarini yig'ish va ballarni deyarli real vaqtda hisoblashni yo'lga qo'ydim."},
            {"text_en": "Automated toll invoice parsing and cost allocation across partner companies with a Pandas/PostgreSQL pipeline.",
             "text_uz": "Yo'l to'lovi hisob-fakturalarini tahlil qilish va hamkor kompaniyalar bo'yicha taqsimlashni Pandas/PostgreSQL pipeline bilan avtomatlashtirdim."},
            {"text_en": "Shipped a roadside service locator that finds the nearest repair shops and pilot services within a 150-mile radius, ranked by past outcomes.",
             "text_uz": "Yo'lda nosozlik yuz berganda 150 milya radiusidagi eng yaqin ustaxona va pilot xizmatlarini topadigan, o'tgan natijalar bo'yicha saralaydigan modulni ishga tushirdim."},
            {"text_en": "Maintain office IT: workstations, accounts, network and the internal tooling other teams depend on.",
             "text_uz": "Ofis IT infratuzilmasi menda: ish stantsiyalari, hisoblar, tarmoq va boshqa jamoalar tayanadigan ichki vositalar."},
        ],
    },
]


PROJECTS = [
    {
        "title": "Smart Yard — Automated Gate Control",
        "slug": "smart-yard-gate-automation",
        "organisation": "International logistics company",
        "year_started": 2024, "year_finished": 2025, "status": "production",
        "is_featured": True, "order": 1, "is_confidential": True,
        "team_size": 1,
        "tagline_en": "Seven camera feeds, one decision: open the gate or don't. No operator in the loop.",
        "tagline_uz": "7 ta kamera oqimi, bitta qaror: shlagbaumni ochish yoki ochmaslik. Operator qatnashmaydi.",
        "tagline_de": "Sieben Kamerastreams, eine Entscheidung: Schranke öffnen oder nicht — ohne Operator.",
        "tagline_ru": "Семь видеопотоков, одно решение: открыть шлагбаум или нет. Без оператора.",
        "role_en": "Computer vision + backend + deployment",
        "role_uz": "Computer vision + backend + deploy",
        "role_de": "Computer Vision + Backend + Deployment",
        "role_ru": "Computer vision + бэкенд + деплой",
        "context_en": "Built and deployed solo, running against live yard traffic.",
        "context_uz": "Yolg'iz qurilgan va joriy etilgan, jonli hovli harakati ustida ishlaydi.",
        "summary_en": (
            "A truck pulls up to the yard. Seven cameras see it from different angles. The system decides "
            "what it is — tractor, trailer or car — reads the plate, the USDOT number and the unit number, "
            "checks the carrier against the FMCSA registry, and either raises the barrier or leaves it down. "
            "The whole loop runs without a person watching."
        ),
        "summary_uz": (
            "Yuk mashinasi hovliga yaqinlashadi. 7 ta kamera uni turli burchakdan ko'radi. Tizim nima ekanini "
            "aniqlaydi — tortuvchi, tirkama yoki yengil avtomobil — davlat raqamini, USDOT va unit raqamini "
            "o'qiydi, tashuvchini FMCSA reyestridan tekshiradi va to'siqni ko'taradi yoki ko'tarmaydi. "
            "Butun sikl inson nazoratisiz ishlaydi."
        ),
        "technologies": ["Python", "YOLOv11", "OpenCV", "Django", "PostgreSQL", "RTSP",
                         "FMCSA API", "Docker", "Linux"],
        "metrics": [
            {"label_en": "Gate handling", "label_uz": "Shlagbaum boshqaruvi",
             "value_before": "manual", "value_after": "autonomous",
             "note_en": "Operator only reviews exceptions", "note_uz": "Operator faqat istisnolarni ko'radi"},
            {"label_en": "Camera feeds processed", "label_uz": "Qayta ishlanadigan kamera oqimlari",
             "value_after": "7 live", "note_en": "Concurrent, on one machine", "note_uz": "Bitta mashinada, parallel"},
            {"label_en": "Identifiers read per vehicle", "label_uz": "Har bir mashinadan o'qiladigan identifikatorlar",
             "value_after": "3", "note_en": "Plate, USDOT, unit number", "note_uz": "Raqam, USDOT, unit raqami"},
        ],
        "sections": [
            {"kind": "problem", "order": 1,
             "heading_en": "A gate that needed a human at 3 a.m.",
             "heading_uz": "Kechasi soat 3 da odam talab qiladigan shlagbaum",
             "body_en": (
                 "The yard gate was operated by hand. Someone had to look at the truck, read the plate, check "
                 "whether that carrier was allowed in, and press a button. That works during the day. It works "
                 "badly at night, and it does not work at all when the person steps away.\n\n"
                 "The cost was not only labour. Every manual check is a place where the wrong truck gets waved "
                 "through and the right one waits."
             ),
             "body_uz": (
                 "Hovli darvozasi qo'lda boshqarilardi. Kimdir mashinaga qarab, raqamni o'qib, bu tashuvchiga "
                 "ruxsat bor-yo'qligini tekshirib, tugmani bosishi kerak edi. Kunduzi bu ishlaydi. Kechasi yomon "
                 "ishlaydi. Odam joyida bo'lmasa — umuman ishlamaydi.\n\n"
                 "Xarajat faqat ish haqida emas edi. Har bir qo'lda tekshiruv — noto'g'ri mashina o'tib ketishi "
                 "va to'g'risi kutib qolishi mumkin bo'lgan nuqta."
             )},
            {"kind": "constraints", "order": 2,
             "heading_en": "What I could not change",
             "heading_uz": "Men o'zgartira olmagan narsalar",
             "body_en": (
                 "- **The cameras were already installed.** Seven feeds, fixed positions, mixed angles. No budget "
                 "to reposition them for a nicer dataset.\n"
                 "- **One machine.** All seven streams had to be processed on existing hardware.\n"
                 "- **Real weather.** Mud on plates, low sun, rain at night, snow. The demo conditions were the "
                 "exception, not the rule.\n"
                 "- **A wrong 'open' is worse than a wrong 'wait'.** An unauthorised truck inside the yard is a "
                 "security incident; a driver waiting 40 extra seconds is an annoyance."
             ),
             "body_uz": (
                 "- **Kameralar allaqachon o'rnatilgan edi.** 7 ta oqim, qat'iy joylashuv, turli burchaklar. "
                 "Chiroyliroq dataset uchun ularni ko'chirishga byudjet yo'q.\n"
                 "- **Bitta mashina.** Yettala oqim ham mavjud jihozda qayta ishlanishi kerak edi.\n"
                 "- **Haqiqiy ob-havo.** Raqamdagi loy, past quyosh, kechqurungi yomg'ir, qor. Demo sharoiti — "
                 "istisno, qoida emas.\n"
                 "- **Noto'g'ri 'ochish' noto'g'ri 'kutish'dan yomonroq.** Ruxsatsiz mashina hovli ichida — "
                 "xavfsizlik hodisasi; 40 soniya kutgan haydovchi — shunchaki noqulaylik."
             )},
            {"kind": "decision", "order": 3,
             "heading_en": "Decisions, and what I rejected",
             "heading_uz": "Qarorlar va nimani rad etdim",
             "body_en": (
                 "**Detection and reading are separate stages.** YOLOv11 answers *what and where*; a cropped "
                 "region then goes to OCR for *which one*. Merging them into a single model would have been "
                 "elegant and much harder to debug when a plate is misread.\n\n"
                 "**Multiple frames, not one.** A decision is never made on a single frame. The vehicle is "
                 "tracked across the approach and identifiers are voted on across frames. This is the single "
                 "change that moved the system from 'promising' to 'usable' — mud and glare are frame-local, "
                 "consensus is not.\n\n"
                 "**FMCSA is the source of truth, but not a blocker.** The carrier lookup runs against the "
                 "FMCSA API and is cached. If the API is slow or down, the system falls back to the local "
                 "cache and flags the entry rather than freezing the gate.\n\n"
                 "**Rejected: cloud inference.** Sending seven video streams out and waiting for a verdict adds "
                 "latency I cannot control and a bill that scales with traffic. Everything runs on site."
             ),
             "body_uz": (
                 "**Aniqlash va o'qish — alohida bosqichlar.** YOLOv11 *nima va qayerda* degan savolga javob "
                 "beradi; kesilgan qism keyin OCR'ga borib *qaysi biri* ekanini aytadi. Ularni bitta modelga "
                 "qo'shish chiroyli bo'lardi, lekin raqam noto'g'ri o'qilganda tuzatish ancha qiyin bo'lardi.\n\n"
                 "**Bitta kadr emas, bir nechta.** Qaror hech qachon bitta kadr asosida qabul qilinmaydi. "
                 "Mashina yaqinlashish davomida kuzatiladi va identifikatorlar kadrlar bo'ylab ovoz berish "
                 "orqali aniqlanadi. Tizimni 'istiqbolli' holatidan 'ishlatsa bo'ladigan' holatga o'tkazgan "
                 "yagona o'zgarish shu bo'ldi — loy va yarqirash bitta kadrga tegishli, konsensus esa yo'q.\n\n"
                 "**FMCSA — haqiqat manbasi, lekin to'siq emas.** Tashuvchi tekshiruvi FMCSA API orqali "
                 "boradi va keshlanadi. API sekinlashsa yoki ishlamasa, tizim lokal keshga qaytadi va "
                 "shlagbaumni qotirib qo'ymay, yozuvni belgilab qo'yadi.\n\n"
                 "**Rad etilgan: cloud inference.** 7 ta video oqimni tashqariga yuborib javob kutish — men "
                 "boshqara olmaydigan kechikish va harakat hajmiga qarab o'sadigan hisob. Hamma narsa "
                 "joyning o'zida ishlaydi."
             )},
            {"kind": "architecture", "order": 4,
             "heading_en": "How it fits together",
             "heading_uz": "Qismlar qanday bog'langan",
             "body_en": (
                 "```\nRTSP × 7  →  frame sampler  →  YOLOv11 detector\n"
                 "                                    ↓ (crops)\n"
                 "                              OCR: plate · USDOT · unit\n"
                 "                                    ↓\n"
                 "                       multi-frame consensus + tracker\n"
                 "                                    ↓\n"
                 "         FMCSA lookup (cached)  →  decision engine  →  barrier relay\n"
                 "                                    ↓\n"
                 "                          Django + PostgreSQL (event log, review UI)\n```\n\n"
                 "Every decision writes an event: the frames it used, what it read, what FMCSA returned and why "
                 "it opened or did not. When someone asks *why did that truck get in*, there is an answer."
             ),
             "body_uz": (
                 "```\nRTSP × 7  →  kadr tanlagich  →  YOLOv11 detektor\n"
                 "                                     ↓ (kesilgan qismlar)\n"
                 "                              OCR: raqam · USDOT · unit\n"
                 "                                     ↓\n"
                 "                       ko'p kadrli konsensus + tracker\n"
                 "                                     ↓\n"
                 "         FMCSA tekshiruvi (kesh)  →  qaror moduli  →  shlagbaum relesi\n"
                 "                                     ↓\n"
                 "                        Django + PostgreSQL (hodisalar jurnali, ko'rib chiqish UI)\n```\n\n"
                 "Har bir qaror hodisa sifatida yoziladi: qaysi kadrlar ishlatilgani, nima o'qilgani, FMCSA "
                 "nima qaytargani va nega ochilgani yoki ochilmagani. Kimdir *nega u mashina kirdi* deb "
                 "so'raganda javob bor."
             )},
            {"kind": "result", "order": 5,
             "heading_en": "Where it stands",
             "heading_uz": "Hozirgi holati",
             "body_en": (
                 "The gate runs unattended. Operators moved from *watching every truck* to *reviewing the "
                 "exceptions the system flagged* — unreadable plates, carriers missing from the registry, "
                 "vehicles that do not match their paperwork.\n\n"
                 "The event log turned out to be as valuable as the automation. It answers questions nobody "
                 "could answer before: which carriers arrive late, how long trucks sit at the gate, which "
                 "camera angle produces the most failed reads."
             ),
             "body_uz": (
                 "Shlagbaum nazoratsiz ishlaydi. Operatorlar *har bir mashinani kuzatish*dan *tizim belgilagan "
                 "istisnolarni ko'rib chiqish*ga o'tdi — o'qib bo'lmaydigan raqamlar, reyestrda topilmagan "
                 "tashuvchilar, hujjatiga mos kelmaydigan mashinalar.\n\n"
                 "Hodisalar jurnali avtomatika kabi qimmatli bo'lib chiqdi. U ilgari hech kim javob bera "
                 "olmagan savollarga javob beradi: qaysi tashuvchilar kechikadi, mashinalar darvozada qancha "
                 "turadi, qaysi kamera burchagi eng ko'p muvaffaqiyatsiz o'qishga sabab bo'ladi."
             )},
            {"kind": "retro", "order": 6,
             "heading_en": "What I would do differently",
             "heading_uz": "Nimani boshqacha qilardim",
             "body_en": (
                 "I built the review interface last. That was backwards. For the first weeks the only way to "
                 "understand a bad read was to dig through logs and re-run frames by hand — the UI that made "
                 "debugging cheap should have existed on day one.\n\n"
                 "I would also collect the hard cases from the start. The mud, glare and night frames that "
                 "broke the model are exactly the training data I needed, and for the first month I was "
                 "discarding them instead of saving them."
             ),
             "body_uz": (
                 "Ko'rib chiqish interfeysini eng oxirida qurdim. Bu teskari tartib edi. Dastlabki haftalarda "
                 "xato o'qishni tushunishning yagona yo'li loglarni titish va kadrlarni qo'lda qayta "
                 "ishlatish edi — nosozlikni arzon qiladigan UI birinchi kunidan bo'lishi kerak edi.\n\n"
                 "Shuningdek, qiyin holatlarni boshidan yig'gan bo'lardim. Modelni buzgan loyli, yarqiragan va "
                 "tungi kadrlar — aynan menga kerak bo'lgan o'quv ma'lumoti; birinchi oy davomida men ularni "
                 "saqlash o'rniga tashlab yuborardim."
             )},
        ],
    },
    {
        "title": "Fleet & Asset Management Platform",
        "slug": "fleet-asset-platform",
        "organisation": "International logistics company",
        "year_started": 2024, "year_finished": 2026, "status": "production",
        "is_featured": True, "order": 2, "is_confidential": True, "team_size": 1,
        "tagline_en": "3,400 trucks, 800 trailers and every device attached to them — moved off spreadsheets and into a system that reminds you before the lease expires.",
        "tagline_uz": "3 400 yuk mashinasi, 800 tirkama va ularga biriktirilgan har bir qurilma — jadvallardan chiqib, ijara muddati tugashidan oldin ogohlantiradigan tizimga o'tdi.",
        "tagline_de": "3.400 Lkw, 800 Auflieger und jedes zugehörige Gerät — raus aus Tabellen, rein in ein System, das vor Vertragsende erinnert.",
        "tagline_ru": "3 400 тягачей, 800 прицепов и все привязанные устройства — из таблиц в систему, которая напомнит до окончания аренды.",
        "role_en": "Backend, data model, admin tooling",
        "role_uz": "Backend, ma'lumotlar modeli, admin vositalari",
        "role_de": "Backend, Datenmodell, Admin-Werkzeuge",
        "role_ru": "Бэкенд, модель данных, админ-инструменты",
        "summary_en": (
            "The company ran its entire fleet on Google Sheets. Which truck has which ELD, whose fuel card is "
            "in which cab, when a lease ends, what a unit earned last month — all of it lived in tabs that "
            "several people edited at once. I replaced it with a Django and PostgreSQL platform where an asset "
            "has one record, one owner and one history."
        ),
        "summary_uz": (
            "Kompaniya butun parkni Google Sheets'da yuritardi. Qaysi mashinada qaysi ELD bor, kimning "
            "yoqilg'i kartasi qaysi kabinada, ijara qachon tugaydi, unit o'tgan oyda qancha daromad keltirdi — "
            "bularning hammasi bir vaqtning o'zida bir necha odam tahrirlaydigan varaqlarda edi. Men buni "
            "Django va PostgreSQL platformasi bilan almashtirdim: har bir aktivning bitta yozuvi, bitta egasi "
            "va bitta tarixi bor."
        ),
        "technologies": ["Django", "PostgreSQL", "Python", "Celery", "Redis", "Pandas", "REST API"],
        "metrics": [
            {"label_en": "Trucks tracked", "label_uz": "Kuzatiladigan mashinalar",
             "value_before": "spreadsheet", "value_after": "3,400+"},
            {"label_en": "Trailers tracked", "label_uz": "Kuzatiladigan tirkamalar",
             "value_before": "spreadsheet", "value_after": "800+"},
            {"label_en": "Lease expiry surprises", "label_uz": "Kutilmagan ijara tugashi",
             "value_before": "found late", "value_after": "flagged early",
             "note_en": "Automatic reminders before the date", "note_uz": "Sana yetmasdan avtomatik eslatma"},
        ],
        "sections": [
            {"kind": "problem", "order": 1,
             "heading_en": "The spreadsheet was the system of record",
             "heading_uz": "Jadval — yagona rasmiy manba edi",
             "body_en": (
                 "Not a report *about* the fleet — the fleet itself existed as rows in Google Sheets. That has "
                 "predictable consequences: two people edit the same cell, a truck goes inactive but its ELD "
                 "and fuel card stay assigned to it, a lease quietly expires, and nobody can reconstruct who "
                 "changed what.\n\n"
                 "The failure that finally forced the rebuild was equipment: devices staying with vehicles that "
                 "had left the fleet. Paid for, assigned to nothing, invisible."
             ),
             "body_uz": (
                 "Bu park *haqidagi* hisobot emas edi — parkning o'zi Google Sheets qatorlari sifatida mavjud "
                 "edi. Buning oqibatlari oldindan ma'lum: ikki kishi bitta katakni tahrirlaydi, mashina faol "
                 "bo'lmay qoladi-yu, ELD va yoqilg'i kartasi unga biriktirilgan qolaveradi, ijara sezdirmay "
                 "tugaydi, va kim nimani o'zgartirganini hech kim tiklay olmaydi.\n\n"
                 "Qayta qurishga majbur qilgan holat — uskunalar edi: parkdan chiqib ketgan mashinalarda "
                 "qolib ketgan qurilmalar. Puli to'langan, hech narsaga biriktirilmagan, ko'rinmaydigan."
             )},
            {"kind": "constraints", "order": 2,
             "heading_en": "Migrating a live fleet",
             "heading_uz": "Ishlab turgan parkni ko'chirish",
             "body_en": (
                 "- **No downtime.** Dispatch runs around the clock; there is no weekend to migrate on.\n"
                 "- **Dirty data.** Years of free-text entry: the same carrier spelled four ways, dates in three "
                 "formats, unit numbers with and without prefixes.\n"
                 "- **Non-technical users.** The people entering data are dispatchers, not engineers. If the new "
                 "system is slower to use than a spreadsheet, they will keep the spreadsheet."
             ),
             "body_uz": (
                 "- **To'xtatib bo'lmaydi.** Dispetcherlik kechayu kunduz ishlaydi; ko'chirish uchun dam olish "
                 "kuni yo'q.\n"
                 "- **Iflos ma'lumot.** Yillar davomida erkin matn kiritilgan: bitta tashuvchi to'rt xil "
                 "yozilgan, sanalar uch formatda, unit raqamlari prefiksli va prefikssiz.\n"
                 "- **Texnik bo'lmagan foydalanuvchilar.** Ma'lumot kiritadiganlar — dispetcherlar, muhandis "
                 "emas. Agar yangi tizimdan foydalanish jadvaldan sekinroq bo'lsa, ular jadvalda qolaveradi."
             )},
            {"kind": "decision", "order": 3,
             "heading_en": "Decisions, and what I rejected",
             "heading_uz": "Qarorlar va nimani rad etdim",
             "body_en": (
                 "**Assignment is an event, not a field.** A fuel card is not *on* a truck — it was assigned to "
                 "it on a date, and possibly returned on another. Modelling assignments as dated records instead "
                 "of foreign keys is what makes 'return equipment from inactive vehicles' a query rather than "
                 "a manual audit.\n\n"
                 "**Django admin as the primary interface.** I did not build a custom CRUD frontend. The admin, "
                 "configured properly — inlines, filters, search, bulk actions — was faster to ship and faster "
                 "for dispatchers to use than anything I would have written from scratch. I spent the saved "
                 "time on the parts that actually needed custom work: reminders and revenue calculation.\n\n"
                 "**Import, then reconcile.** Rather than cleaning the spreadsheets first, I imported them "
                 "as-is into a staging table and built a reconciliation screen showing conflicts. Cleaning data "
                 "you can see is far faster than cleaning data you are guessing about.\n\n"
                 "**Rejected: a full ERP product.** Evaluated, and it would have solved 60% of this at the cost "
                 "of fitting the company's process to the tool. The other 40% — yard, tolls, safety — is where "
                 "the actual leverage was."
             ),
             "body_uz": (
                 "**Biriktirish — bu maydon emas, hodisa.** Yoqilg'i kartasi mashinada *turmaydi* — u ma'lum "
                 "sanada biriktirilgan va, ehtimol, boshqa sanada qaytarilgan. Biriktirishlarni foreign key "
                 "emas, sanali yozuv sifatida modellashtirish 'faol bo'lmagan mashinalardan uskunani qaytarish' "
                 "vazifasini qo'lda auditdan oddiy so'rovga aylantiradi.\n\n"
                 "**Django admin — asosiy interfeys.** Men alohida CRUD frontend qurmadim. To'g'ri sozlangan "
                 "admin — inline'lar, filtrlar, qidiruv, ommaviy amallar — men noldan yozadigan har qanday "
                 "narsadan tezroq yetkazildi va dispetcherlar uchun tezroq bo'ldi. Tejalgan vaqtni haqiqatan "
                 "maxsus ish talab qilgan qismlarga sarfladim: eslatmalar va daromad hisobi.\n\n"
                 "**Avval import, keyin solishtirish.** Jadvallarni oldin tozalash o'rniga ularni borligicha "
                 "staging jadvalga yukladim va nizolarni ko'rsatadigan solishtirish ekranini qurdim. Ko'rib "
                 "turgan ma'lumotni tozalash — taxmin qilayotgan ma'lumotni tozalashdan ancha tez.\n\n"
                 "**Rad etilgan: tayyor ERP.** Ko'rib chiqildi va bu masalaning 60% ini hal qilardi, lekin "
                 "kompaniya jarayonini vositaga moslashtirish evaziga. Qolgan 40% — hovli, yo'l to'lovlari, "
                 "xavfsizlik — asosiy foyda aynan shu yerda edi."
             )},
            {"kind": "result", "order": 4,
             "heading_en": "What changed",
             "heading_uz": "Nima o'zgardi",
             "body_en": (
                 "Assets have a single record with a full history. Lease expiries surface as reminders before "
                 "the date rather than as a surprise after it. Monthly revenue per unit is calculated instead "
                 "of assembled by hand. Equipment attached to inactive vehicles is a report, so it gets "
                 "returned.\n\n"
                 "The quieter win: questions that used to require someone to open four tabs are now a filter."
             ),
             "body_uz": (
                 "Aktivlarning to'liq tarixli yagona yozuvi bor. Ijara tugashi sanadan keyingi kutilmagan "
                 "hodisa emas, undan oldingi eslatma sifatida chiqadi. Har bir unit bo'yicha oylik daromad "
                 "qo'lda yig'ilmaydi, hisoblanadi. Faol bo'lmagan mashinalardagi uskunalar — hisobot, shuning "
                 "uchun ular qaytarib olinadi.\n\n"
                 "Sokinroq yutuq: ilgari to'rtta varaqni ochishni talab qilgan savollar endi oddiy filtr."
             )},
            {"kind": "retro", "order": 5,
             "heading_en": "What I would do differently",
             "heading_uz": "Nimani boshqacha qilardim",
             "body_en": (
                 "I would model the assignment history from the first migration instead of adding it later. "
                 "Retrofitting dated records onto data that was stored as a single current value means the "
                 "history before the change is simply gone — I can tell you where every device is today and "
                 "where it has been since the rebuild, but not before it.\n\n"
                 "I would also involve two dispatchers in the design week, not the launch week. The three "
                 "changes they asked for after launch were all things they would have said at the start."
             ),
             "body_uz": (
                 "Biriktirish tarixini keyin qo'shish o'rniga birinchi migratsiyadanoq modellashtirgan "
                 "bo'lardim. Faqat joriy qiymat sifatida saqlangan ma'lumot ustiga sanali yozuvlarni keyin "
                 "qo'shish — o'zgarishdan oldingi tarix shunchaki yo'q degani. Men har bir qurilma bugun "
                 "qayerdaligini va qayta qurishdan beri qayerda bo'lganini ayta olaman, undan oldingisini yo'q.\n\n"
                 "Shuningdek, ikki dispetcherni ishga tushirish haftasida emas, loyihalash haftasida jalb "
                 "qilgan bo'lardim. Ular ishga tushgandan keyin so'ragan uchta o'zgarishning hammasini "
                 "boshida ham aytgan bo'lardi."
             )},
        ],
    },
    {
        "title": "Driver Safety Scoring & Toll Reconciliation",
        "slug": "driver-safety-and-toll-automation",
        "organisation": "International logistics company",
        "year_started": 2025, "year_finished": 2026, "status": "production",
        "is_featured": True, "order": 3, "is_confidential": True, "team_size": 1,
        "tagline_en": "Two automations that share a shape: pull messy external data on a schedule, turn it into a number someone can act on.",
        "tagline_uz": "Bitta shaklga ega ikki avtomatika: tartibsiz tashqi ma'lumotni jadval bo'yicha olib kelib, harakat qilsa bo'ladigan raqamga aylantirish.",
        "tagline_de": "Zwei Automatisierungen mit gleicher Form: unsaubere externe Daten regelmäßig holen und in handlungsfähige Zahlen verwandeln.",
        "tagline_ru": "Две автоматизации одной формы: регулярно забирать грязные внешние данные и превращать их в число, с которым можно работать.",
        "role_en": "Backend, API integration, data pipeline",
        "role_uz": "Backend, API integratsiya, ma'lumot pipeline'i",
        "role_de": "Backend, API-Integration, Datenpipeline",
        "role_ru": "Бэкенд, интеграция API, конвейер данных",
        "summary_en": (
            "Two problems the company solved by hand every week. Driver safety events arrived in Motive and were "
            "read one by one. Toll invoices arrived as documents and were split between partner companies with a "
            "calculator. Both are now pipelines: fetch, normalise, allocate, report."
        ),
        "summary_uz": (
            "Kompaniya har hafta qo'lda hal qilgan ikki masala. Haydovchilarning xavfsizlik hodisalari Motive'ga "
            "tushardi va birma-bir o'qilardi. Yo'l to'lovi hisob-fakturalari hujjat sifatida kelardi va hamkor "
            "kompaniyalar orasida kalkulyator bilan bo'linardi. Endi ikkalasi ham pipeline: olib kelish, "
            "normallashtirish, taqsimlash, hisobot."
        ),
        "technologies": ["Python", "Django", "PostgreSQL", "Pandas", "Celery", "Motive API", "REST API"],
        "metrics": [
            {"label_en": "Safety scoring", "label_uz": "Xavfsizlik bahosi",
             "value_before": "weekly, manual", "value_after": "near real time"},
            {"label_en": "Toll allocation", "label_uz": "Yo'l to'lovi taqsimoti",
             "value_before": "by hand", "value_after": "automatic",
             "note_en": "Per client and partner company", "note_uz": "Har bir mijoz va hamkor bo'yicha"},
        ],
        "sections": [
            {"kind": "problem", "order": 1,
             "heading_en": "Data that existed but could not be used",
             "heading_uz": "Mavjud, lekin ishlatib bo'lmaydigan ma'lumot",
             "body_en": (
                 "Motive already recorded every harsh brake, every speeding event, every distraction alert. The "
                 "data was there. What was missing was anything that turned thousands of individual events into "
                 "*this driver's trend is going the wrong way*.\n\n"
                 "Tolls had the opposite problem: the totals were obvious, the attribution was not. One invoice, "
                 "many trucks, several partner companies, and someone deciding by hand who pays for what."
             ),
             "body_uz": (
                 "Motive har bir keskin tormozlashni, har bir tezlik oshirishni, har bir chalg'ish "
                 "ogohlantirishini allaqachon yozib borardi. Ma'lumot bor edi. Minglab alohida hodisani "
                 "*bu haydovchining tendensiyasi noto'g'ri tomonga ketyapti* degan xulosaga aylantiradigan "
                 "narsa yo'q edi.\n\n"
                 "Yo'l to'lovlarida teskari muammo bor edi: umumiy summa aniq, kimga tegishli ekani noaniq. "
                 "Bitta hisob-faktura, ko'p mashina, bir nechta hamkor kompaniya va kim nima to'lashini qo'lda "
                 "hal qiladigan odam."
             )},
            {"kind": "decision", "order": 2,
             "heading_en": "Decisions, and what I rejected",
             "heading_uz": "Qarorlar va nimani rad etdim",
             "body_en": (
                 "**Store raw events, compute scores on top.** The scoring formula will change — management will "
                 "want harsh braking weighted differently next quarter. Raw events are permanent; scores are "
                 "derived and recomputable. Storing only the score would have made every formula change a data "
                 "loss.\n\n"
                 "**Idempotent syncs.** The Motive sync can run twice on the same window without double-counting. "
                 "This sounds obvious and is the thing that most often is not true in hand-rolled integrations — "
                 "and the reason a failed job can simply be re-run instead of investigated.\n\n"
                 "**Allocation rules live in the database, not the code.** Which partner pays for which unit is a "
                 "business arrangement that changes. Putting it in a table means finance updates it; putting it "
                 "in Python means I do.\n\n"
                 "**Rejected: real-time streaming.** Safety trends do not need sub-minute latency. A scheduled "
                 "pull is simpler, cheaper to reason about and survives an API outage by just running later."
             ),
             "body_uz": (
                 "**Xom hodisalarni saqlash, ballarni ustidan hisoblash.** Ball formulasi o'zgaradi — keyingi "
                 "chorakda rahbariyat keskin tormozlashga boshqacha vazn berishni xohlaydi. Xom hodisalar "
                 "doimiy; ballar hosila va qayta hisoblanadi. Faqat ballni saqlash har bir formula "
                 "o'zgarishini ma'lumot yo'qotishga aylantirardi.\n\n"
                 "**Idempotent sinxronizatsiya.** Motive sinxronizatsiyasi bitta oraliqda ikki marta ishlasa "
                 "ham ikki hisoblamaydi. Bu ravshan tuyuladi, lekin qo'lda yozilgan integratsiyalarda eng "
                 "ko'p buziladigan narsa aynan shu — va muvaffaqiyatsiz vazifani tekshirish o'rniga shunchaki "
                 "qayta ishga tushirish mumkinligining sababi.\n\n"
                 "**Taqsimlash qoidalari kodda emas, bazada.** Qaysi hamkor qaysi unit uchun to'lashi — "
                 "o'zgarib turadigan biznes kelishuvi. Uni jadvalga qo'yish moliya bo'limi yangilashini "
                 "anglatadi; Python'ga qo'yish esa men yangilashimni.\n\n"
                 "**Rad etilgan: real-time streaming.** Xavfsizlik tendensiyalariga bir daqiqadan kam "
                 "kechikish kerak emas. Jadval bo'yicha olib kelish soddaroq, tushunarliroq va API ishlamay "
                 "qolsa keyinroq ishga tushib omon qoladi."
             )},
            {"kind": "result", "order": 3,
             "heading_en": "Where it stands",
             "heading_uz": "Hozirgi holati",
             "body_en": (
                 "Safety managers see a current score per driver and the events behind it, instead of a weekly "
                 "PDF assembled by someone. Toll costs land on the right company without a spreadsheet in "
                 "between.\n\n"
                 "The unexpected outcome was disagreement becoming productive: when a driver disputes a score, "
                 "the conversation is now about specific events with timestamps rather than about the number."
             ),
             "body_uz": (
                 "Xavfsizlik menejerlari kimdir yig'gan haftalik PDF o'rniga har bir haydovchining joriy "
                 "balini va uning ortidagi hodisalarni ko'radi. Yo'l to'lovi xarajatlari oradagi jadvalsiz "
                 "to'g'ri kompaniyaga tushadi.\n\n"
                 "Kutilmagan natija — nizolar foydali bo'lib qoldi: haydovchi balga e'tiroz bildirganda, "
                 "suhbat endi raqam haqida emas, vaqt belgisi bor aniq hodisalar haqida boradi."
             )},
            {"kind": "retro", "order": 4,
             "heading_en": "What I would do differently",
             "heading_uz": "Nimani boshqacha qilardim",
             "body_en": (
                 "I would version the scoring formula from the beginning. When the weights changed, historical "
                 "scores were recomputed under the new rules — which is defensible, but it means a driver's "
                 "score from six months ago is not the score they were shown six months ago. Storing the formula "
                 "version alongside each computed score costs one column and prevents an argument."
             ),
             "body_uz": (
                 "Ball formulasini boshidan versiyalagan bo'lardim. Vaznlar o'zgarganda tarixiy ballar yangi "
                 "qoidalar bo'yicha qayta hisoblandi — buni himoya qilsa bo'ladi, lekin bu haydovchining olti "
                 "oy oldingi bali unga o'shanda ko'rsatilgan ball emasligini bildiradi. Har bir hisoblangan "
                 "ball yoniga formula versiyasini saqlash bitta ustunga tushadi va bahsning oldini oladi."
             )},
        ],
    },
    {
        "title": "Roadside Service Locator",
        "slug": "roadside-service-locator",
        "organisation": "International logistics company",
        "year_started": 2025, "year_finished": 2025, "status": "production",
        "is_featured": False, "order": 4, "is_confidential": True, "team_size": 1,
        "tagline_en": "A truck breaks down somewhere on an interstate. This finds the nearest shop that will actually help — and remembers whether it did.",
        "tagline_uz": "Mashina magistralning qayerdadir buzildi. Bu modul haqiqatan yordam beradigan eng yaqin ustaxonani topadi — va u yordam berganini eslab qoladi.",
        "tagline_de": "Ein Lkw fällt irgendwo auf der Interstate aus. Findet die nächste Werkstatt, die wirklich hilft — und merkt sich, ob sie es tat.",
        "tagline_ru": "Грузовик сломался где-то на трассе. Модуль находит ближайший сервис, который реально поможет — и запоминает результат.",
        "role_en": "Backend, geospatial queries, ranking",
        "role_uz": "Backend, geofazoviy so'rovlar, saralash",
        "summary_en": (
            "Given GPS coordinates, the module returns repair shops, pilot services and service points within a "
            "150-mile radius. The part that matters is not the search — it is that every call-out is scored "
            "afterwards, so the ranking improves with use."
        ),
        "summary_uz": (
            "GPS koordinatalari berilganda modul 150 milya radiusidagi ta'mirlash ustaxonalari, pilot xizmatlari "
            "va servis punktlarini qaytaradi. Muhimi qidiruv emas — har bir chaqiruv keyin baholanadi, shuning "
            "uchun saralash foydalanish davomida yaxshilanadi."
        ),
        "technologies": ["Django", "PostgreSQL", "Python", "Google Maps API", "REST API"],
        "metrics": [
            {"label_en": "Search radius", "label_uz": "Qidiruv radiusi", "value_after": "150 mi"},
            {"label_en": "Ranking input", "label_uz": "Saralash mezoni",
             "value_before": "distance only", "value_after": "distance + past outcome"},
        ],
        "sections": [
            {"kind": "problem", "order": 1,
             "heading_en": "The nearest shop is not the best shop",
             "heading_uz": "Eng yaqin ustaxona — eng yaxshisi emas",
             "body_en": (
                 "When a truck goes down, dispatch searches maps, calls numbers and hopes. Distance is the only "
                 "thing a map gives you, and distance is a weak predictor of whether a shop answers the phone at "
                 "11 p.m., has the part, or charges what it quoted.\n\n"
                 "That knowledge existed — in the heads of the dispatchers who had called before. It just was not "
                 "written down anywhere."
             ),
             "body_uz": (
                 "Mashina buzilganda dispetcher xaritadan qidiradi, raqamlarga qo'ng'iroq qiladi va umid "
                 "qiladi. Xarita beradigan yagona narsa — masofa, masofa esa ustaxona kechqurun soat 11 da "
                 "telefonni ko'taradimi, ehtiyot qismi bormi, aytgan narxida ishlaydimi — bularni juda yomon "
                 "bashorat qiladi.\n\n"
                 "Bu bilim mavjud edi — ilgari qo'ng'iroq qilgan dispetcherlarning boshida. Faqat hech qayerda "
                 "yozilmagan edi."
             )},
            {"kind": "decision", "order": 2,
             "heading_en": "Decisions",
             "heading_uz": "Qarorlar",
             "body_en": (
                 "**Capture the outcome, not just the search.** After every call-out, dispatch records what "
                 "happened: answered or not, fixed or not, price as quoted or not. Two fields at the end of an "
                 "incident turn a directory into something that learns.\n\n"
                 "**Rank on distance *and* history, weighted.** A shop 30 miles further that has never let anyone "
                 "down beats a nearer unknown. Both factors are visible in the result so dispatch can override.\n\n"
                 "**Cache aggressively.** The set of service points in a region barely changes week to week. "
                 "Hitting the maps API on every breakdown would be slow and expensive for no benefit."
             ),
             "body_uz": (
                 "**Faqat qidiruvni emas, natijani ham yozib olish.** Har bir chaqiruvdan keyin dispetcher nima "
                 "bo'lganini yozadi: javob berdimi, tuzatdimi, narx aytilganidek bo'ldimi. Hodisa oxiridagi "
                 "ikkita maydon oddiy ma'lumotnomani o'rganadigan tizimga aylantiradi.\n\n"
                 "**Masofa *va* tarix bo'yicha, vazn bilan saralash.** Hech qachon qo'ymagan, 30 milya uzoqdagi "
                 "ustaxona yaqindagi noma'lumdan afzal. Ikkala omil ham natijada ko'rinadi, shuning uchun "
                 "dispetcher o'z qarorini qo'ya oladi.\n\n"
                 "**Keshni qattiq ishlatish.** Mintaqadagi servis punktlari to'plami haftadan haftaga deyarli "
                 "o'zgarmaydi. Har bir nosozlikda xarita API'siga murojaat qilish sekin va qimmat bo'lardi."
             )},
            {"kind": "result", "order": 3,
             "heading_en": "Where it stands",
             "heading_uz": "Hozirgi holati",
             "body_en": (
                 "Dispatch starts from a ranked list instead of a map search. The institutional knowledge that "
                 "used to leave with an employee now stays in the database."
             ),
             "body_uz": (
                 "Dispetcher xaritadan qidirish o'rniga saralangan ro'yxatdan boshlaydi. Ilgari xodim bilan "
                 "birga ketib qoladigan bilim endi bazada qoladi."
             )},
            {"kind": "retro", "order": 4,
             "heading_en": "What I would do differently",
             "heading_uz": "Nimani boshqacha qilardim",
             "body_en": (
                 "The outcome form was optional at launch, so for the first weeks it was mostly skipped and the "
                 "ranking had nothing to learn from. Making it a required step to close an incident — one screen, "
                 "three taps — would have got the system useful a month earlier."
             ),
             "body_uz": (
                 "Natija formasi boshida ixtiyoriy edi, shuning uchun dastlabki haftalarda ko'pincha o'tkazib "
                 "yuborildi va saralash o'rganadigan narsa bo'lmadi. Uni hodisani yopish uchun majburiy "
                 "qadamga aylantirish — bitta ekran, uchta bosish — tizimni bir oy oldin foydali qilgan bo'lardi."
             )},
        ],
    },
    {
        "title": "Cancer Marker Detection in Medical Imaging",
        "slug": "medical-ai-cancer-detection",
        "organisation": "Fergana State Technical University · graduation research",
        "year_started": 2023, "year_finished": 2024, "status": "research",
        "is_featured": True, "order": 5, "team_size": 1,
        "tagline_en": "A YOLOv5 detector for cancer markers in medical scans. Graduation research, later supported by a Silk Road Health Data Science grant.",
        "tagline_uz": "Tibbiy skanerlarda saraton belgilarini aniqlovchi YOLOv5 modeli. Bitiruv ilmiy ishi, keyinchalik Silk Road Health Data Science granti bilan qo'llab-quvvatlangan.",
        "tagline_de": "Ein YOLOv5-Detektor für Krebsmarker in medizinischen Scans. Abschlussforschung, später durch ein Silk-Road-Stipendium gefördert.",
        "tagline_ru": "YOLOv5-детектор онкомаркеров на медицинских снимках. Дипломное исследование, поддержанное грантом Silk Road Health Data Science.",
        "role_en": "Research, model architecture, training",
        "role_uz": "Tadqiqot, model arxitekturasi, o'qitish",
        "role_de": "Forschung, Modellarchitektur, Training",
        "role_ru": "Исследование, архитектура модели, обучение",
        "summary_en": (
            "My thesis project: a neural network built on YOLOv5 and PyTorch that highlights regions in medical "
            "scans consistent with cancer markers. It is a screening aid — it narrows where a specialist looks, "
            "it does not diagnose."
        ),
        "summary_uz": (
            "Bitiruv ishim: YOLOv5 va PyTorch asosidagi neyrotarmoq tibbiy skanerlarda saraton belgilariga mos "
            "hududlarni ajratib ko'rsatadi. Bu skrining yordamchisi — mutaxassis qayerga qarashini toraytiradi, "
            "tashxis qo'ymaydi."
        ),
        "technologies": ["Python", "PyTorch", "YOLOv5", "OpenCV", "NumPy"],
        "sections": [
            {"kind": "problem", "order": 1,
             "heading_en": "Screening is attention-limited",
             "heading_uz": "Skrining — e'tibor bilan cheklangan jarayon",
             "body_en": (
                 "Reviewing scans is slow, and the cost of missing something is not symmetric with the cost of a "
                 "false alarm. The goal was never to replace the radiologist — it was to reduce the search space "
                 "before a human looks."
             ),
             "body_uz": (
                 "Skanerlarni ko'rib chiqish sekin, va biror narsani o'tkazib yuborish narxi yolg'on "
                 "signal narxiga teng emas. Maqsad hech qachon radiologni almashtirish bo'lmagan — inson "
                 "qarashidan oldin qidiruv maydonini toraytirish edi."
             )},
            {"kind": "constraints", "order": 2,
             "heading_en": "Constraints of student research",
             "heading_uz": "Talaba tadqiqotining cheklovlari",
             "body_en": (
                 "- **Limited annotated data.** Medical datasets are small, imbalanced and hard to obtain.\n"
                 "- **Class imbalance.** Positive cases are rare, which makes accuracy a useless metric — a model "
                 "that predicts 'negative' every time scores well and helps nobody.\n"
                 "- **A single GPU.** Training budget measured in hours, not cluster-days."
             ),
             "body_uz": (
                 "- **Cheklangan annotatsiyalangan ma'lumot.** Tibbiy datasetlar kichik, nomutanosib va olish qiyin.\n"
                 "- **Sinflar nomutanosibligi.** Musbat holatlar kam, shu sababli accuracy foydasiz o'lchov — "
                 "har safar 'salbiy' deb bashorat qiladigan model yaxshi ball oladi va hech kimga foyda bermaydi.\n"
                 "- **Bitta GPU.** O'qitish byudjeti klaster-kunlarda emas, soatlarda o'lchanadi."
             )},
            {"kind": "decision", "order": 3,
             "heading_en": "Decisions, and what I rejected",
             "heading_uz": "Qarorlar va nimani rad etdim",
             "body_en": (
                 "**Recall over precision, deliberately.** The threshold was tuned to favour catching a marker "
                 "and flagging extra regions over missing one. In a screening aid, a false positive costs a "
                 "second look; a false negative costs everything. This is a clinical decision expressed as a "
                 "number, and I documented it as such rather than reporting a single headline accuracy.\n\n"
                 "**Detection, not classification.** Localising *where* is more useful to a reviewer than a "
                 "whole-image yes/no, and it makes the model's reasoning visible.\n\n"
                 "**Rejected: training from scratch.** With the available data, transfer learning from "
                 "pretrained weights was the only honest option."
             ),
             "body_uz": (
                 "**Ataylab precision emas, recall.** Chegara qiymati belgini o'tkazib yuborishdan ko'ra "
                 "ortiqcha hududlarni belgilashga moyil qilib sozlangan. Skrining yordamchisida false "
                 "positive — ikkinchi marta qarash; false negative — hamma narsani yo'qotish. Bu raqam bilan "
                 "ifodalangan klinik qaror, va men uni bitta umumiy accuracy o'rniga aynan shunday hujjatlashtirdim.\n\n"
                 "**Klassifikatsiya emas, detektsiya.** *Qayerda* ekanini aniqlash ko'rib chiquvchi uchun butun "
                 "tasvir bo'yicha ha/yo'q javobidan foydaliroq va model mantiqini ko'rinadigan qiladi.\n\n"
                 "**Rad etilgan: noldan o'qitish.** Mavjud ma'lumot bilan oldindan o'qitilgan vaznlardan "
                 "transfer learning yagona halol variant edi."
             )},
            {"kind": "result", "order": 4,
             "heading_en": "Outcome",
             "heading_uz": "Natija",
             "body_en": (
                 "The work was defended as my graduation project and received a grant from the Silk Road Health "
                 "Data Science community.\n\n"
                 "What I carried into every project since: the threshold is a business decision. Somebody has to "
                 "decide which error is worse, and it is not the model."
             ),
             "body_uz": (
                 "Ish bitiruv loyihasi sifatida himoya qilindi va Silk Road Health Data Science hamjamiyatining "
                 "grantiga sazovor bo'ldi.\n\n"
                 "Shundan keyingi har bir loyihaga olib o'tgan xulosam: chegara qiymati — biznes qarori. "
                 "Qaysi xato yomonroq ekanini kimdir hal qilishi kerak, va bu model emas."
             )},
            {"kind": "retro", "order": 5,
             "heading_en": "What I would do differently",
             "heading_uz": "Nimani boshqacha qilardim",
             "body_en": (
                 "I would report the confusion matrix and the operating point from the first presentation, not "
                 "accuracy. Accuracy on an imbalanced medical dataset is close to meaningless, and leading with "
                 "it invites the wrong questions."
             ),
             "body_uz": (
                 "Birinchi taqdimotdanoq accuracy emas, confusion matrix va ishchi nuqtani ko'rsatgan bo'lardim. "
                 "Nomutanosib tibbiy datasetda accuracy deyarli ma'nosiz, va uni oldinga qo'yish noto'g'ri "
                 "savollarni keltirib chiqaradi."
             )},
        ],
    },
    {
        "title": "Driver Drowsiness Detector",
        "slug": "driver-drowsiness-detector",
        "organisation": "Personal project",
        "year_started": 2024, "year_finished": 2024, "status": "archived",
        "is_featured": False, "order": 6, "team_size": 1,
        "tagline_en": "Eye Aspect Ratio in real time from a webcam. When the eyes stay closed too long, it makes noise.",
        "tagline_uz": "Veb-kameradan real vaqtda Eye Aspect Ratio. Ko'zlar juda uzoq yumilib qolsa — signal beradi.",
        "tagline_de": "Eye Aspect Ratio in Echtzeit per Webcam. Bleiben die Augen zu lange geschlossen, schlägt es Alarm.",
        "tagline_ru": "Eye Aspect Ratio в реальном времени с веб-камеры. Если глаза закрыты слишком долго — сигнал.",
        "role_en": "Computer vision, everything",
        "role_uz": "Computer vision, hammasi",
        "summary_en": (
            "A small, focused computer vision tool: MediaPipe finds facial landmarks, OpenCV computes the eye "
            "aspect ratio frame by frame, and a sustained drop below threshold triggers an audio-visual alert."
        ),
        "summary_uz": (
            "Kichik va aniq maqsadli computer vision vositasi: MediaPipe yuz nuqtalarini topadi, OpenCV har "
            "kadrda ko'z nisbatini hisoblaydi, chegaradan uzoq vaqt past qolish audio-vizual signalni ishga "
            "tushiradi."
        ),
        "technologies": ["Python", "OpenCV", "MediaPipe", "NumPy"],
        "sections": [
            {"kind": "problem", "order": 1,
             "heading_en": "Why I built it",
             "heading_uz": "Nega qurdim",
             "body_en": (
                 "Working around long-haul logistics, driver fatigue is not an abstract topic. I wanted to know "
                 "how far a laptop webcam and classical computer vision could get without a trained model."
             ),
             "body_uz": (
                 "Uzoq masofali logistika atrofida ishlaganda haydovchi charchog'i mavhum mavzu emas. Men "
                 "o'qitilgan modelsiz, noutbuk kamerasi va klassik computer vision bilan qay darajaga borish "
                 "mumkinligini bilmoqchi edim."
             )},
            {"kind": "decision", "order": 2,
             "heading_en": "Decisions",
             "heading_uz": "Qarorlar",
             "body_en": (
                 "**Geometry instead of a trained classifier.** EAR is a ratio computed from six landmarks. No "
                 "dataset, no training, no GPU — and it runs at full frame rate on a laptop.\n\n"
                 "**Duration, not a single frame.** Blinking is a drop in EAR too. Only a sustained drop across "
                 "consecutive frames counts, which is the entire difference between a useful alert and a device "
                 "that beeps at every blink."
             ),
             "body_uz": (
                 "**O'qitilgan klassifikator emas, geometriya.** EAR — oltita nuqtadan hisoblanadigan nisbat. "
                 "Dataset yo'q, o'qitish yo'q, GPU yo'q — va noutbukda to'liq kadr tezligida ishlaydi.\n\n"
                 "**Bitta kadr emas, davomiylik.** Ko'z pirpiratish ham EAR pasayishi. Faqat ketma-ket "
                 "kadrlarda davom etgan pasayish hisobga olinadi — foydali ogohlantirish bilan har pirpirashda "
                 "chiyillaydigan qurilma o'rtasidagi butun farq shu."
             )},
            {"kind": "result", "order": 3,
             "heading_en": "Outcome",
             "heading_uz": "Natija",
             "body_en": (
                 "It works well in good light and degrades exactly where you would expect: glasses with glare, "
                 "darkness, a head turned away from the camera.\n\n"
                 "I keep it here because it is honest about its limits, and because the duration-threshold idea "
                 "is the same principle I later used for multi-frame consensus in the yard system."
             ),
             "body_uz": (
                 "Yaxshi yorug'likda yaxshi ishlaydi va aynan kutilgan joyda yomonlashadi: yarqiragan ko'zoynak, "
                 "qorong'ilik, kameradan burilgan bosh.\n\n"
                 "Buni shu yerda saqlayman, chunki u o'z chegaralari haqida halol, va davomiylik-chegarasi "
                 "g'oyasi keyinchalik hovli tizimida ko'p kadrli konsensus uchun ishlatgan printsipning aynan "
                 "o'zi."
             )},
        ],
    },
]
