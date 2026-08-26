/** Header, mobil menyu, til menyusi, filtr. */
export function initHeader() {
  const header = document.querySelector(".header");
  const nav = document.querySelector("[data-nav]");
  const toggle = document.querySelector("[data-nav-toggle]");

  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  toggle?.addEventListener("click", () => {
    const open = nav.dataset.open === "true";
    nav.dataset.open = String(!open);
    toggle.setAttribute("aria-expanded", String(!open));
  });

  const langBtn = document.querySelector("[data-lang-toggle]");
  const langMenu = document.querySelector("[data-lang-menu]");
  langBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = langMenu.dataset.open === "true";
    langMenu.dataset.open = String(!open);
    langBtn.setAttribute("aria-expanded", String(!open));
  });
  document.addEventListener("click", () => {
    if (langMenu) { langMenu.dataset.open = "false"; langBtn?.setAttribute("aria-expanded", "false"); }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && langMenu?.dataset.open === "true") {
      langMenu.dataset.open = "false"; langBtn.focus();
    }
  });
}

/** Loyihalar filtri — sahifa yangilanmaydi, URL o'zgaradi (havolani ulashish mumkin). */
export function initFilter() {
  const grid = document.querySelector("[data-project-grid]");
  if (!grid) return;
  const filters = document.querySelectorAll("[data-filter]");

  filters.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const tech = link.dataset.filter;

      filters.forEach((f) => f.classList.toggle("is-active", f === link));
      let shown = 0;
      grid.querySelectorAll("[data-tech]").forEach((card) => {
        const match = !tech || card.dataset.tech.split(" ").includes(tech);
        card.hidden = !match;
        if (match) shown += 1;
      });

      const empty = document.querySelector("[data-filter-empty]");
      if (empty) empty.hidden = shown > 0;

      const url = new URL(window.location);
      tech ? url.searchParams.set("tech", tech) : url.searchParams.delete("tech");
      history.replaceState({}, "", url);

      document.querySelector("[data-result-count]")?.replaceChildren(String(shown));
    });
  });
}
