/**
 * Loyihalar ro'yxati: qator ustiga kelganda o'ngda rasm ko'rinadi.
 *
 * Rasm ataylab sichqoncha ostida emas, o'ngdagi bo'sh ustunda turadi.
 * Kursor ostidagi variant chiroyliroq ko'rinadi, lekin u sarlavhani
 * berkitadi — foydalanuvchi aynan o'qimoqchi bo'lgan matnni. Shu sababli
 * rasm faqat vertikal siljiydi: qaysi qator faol ekani ko'rinib turadi,
 * matn esa hech qachon yopilmaydi.
 */
export function initPreview() {
  const list = document.querySelector("[data-preview-list]");
  const layer = document.querySelector("[data-preview-layer]");
  if (!list || !layer) return;

  const fine = window.matchMedia("(pointer: fine)").matches;
  const wide = window.matchMedia("(min-width: 1100px)").matches;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!fine || !wide || reduced || !window.gsap) return;

  const { gsap } = window;
  list.dataset.previewActive = "true";

  const images = [...layer.querySelectorAll("[data-preview-image]")];
  const rows = [...list.querySelectorAll("[data-preview-row]")];
  if (!images.length || !rows.length) return;

  let active = -1;

  gsap.set(images, { autoAlpha: 0, scale: 0.94 });
  gsap.set(layer, { autoAlpha: 0 });

  // Rasm faol qator balandligiga sinxron siljiydi
  const setY = gsap.quickTo(layer, "y", { duration: 0.5, ease: "power3.out" });

  function show(index) {
    if (active === index) return;

    if (active >= 0) {
      gsap.to(images[active], {
        autoAlpha: 0, scale: 0.96, duration: 0.3, ease: "power2.out",
      });
    }

    active = index;

    const row = rows[index];
    const listBox = list.getBoundingClientRect();
    const rowBox = row.getBoundingClientRect();
    // Rasm markazi qator markaziga to'g'ri keladi
    setY(rowBox.top - listBox.top + rowBox.height / 2 - layer.offsetHeight / 2);

    gsap.to(layer, { autoAlpha: 1, duration: 0.25, ease: "power2.out" });
    gsap.to(images[index], {
      autoAlpha: 1, scale: 1, duration: 0.45, ease: "power3.out",
    });
  }

  function hide() {
    if (active >= 0) {
      gsap.to(images[active], {
        autoAlpha: 0, scale: 0.96, duration: 0.3, ease: "power2.out",
      });
    }
    gsap.to(layer, { autoAlpha: 0, duration: 0.25, ease: "power2.out" });
    active = -1;
  }

  rows.forEach((row, i) => {
    row.addEventListener("pointerenter", () => show(i));
    // Klaviatura bilan yurganda ham ishlasin
    row.addEventListener("focus", () => show(i));
  });

  list.addEventListener("pointerleave", hide);
  list.addEventListener("focusout", (e) => {
    if (!list.contains(e.relatedTarget)) hide();
  });
}