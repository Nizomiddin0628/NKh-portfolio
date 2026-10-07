# Loyiha demolari (jonli SVG sahnalar)

Har bir loyiha kartochkasida statik rasm o'rniga loyihaning o'zi ishlab turgan mini-sahnasi o'ynaydi. Loyiha sahifasida o'sha sahna kattaroq ko'rinishda, qadamlar izohi bilan chiqadi.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| `static/js/demos/engine.js` | Dvigatel: lazy import, ko'rinmasa pauza, karuselda faqat faol karta, `prefers-reduced-motion` uchun statik kadr |
| `static/js/demos/<slug>.js` | Bitta loyiha sahnasi (`build` + `play`, `i18n` en/uz/ru) |
| `static/css/demos.css` | Sahna ranglari (sayt tokenlaridan), loyiha sahifasidagi panel |
| `static/js/demos/map-kit.js` | Xarita sahnalari uchun: proyeksiya, yo'llar, Interstate belgilari, Leaflet tugmalari, pin va markerlar |
| `static/js/demos/contact-flow.js` | Contact sahifasi: xabar formadan serverga, Telegram'ga va javob sifatida qaytib kelishi |
| `apps/core/templatetags/site_extras.py` | `DEMO_SLUGS` va `has_demo` filtri |

Sahna mavjud bo'lgan loyihalar: smart-yard-gate-automation, medical-ai-cancer-detection, ai-portfolio-assistant, driver-drowsiness-detector, restaurant-erp, ai-kotib-restaurant, live-truck-map, roadside-service-locator. Qolgan loyihalarda avvalgidek muqova rasmi chiqadi.

## Yangi sahna qo'shish

1. `static/js/demos/<slug>.js` yarating (mavjudlaridan birini namuna qiling). U `{ duration, rest, i18n, build(svg, kit, t), play(api, scene, t) }` ni eksport qiladi.
2. `play` ichida oddiy ketma-ket hikoya yoziladi: `await api.wait(ms)`, `await api.tween(el, keyframes, {dur})`, `api.type`, `api.count`, `api.draw`, `api.step(i)` (izoh qatori), `api.poster()` (statik kadr shu yerda to'xtaydi).
3. `DEMO_SLUGS` ga slug qo'shing.
4. `duration` — bitta sikl uzunligi (ms). Karusel nuqtasi shu vaqt ichida to'ladi, keyingi kartaga esa sahna `demo:end` bergandan keyin o'tadi.

## Kesh

`base.html` dagi import map (`{% module_importmap %}`) `static/js` dagi barcha modullarni xeshli URL'larga yo'naltiradi. Shu tufayli deploy'dan keyin brauzer eski `ui.js` yoki demo faylini keshdan bermaydi. Yangi JS fayl qo'shilsa, alohida hech narsa qilish shart emas: `collectstatic` uni o'zi map'ga qo'shadi.

## Qoidalar

- Sahna "multfilm" emas, haqiqiy mahsulotning o'zi kabi ko'rinsin: haqiqiy UI (oyna sarlavhasi, Leaflet tugmalari, Telegram ranglari, OpenCV/matplotlib oynalari), haqiqiy geografiya, kamera kadri uchun shovqin va vinyetka. Sakrab chiqadigan `scale(0.4)` kabi effektlardan foydalanmang, harakat sokin bo'lsin.
- Xarita zoom bo'lganda faqat asosiy qatlam kattalashadi (`vector-effect: non-scaling-stroke`). Yozuvlar, pinlar va markerlar har kadrda qayta proyeksiya qilinadi, shuning uchun o'lchami o'zgarmaydi.
- `transform` atributi bilan joylashtirilgan guruhni `api.show()` bilan chiqarmang, chunki CSS `transform` atributni bosib ketadi. Faqat opacity tween ishlating.

- Koordinatalar `viewBox="0 0 400 250"`. Telefonda karta ~330 px bo'ladi, shuning uchun matn kamida 9–10 birlik bo'lsin.
- Ranglar faqat klasslar orqali beriladi (`d-card`, `d-tx`, `d-acc`, `s-tq` …). Atribut ichida `var(--…)` ishlamaydi, kerak bo'lsa `style` dan foydalaning.
- SVG elementlarida `transform="rotate(a x y)"` ishlatilmaydi, chunki CSS `transform-origin` uni buzadi. Uning o'rniga `style: "transform: rotate(…deg)"` yozing.
- Klass nomlari saytning global klasslari bilan to'qnashmasin: `mono` emas, `dm` (sayt `.mono` klassi `font-size` ni ham o'zgartiradi).
- Cheksiz fon animatsiyalari faqat `api.loop` / `api.spawn` orqali yoziladi, shunda ular pauza va to'xtatishga bo'ysunadi.
