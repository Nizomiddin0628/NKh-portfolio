/**
 * Silliq skroll (Lenis) + sahifalar orasidagi o'tish (View Transitions API).
 *
 * View Transitions — brauzerning o'z imkoniyati. Chrome, Edge va Safari'da
 * ishlaydi; Firefox'da oddiy fade fallback'i qoladi. Hech qanday SPA
 * router kerak emas: sayt server tomonda render qilinganicha qolaveradi.
 */

const reduced = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ── Skroll qulfi (lightbox va ⌘K uchun) ───────────────────────────────── */

let lenis = null;

window.scrollLock = (locked) => {
  document.body.style.overflow = locked ? "hidden" : "";
  if (lenis) locked ? lenis.stop() : lenis.start();
};

/* ── Lenis ─────────────────────────────────────────────────────────────── */

export async function initSmoothScroll() {
  if (reduced()) return;

  try {
    const { default: Lenis } = await import("lenis");
    lenis = new Lenis({
      lerp: 0.09,
      wheelMultiplier: 1,
      smoothWheel: true,
      autoRaf: false,
    });

    const raf = (time) => {
      lenis.raf(time);
      requestAnimationFrame(raf);
    };
    requestAnimationFrame(raf);

    // Ichki havolalar Lenis orqali skroll qilsin
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", (e) => {
        const target = document.querySelector(link.getAttribute("href"));
        if (!target) return;
        e.preventDefault();
        lenis.scrollTo(target, { offset: -80 });
      });
    });
  } catch {
    // CDN yetib kelmadi — brauzerning odatiy skrolli qoladi
  }
}

/* ── Sahifalar orasidagi o'tish ────────────────────────────────────────── */

export function initPageTransitions() {
  if (reduced()) return;

  const supported = "startViewTransition" in document;

  if (supported) {
    /*
     * Loyiha kartochkasidagi rasm detail sahifasidagi katta rasmga
     * "uchib" o'tadi. Buning uchun ikkala tomonda bir xil
     * `view-transition-name` bo'lishi kerak — uni bosishdan oldin
     * faqat bosilgan kartochkaga beramiz (nom sahifada yagona bo'lishi shart).
     */
    window.addEventListener("pageswap", (e) => {
      if (!e.viewTransition) return;
      const url = new URL(e.activation.entry.url);
      const card = document.querySelector(`a.card[href="${url.pathname}"]`);
      card?.querySelector("img")?.style.setProperty("view-transition-name", "project-media");
    });

    window.addEventListener("pagereveal", (e) => {
      if (!e.viewTransition) return;
      const hero = document.querySelector("[data-hero-media]");
      if (!hero) return;
      hero.style.setProperty("view-transition-name", "project-media");
      e.viewTransition.finished.finally(() =>
        hero.style.removeProperty("view-transition-name"));
    });
    return;
  }

  // Fallback: navigatsiyadan oldin qisqa fade
  document.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (!link) return;
    if (link.target === "_blank" || link.hasAttribute("download")) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;

    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin) return;
    if (url.pathname === location.pathname && url.hash) return;

    e.preventDefault();
    document.documentElement.classList.add("is-leaving");
    setTimeout(() => (location.href = url.href), 220);
  });

  // Orqaga qaytilganda oq ekran qolib ketmasin
  window.addEventListener("pageshow", () =>
    document.documentElement.classList.remove("is-leaving"));
}