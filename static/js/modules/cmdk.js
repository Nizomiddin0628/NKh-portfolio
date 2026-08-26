/** Cmd/Ctrl + K buyruq palitrasi. */
export function initCmdK() {
  const palette = document.querySelector("[data-cmdk]");
  if (!palette) return;

  const input = palette.querySelector("[data-cmdk-input]");
  const list = palette.querySelector("[data-cmdk-list]");
  const items = JSON.parse(palette.dataset.cmdk || "[]");
  let filtered = items;
  let cursor = 0;
  let lastFocus = null;

  function render() {
    if (!filtered.length) {
      list.innerHTML = `<p class="cmdk__empty">${palette.dataset.emptyText || "Nothing found"}</p>`;
      return;
    }
    let html = "";
    let group = null;
    filtered.forEach((item, i) => {
      if (item.group !== group) {
        group = item.group;
        html += `<div class="cmdk__group">${group}</div>`;
      }
      html += `<a class="cmdk__item" href="${item.url}" role="option" data-i="${i}"
                  aria-selected="${i === cursor}">${item.label}${
        item.hint ? `<small>${item.hint}</small>` : ""}</a>`;
    });
    list.innerHTML = html;
    list.querySelector('[aria-selected="true"]')?.scrollIntoView({ block: "nearest" });
  }

  function open() {
    lastFocus = document.activeElement;
    palette.dataset.open = "true";
    document.body.style.overflow = "hidden";
    input.value = "";
    filtered = items; cursor = 0;
    render();
    input.focus();
  }

  function close() {
    palette.dataset.open = "false";
    document.body.style.overflow = "";
    lastFocus?.focus();
  }

  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      palette.dataset.open === "true" ? close() : open();
      return;
    }
    if (palette.dataset.open !== "true") return;

    if (e.key === "Escape") { close(); return; }
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!filtered.length) return;
      cursor = (cursor + (e.key === "ArrowDown" ? 1 : -1) + filtered.length) % filtered.length;
      render();
    }
    if (e.key === "Enter" && filtered[cursor]) {
      e.preventDefault();
      window.location.href = filtered[cursor].url;
    }
  });

  input?.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    filtered = q ? items.filter((i) => (i.label + " " + (i.keywords || "")).toLowerCase().includes(q)) : items;
    cursor = 0;
    render();
  });

  list?.addEventListener("mousemove", (e) => {
    const el = e.target.closest("[data-i]");
    if (el && Number(el.dataset.i) !== cursor) { cursor = Number(el.dataset.i); render(); }
  });

  palette.addEventListener("click", (e) => { if (e.target === palette) close(); });
  document.querySelectorAll("[data-cmdk-open]").forEach((b) => b.addEventListener("click", open));
}
