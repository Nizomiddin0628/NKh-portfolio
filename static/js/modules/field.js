/**
 * Fon gradienti sichqoncha ortidan sekin suriladi.
 *
 * Ikki qatlam: doimiy sinusoidal siljish (sahifa tinch turganda ham
 * jonli ko'rinadi) + kursorga tortilish. Ikkalasi bitta rAF ichida —
 * CSS animatsiyasi bilan ziddiyat bo'lmasligi uchun.
 */
export function initField() {
  const field = document.querySelector(".field");
  if (!field) return;

  const blobs = [...field.querySelectorAll(".field__blob")];
  if (!blobs.length) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const fine = window.matchMedia("(pointer: fine)").matches;
  field.dataset.js = "true"; // CSS keyframe'lari o'chadi

  let tx = 0.5, ty = 0.45;
  let cx = 0.5, cy = 0.45;
  let running = true;

  if (fine) {
    window.addEventListener("pointermove", (e) => {
      tx = e.clientX / window.innerWidth;
      ty = e.clientY / window.innerHeight;
    }, { passive: true });
  }

  const tick = (now) => {
    if (!running) return;

    cx += (tx - cx) * 0.035;
    cy += (ty - cy) * 0.035;

    const t = now / 1000;
    const dx = (cx - 0.5) * 2;
    const dy = (cy - 0.45) * 2;

    blobs[0].style.transform =
      `translate3d(${dx * 70 + Math.sin(t * 0.14) * 45}px,` +
      ` ${dy * 55 + Math.cos(t * 0.11) * 35}px, 0)` +
      ` scale(${1 + Math.sin(t * 0.09) * 0.07})`;

    if (blobs[1]) {
      blobs[1].style.transform =
        `translate3d(${dx * -90 + Math.cos(t * 0.1) * 55}px,` +
        ` ${dy * -70 + Math.sin(t * 0.13) * 40}px, 0)` +
        ` scale(${1.05 + Math.cos(t * 0.12) * 0.08})`;
    }

    requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);

  // Sahifa fonda turganda hisoblashni to'xtatamiz
  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) requestAnimationFrame(tick);
  });
}