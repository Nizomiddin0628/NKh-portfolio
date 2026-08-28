/**
 * Silliq skroll (Lenis) + sahifalar orasidagi o'tish.
 *
 * O'tish: pastdan gradient panel ko'tarilib ekranni yopadi, keyingi sahifa
 * yuklanganda yuqoriga chiqib ketadi. View Transitions API'dan farqli
 * o'laroq bu barcha brauzerlarda bir xil ishlaydi.
 */

const reduced = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let lenis = null;

/** Lightbox va ⌘K skrollni qulflaydi. */
window.scrollLock = (locked) => {
  document.body.style.overflow = locked ? "hidden" : "";
  if (lenis) locked ? lenis.stop() : lenis.start();
};

/* ── Lenis ─────────────────────────────────────────────────────────────── */

export async function initSmoothScroll() {
  if (reduced()) return;

  try {
    const { default: Lenis } = await import("lenis");
    lenis = new Lenis({ lerp: 0.085, smoothWheel: true, autoRaf: false });

    // Lenis va ScrollTrigger bitta rAF siklida ishlashi kerak,
    // aks holda scrub animatsiyalari kechikadi.
    if (window.ScrollTrigger) {
      lenis.on("scroll", window.ScrollTrigger.update);
      window.gsap?.ticker.add((time) => lenis.raf(time * 1000));
      window.gsap?.ticker.lagSmoothing(0);
    } else {
      const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }

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

/* ── Sahifa o'tishi ────────────────────────────────────────────────────── */

export function initPageTransitions() {
  const panel = document.querySelector("[data-transition]");
  if (!panel || reduced() || !window.gsap) return;

  const { gsap } = window;

  // Kirish: panel yuqoriga chiqib ketadi
  gsap.set(panel, { yPercent: 0 });
  gsap.to(panel, {
    yPercent: -100,
    duration: 0.85,
    ease: "power4.inOut",
    onComplete: () => gsap.set(panel, { visibility: "hidden" }),
  });

  document.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (!link || link.target === "_blank" || link.hasAttribute("download")) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;

    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin) return;
    if (url.pathname === location.pathname) return;   // filtr va anchor'lar
    if (url.protocol !== "http:" && url.protocol !== "https:") return;

    e.preventDefault();

    gsap.set(panel, { visibility: "visible", yPercent: 100 });
    gsap.to(panel, {
      yPercent: 0,
      duration: 0.65,
      ease: "power4.inOut",
      onComplete: () => (location.href = url.href),
    });
  });

  // Orqaga qaytilganda panel qotib qolmasin
  window.addEventListener("pageshow", (e) => {
    if (e.persisted) gsap.set(panel, { visibility: "hidden", yPercent: -100 });
  });
}