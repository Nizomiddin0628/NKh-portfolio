/**
 * Mobil va planshet uchun loyihalar karuseli.
 *
 * Asosi — CSS `scroll-snap`. Barmoq bilan surish, inersiya va qatorga
 * "yopishish" brauzerning o'zida bajariladi; u JS bilan yozilgan har qanday
 * karuseldan silliqroq ishlaydi va Lenis bilan to'qnashmaydi.
 *
 * JS faqat uchta narsa qiladi:
 *   1. Markazdagi kartochkani belgilaydi (IntersectionObserver)
 *   2. Oldinga/orqaga tugmalarini boshqaradi
 *   3. Nuqtalar va hisoblagichni yangilaydi
 *
 * Keng ekranda karusel o'chadi — u yerda CSS kartochkalarni to'r qilib
 * joylashtiradi. DOM bir xil qoladi, faqat ko'rinish o'zgaradi.
 */

const QUERY = "(max-width: 899px)";

export function initCarousel() {
  document.querySelectorAll("[data-carousel]").forEach(setup);
}

function setup(root) {
  const track = root.querySelector("[data-carousel-track]");
  const items = [...root.querySelectorAll("[data-carousel-item]")];
  if (!track || items.length < 2) return;

  const prev = root.querySelector("[data-carousel-prev]");
  const next = root.querySelector("[data-carousel-next]");
  const dotsBox = root.querySelector("[data-carousel-dots]");
  const counter = root.querySelector("[data-carousel-counter]");

  let index = 0;
  let observer = null;
  const mq = window.matchMedia(QUERY);

  /* ── Nuqtalar ── */
  const dots = items.map((_, i) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "carousel__dot";
    dot.setAttribute("aria-label", `${i + 1}`);
    dot.addEventListener("click", () => goTo(i));
    dotsBox?.append(dot);
    return dot;
  });

  function paint() {
    items.forEach((item, i) => item.classList.toggle("is-active", i === index));
    dots.forEach((dot, i) => dot.setAttribute("aria-current", String(i === index)));

    if (counter) {
      counter.textContent =
        `${String(index + 1).padStart(2, "0")} / ${String(items.length).padStart(2, "0")}`;
    }

    // Chekkaga yetganda tugmani o'chiramiz — bosilmaydigan tugma
    // bosiladiganday ko'rinib turishi foydalanuvchini chalg'itadi.
    if (prev) prev.disabled = index === 0;
    if (next) next.disabled = index === items.length - 1;
  }

  function goTo(i) {
    index = Math.max(0, Math.min(i, items.length - 1));
    const item = items[index];
    // `scrollIntoView` o'rniga qo'lda hisoblash: sahifa vertikal
    // sakramasligi uchun faqat gorizontal skroll o'zgaradi.
    track.scrollTo({
      left: item.offsetLeft - (track.clientWidth - item.clientWidth) / 2,
      behavior: "smooth",
    });
    paint();
  }

  /* ── Markazdagi kartochkani aniqlash ── */
  function observe() {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const i = items.indexOf(entry.target);
          if (i >= 0 && i !== index) {
            index = i;
            paint();
          }
        });
      },
      { root: track, threshold: 0.6 },
    );
    items.forEach((item) => observer.observe(item));
  }

  function enable() {
    root.dataset.carouselActive = "true";
    if (!observer) observe();
    paint();
  }

  function disable() {
    root.dataset.carouselActive = "false";
    observer?.disconnect();
    observer = null;
    items.forEach((item) => item.classList.remove("is-active"));
  }

  prev?.addEventListener("click", () => goTo(index - 1));
  next?.addEventListener("click", () => goTo(index + 1));

  // Klaviatura bilan ham yurish mumkin
  track.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { e.preventDefault(); goTo(index + 1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); goTo(index - 1); }
  });

  mq.matches ? enable() : disable();
  mq.addEventListener("change", (e) => (e.matches ? enable() : disable()));
}