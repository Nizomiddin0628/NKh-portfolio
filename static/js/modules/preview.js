/**
 * Loyihalar ro'yxati: qator ustiga kelganda rasm sichqoncha ortidan chiqadi.
 *
 * Nega kartochkalar o'rniga qator: 10 ta loyihani bir ekranda ko'rish va
 * sarlavhalarni tez o'qib chiqish mumkin. Rasm faqat qiziqqan odam uchun
 * chiqadi — ya'ni sahifa yengil bo'ladi, lekin vizual qism yo'qolmaydi.
 *
 * Sensorli ekranda umuman ishga tushmaydi: u yerda hover degan tushuncha yo'q,
 * shuning uchun rasmlar qatorlarning ichida statik ko'rinadi (CSS orqali).
 */
export function initPreview() {
  const list = document.querySelector("[data-preview-list]");
  const layer = document.querySelector("[data-preview-layer]");
  if (!list || !layer) return;

  const fine = window.matchMedia("(pointer: fine)").matches;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!fine || reduced || !window.gsap) return;

  const { gsap } = window;
  list.dataset.previewActive = "true";

  const images = [...layer.querySelectorAll("[data-preview-image]")];
  const rows = [...list.querySelectorAll("[data-preview-row]")];
  let active = -1;

  gsap.set(images, { autoAlpha: 0, scale: 0.9, yPercent: 6 });

  // Sichqoncha pozitsiyasini kechikish bilan kuzatamiz — "og'irlik" hissi
  const setX = gsap.quickTo(layer, "x", { duration: 0.55, ease: "power3.out" });
  const setY = gsap.quickTo(layer, "y", { duration: 0.55, ease: "power3.out" });
  const setRot = gsap.quickTo(layer, "rotation", { duration: 0.8, ease: "power3.out" });

  let lastX = 0;

  list.addEventListener("pointermove", (e) => {
    const bounds = list.getBoundingClientRect();
    setX(e.clientX - bounds.left);
    setY(e.clientY - bounds.top);

    // Tez harakatda rasm biroz egiladi
    const velocity = gsap.utils.clamp(-12, 12, (e.clientX - lastX) * 0.6);
    setRot(velocity);
    lastX = e.clientX;
  });

  rows.forEach((row, i) => {
    row.addEventListener("pointerenter", () => {
      if (active === i) return;

      if (active >= 0) {
        gsap.to(images[active], {
          autoAlpha: 0, scale: 0.92, duration: 0.35, ease: "power2.out",
        });
      }

      active = i;
      gsap.to(images[i], {
        autoAlpha: 1, scale: 1, yPercent: 0,
        duration: 0.55, ease: "power3.out",
      });
      row.dataset.hover = "true";
    });

    row.addEventListener("pointerleave", () => (row.dataset.hover = "false"));
  });

  list.addEventListener("pointerleave", () => {
    if (active >= 0) {
      gsap.to(images[active], {
        autoAlpha: 0, scale: 0.9, duration: 0.4, ease: "power2.out",
      });
    }
    active = -1;
  });
}