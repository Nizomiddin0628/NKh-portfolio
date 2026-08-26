/** Dark / light rejim. Tanlov localStorage'da saqlanadi. */
const KEY = "theme";
const root = document.documentElement;

export function initTheme() {
  const btn = document.querySelector("[data-theme-toggle]");
  if (!btn) return;

  const apply = (value) => {
    root.dataset.theme = value;
    btn.setAttribute("aria-label", value === "dark" ? "Switch to light mode" : "Switch to dark mode");
    btn.setAttribute("aria-pressed", String(value === "dark"));
    document.querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", value === "dark" ? "#0c1220" : "#f7f8fa");
  };

  apply(root.dataset.theme || "light");

  btn.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem(KEY, next); } catch { /* private mode */ }
    apply(next);
  });

  // Foydalanuvchi qo'lda tanlamagan bo'lsa — tizim sozlamasiga ergashamiz.
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    let stored = null;
    try { stored = localStorage.getItem(KEY); } catch { /* noop */ }
    if (!stored) apply(e.matches ? "dark" : "light");
  });
}
