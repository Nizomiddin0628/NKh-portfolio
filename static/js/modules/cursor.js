/**
 * Maxsus kursor: markazda nuqta, atrofida orqada qoladigan halqa.
 *
 * Faqat sichqonchali qurilmalarda. Sensorli ekranda ham,
 * `prefers-reduced-motion` yoqilganda ham umuman yaratilmaydi —
 * shuning uchun DOM'da keraksiz element qolmaydi.
 */
export function initCursor() {
  const fine = window.matchMedia("(pointer: fine)").matches;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!fine || reduced) return;

  const dot = document.createElement("div");
  dot.className = "cursor cursor--dot";
  const ring = document.createElement("div");
  ring.className = "cursor cursor--ring";
  const label = document.createElement("span");
  label.className = "cursor__label";
  ring.append(label);
  document.body.append(dot, ring);
  document.documentElement.classList.add("has-cursor");

  let mx = innerWidth / 2, my = innerHeight / 2;
  let rx = mx, ry = my;

  const tick = () => {
    rx += (mx - rx) * 0.16;
    ry += (my - ry) * 0.16;
    dot.style.transform = `translate3d(${mx}px, ${my}px, 0) translate(-50%, -50%)`;
    ring.style.transform = `translate3d(${rx}px, ${ry}px, 0) translate(-50%, -50%)`;
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);

  window.addEventListener("pointermove", (e) => {
    mx = e.clientX;
    my = e.clientY;
    document.documentElement.classList.add("cursor-active");
  }, { passive: true });

  document.addEventListener("pointerleave", () =>
    document.documentElement.classList.remove("cursor-active"));

  // Element ustida kursor o'zgaradi
  const INTERACTIVE = "a, button, input, textarea, select, [role='button']";

  document.addEventListener("pointerover", (e) => {
    const zone = e.target.closest("[data-cursor]");
    if (zone) {
      ring.dataset.mode = zone.dataset.cursor;
      label.textContent = zone.dataset.cursorLabel || "";
      return;
    }
    if (e.target.closest(INTERACTIVE)) {
      ring.dataset.mode = "link";
      label.textContent = "";
    }
  });

  document.addEventListener("pointerout", (e) => {
    if (e.relatedTarget?.closest?.("[data-cursor]") ||
        e.relatedTarget?.closest?.(INTERACTIVE)) return;
    ring.dataset.mode = "";
    label.textContent = "";
  });

  document.addEventListener("pointerdown", () => ring.dataset.pressed = "true");
  document.addEventListener("pointerup", () => ring.dataset.pressed = "false");
}