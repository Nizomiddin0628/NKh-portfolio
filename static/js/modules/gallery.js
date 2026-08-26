/**
 * Loyiha galereyasi.
 * 1 ta rasm  -> faqat katta rasm, bosilganda lightbox.
 * 2+ rasm    -> asosiysi katta, qolganlari pastda kichik; bosilganda almashadi.
 * Klaviatura: ← → almashtirish, Esc yopish.
 */
export function initGallery() {
  const gallery = document.querySelector("[data-gallery]");
  const lightbox = document.querySelector("[data-lightbox]");
  if (!gallery || !lightbox) return;

  const images = JSON.parse(gallery.dataset.gallery || "[]");
  if (!images.length) return;

  const mainBtn = gallery.querySelector("[data-gallery-main]");
  const mainImg = mainBtn?.querySelector("img");
  const caption = gallery.querySelector("[data-gallery-caption]");
  const thumbs = [...gallery.querySelectorAll("[data-gallery-thumb]")];

  const lbImg = lightbox.querySelector("img");
  const lbCaption = lightbox.querySelector("[data-lightbox-caption]");
  const lbCounter = lightbox.querySelector("[data-lightbox-counter]");

  let current = 0;
  let lastFocus = null;

  /** Katta rasmni almashtirish (lightbox ochilmasdan). */
  function setMain(index) {
    const item = images[index];
    if (!item || !mainImg) return;
    current = index;
    mainImg.src = item.url;
    mainImg.alt = item.alt;
    if (item.width && item.height) mainImg.style.aspectRatio = `${item.width} / ${item.height}`;
    if (caption) caption.textContent = item.caption || "";
    thumbs.forEach((t) => t.setAttribute("aria-current", String(Number(t.dataset.index) === index)));
  }

  function render() {
    const item = images[current];
    lbImg.src = item.url;
    lbImg.alt = item.alt;
    if (lbCaption) lbCaption.textContent = item.caption || item.alt || "";
    if (lbCounter) lbCounter.textContent = `${current + 1} / ${images.length}`;
  }

  function open(index) {
    current = index;
    lastFocus = document.activeElement;
    render();
    lightbox.dataset.open = "true";
    document.body.style.overflow = "hidden";
    lightbox.querySelector("[data-lightbox-close]")?.focus();
  }

  function close() {
    lightbox.dataset.open = "false";
    document.body.style.overflow = "";
    lastFocus?.focus();
  }

  const step = (delta) => {
    current = (current + delta + images.length) % images.length;
    render();
  };

  mainBtn?.addEventListener("click", () => open(current));

  thumbs.forEach((thumb) => {
    const index = Number(thumb.dataset.index);
    // Bir marta bosilsa asosiy rasm almashadi, ikkinchi marta — lightbox ochiladi.
    thumb.addEventListener("click", () => (current === index ? open(index) : setMain(index)));
  });

  lightbox.querySelector("[data-lightbox-close]")?.addEventListener("click", close);
  lightbox.querySelector("[data-lightbox-prev]")?.addEventListener("click", () => step(-1));
  lightbox.querySelector("[data-lightbox-next]")?.addEventListener("click", () => step(1));
  lightbox.addEventListener("click", (e) => { if (e.target === lightbox) close(); });

  document.addEventListener("keydown", (e) => {
    if (lightbox.dataset.open !== "true") return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
    if (e.key === "Tab") { e.preventDefault(); lightbox.querySelector("[data-lightbox-close]")?.focus(); }
  });
}
