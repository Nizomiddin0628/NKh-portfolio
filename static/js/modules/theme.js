/**
 * Dark / light rejim.
 *
 * Almashish View Transitions API orqali: tugma bosilgan nuqtadan doira
 * kengayib butun ekranni qoplaydi. Brauzer qo'llab-quvvatlamasa yoki
 * foydalanuvchi harakatni o'chirgan bo'lsa — oddiy, bir zumda almashadi.
 */
const KEY = "theme";
const root = document.documentElement;

const reduced = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function initTheme() {
  const btn = document.querySelector("[data-theme-toggle]");
  if (!btn) return;

  /** Haqiqiy o'zgarish — DOM'ni yangilaydi, animatsiyasiz. */
  const set = (value) => {
    root.dataset.theme = value;
    btn.setAttribute("aria-label",
      value === "dark" ? "Switch to light mode" : "Switch to dark mode");
    btn.setAttribute("aria-pressed", String(value === "dark"));
    document.querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", value === "dark" ? "#0c1220" : "#f7f8fa");
  };

  set(root.dataset.theme || "light");

  const apply = (value, event) => {
    if (!document.startViewTransition || reduced()) return set(value);

    // Doira markazi — tugma bosilgan joy
    const rect = btn.getBoundingClientRect();
    const x = event?.clientX || rect.left + rect.width / 2;
    const y = event?.clientY || rect.top + rect.height / 2;

    // Ekranning eng uzoq burchagigacha bo'lgan masofa
    const radius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y),
    );

    root.dataset.themeSwitching = "true";
    const transition = document.startViewTransition(() => set(value));

    transition.ready.then(() => {
      root.animate(
        {
          clipPath: [
            `circle(0px at ${x}px ${y}px)`,
            `circle(${radius}px at ${x}px ${y}px)`,
          ],
        },
        {
          duration: 620,
          easing: "cubic-bezier(0.16, 1, 0.3, 1)",
          pseudoElement: "::view-transition-new(root)",
        },
      );
    });

    transition.finished.finally(() => delete root.dataset.themeSwitching);
  };

  btn.addEventListener("click", (e) => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem(KEY, next); } catch { /* private mode */ }
    apply(next, e);
  });

  // Foydalanuvchi qo'lda tanlamagan bo'lsa — tizim sozlamasiga ergashamiz
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    let stored = null;
    try { stored = localStorage.getItem(KEY); } catch { /* noop */ }
    if (!stored) set(e.matches ? "dark" : "light");
  });
}