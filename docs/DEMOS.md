# Loyiha demolari (jonli SVG sahnalar)

Har bir loyiha kartochkasida statik rasm o'rniga loyihaning o'zi ishlab turgan mini-sahnasi o'ynaydi. Loyiha sahifasida o'sha sahna kattaroq ko'rinishda, qadamlar izohi bilan chiqadi.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| `static/js/demos/engine.js` | Dvigatel: lazy import, ko'rinmasa pauza, karuselda faqat faol karta, `prefers-reduced-motion` uchun statik kadr |
| `static/js/demos/<slug>.js` | Bitta loyiha sahnasi (`build` + `play`, `i18n` en/uz/ru) |
| `static/css/demos.css` | Sahna ranglari (sayt tokenlaridan), loyiha sahifasidagi panel |
| `apps/core/templatetags/site_extras.py` | `DEMO_SLUGS` va `has_demo` filtri |

Sahna mavjud bo'lgan loyihalar: smart-yard-gate-automation, medical-ai-cancer-detection, ai-portfolio-assistant, driver-drowsiness-detector, restaurant-erp, ai-kotib-restaurant, live-truck-map, roadside-service-locator. Qolgan loyihalarda avvalgidek muqova rasmi chiqadi.

## Yangi sahna qo'shish

1. `static/js/demos/<slug>.js` yarating (mavjudlaridan birini namuna qiling). U `{ duration, rest, i18n, build(svg, kit, t), play(api, scene, t) }` ni eksport qiladi.
2. `play` ichida oddiy ketma-ket hikoya yoziladi: `await api.wait(ms)`, `await api.tween(el, keyframes, {dur})`, `api.type`, `api.count`, `api.draw`, `api.step(i)` (izoh qatori), `api.poster()` (statik kadr shu yerda to'xtaydi).
3. `DEMO_SLUGS` ga slug qo'shing.
4. `duration` — bitta sikl uzunligi (ms). Karusel nuqtasi shu vaqt ichida to'ladi, keyingi kartaga esa sahna `demo:end` bergandan keyin o'tadi.

## Qoidalar

- Koordinatalar `viewBox="0 0 400 250"`. Telefonda karta ~330 px bo'ladi, shuning uchun matn kamida 9–10 birlik bo'lsin.
- Ranglar faqat klasslar orqali beriladi (`d-card`, `d-tx`, `d-acc`, `s-tq` …). Atribut ichida `var(--…)` ishlamaydi, kerak bo'lsa `style` dan foydalaning.
- SVG elementlarida `transform="rotate(a x y)"` ishlatilmaydi, chunki CSS `transform-origin` uni buzadi. Uning o'rniga `style: "transform: rotate(…deg)"` yozing.
- Klass nomlari saytning global klasslari bilan to'qnashmasin: `mono` emas, `dm` (sayt `.mono` klassi `font-size` ni ham o'zgartiradi).
- Cheksiz fon animatsiyalari faqat `api.loop` / `api.spawn` orqali yoziladi, shunda ular pauza va to'xtatishga bo'ysunadi.
