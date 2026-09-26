/**
 * Animatsiya qatlami — GSAP + ScrollTrigger + SplitText.
 *
 * GSAP `base.html` da oddiy <script> orqali yuklanadi (UMD, global `gsap`).
 * Agar CDN yetib kelmasa — bu modul jim ravishda chekinadi va sayt
 * animatsiyasiz, lekin to'liq ishlaydigan holatda qoladi.
 */

const reduced = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const EASE = "power3.out";

/** GSAP mavjudmi va harakat ruxsat etilganmi. */
function ready() {
  return Boolean(window.gsap) && !reduced();
}

/** Animatsiya bo'lmasa kontent baribir ko'rinsin. */
function revealAll() {
  document.documentElement.classList.add("no-anim");
}

export function initAnimations() {
  if (!ready()) return revealAll();

  const { gsap } = window;
  gsap.registerPlugin(window.ScrollTrigger, window.SplitText);

  // Split only after web fonts load. Lines measured with the fallback
  // font break in the wrong places once the real font arrives.
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => {
    splitHeadings(gsap);
    window.ScrollTrigger.refresh();
  });
  revealBlocks(gsap);
  parallaxMedia(gsap);
  countUp(gsap);
  scrollProgress(gsap);
  magnetic(gsap);
  projectCards(gsap);
  heroPortrait(gsap);
  timelineDraw(gsap);

  // Rasmlar yuklangach ScrollTrigger o'lchovlarini qayta hisoblaydi
  window.addEventListener("load", () => window.ScrollTrigger.refresh());

  // Carousels, images and fonts change the page height after load. Without
  // a re-measure, triggers near the bottom keep stale positions and their
  // content can stay hidden.
  let refreshTimer = 0;
  new ResizeObserver(() => {
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => window.ScrollTrigger.refresh(), 150);
  }).observe(document.body);
}

/* ── Sarlavha: qatorlar niqob ostidan ko'tariladi ───────────────────────── */

function splitHeadings(gsap) {
  document.querySelectorAll("[data-split]").forEach((el) => {
    // `mask: "lines"` har qatorga ortiqcha o'rovchi qo'shadi — qator
    // shu o'rovchi chegarasida kesiladi, shuning uchun matn "yo'qdan"
    // paydo bo'lgandek ko'rinadi.
    const split = new window.SplitText(el, {
      type: "lines",
      mask: "lines",
      linesClass: "line",
    });
    el.classList.add("is-split");

    const fromLoad = el.dataset.split === "load";

    gsap.from(split.lines, {
      yPercent: 115,
      opacity: 0,
      duration: 1.05,
      ease: "power4.out",
      stagger: 0.09,
      delay: fromLoad ? 0.15 : 0,
      scrollTrigger: fromLoad ? undefined : {
        trigger: el,
        start: "top 88%",
        once: true,
      },
      onComplete: () => {
        el.classList.add("is-revealed");
        split.revert();
      },
    });
  });
}

/* ── Bloklar: pastdan suzib chiqadi ────────────────────────────────────── */

function revealBlocks(gsap) {
  // Guruh ichidagi bolalar navbat bilan
  document.querySelectorAll("[data-reveal-group]").forEach((group) => {
    const children = gsap.utils.toArray(group.children);
    if (!children.length) return;

    gsap.from(children, {
      y: 40,
      opacity: 0,
      duration: 0.95,
      ease: EASE,
      stagger: 0.11,
      scrollTrigger: { trigger: group, start: "top 85%", once: true },
    });
  });

  // Yakka elementlar
  gsap.utils.toArray("[data-reveal]").forEach((el) => {
    if (el.closest("[data-reveal-group]")) return;

    gsap.from(el, {
      y: 32,
      opacity: 0,
      duration: 0.9,
      ease: EASE,
      delay: Number(el.dataset.revealDelay || 0) / 1000,
      scrollTrigger: { trigger: el, start: "top 88%", once: true },
    });
  });
}

/* ── Rasm parallaksi ───────────────────────────────────────────────────── */

function parallaxMedia(gsap) {
  gsap.utils.toArray("[data-parallax]").forEach((wrapper) => {
    const img = wrapper.querySelector("img") || wrapper.firstElementChild;
    if (!img) return;

    const depth = Number(wrapper.dataset.parallax) || 14;

    // Rasm konteynerdan kattaroq turadi, keyin skroll bilan siljiydi.
    gsap.set(img, { scale: 1 + depth / 100, willChange: "transform" });

    gsap.fromTo(img,
      { yPercent: -depth / 2 },
      {
        yPercent: depth / 2,
        ease: "none",
        scrollTrigger: {
          trigger: wrapper,
          start: "top bottom",
          end: "bottom top",
          scrub: true,
        },
      },
    );
  });

  // Katta rasmlar niqob ostidan ochiladi
  gsap.utils.toArray("[data-mask-reveal]").forEach((el) => {
    gsap.fromTo(el,
      { clipPath: "inset(14% 14% 14% 14% round 24px)" },
      {
        clipPath: "inset(0% 0% 0% 0% round 20px)",
        ease: "none",
        scrollTrigger: {
          trigger: el,
          start: "top 90%",
          end: "top 45%",
          scrub: 0.6,
        },
      },
    );
  });
}

/* ── Raqamlar sanaladi ─────────────────────────────────────────────────── */

function countUp(gsap) {
  gsap.utils.toArray("[data-count]").forEach((el) => {
    const end = parseFloat(el.dataset.count);
    if (Number.isNaN(end)) return;

    const suffix = el.dataset.countSuffix || "";
    const counter = { value: 0 };

    gsap.to(counter, {
      value: end,
      duration: 1.8,
      ease: "power2.out",
      scrollTrigger: { trigger: el, start: "top 92%", once: true },
      onUpdate: () => {
        el.textContent = Math.round(counter.value).toLocaleString() + suffix;
      },
    });
  });
}


/* ── O'qish progressi ──────────────────────────────────────────────────── */

function scrollProgress(gsap) {
  const bar = document.querySelector("[data-progress]");
  const target = document.querySelector("[data-progress-target]");
  if (!bar || !target) return;

  gsap.to(bar, {
    scaleX: 1,
    ease: "none",
    scrollTrigger: {
      trigger: target,
      start: "top top",
      end: "bottom bottom",
      scrub: 0.3,
    },
  });
}

/* ── Magnit tugmalar ───────────────────────────────────────────────────── */

function magnetic(gsap) {
  if (!window.matchMedia("(pointer: fine)").matches) return;

  document.querySelectorAll("[data-magnetic]").forEach((el) => {
    const strength = Number(el.dataset.magnetic) || 0.3;
    const label = el.querySelector("[data-magnetic-label]") || el.firstElementChild;

    const move = (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - (r.left + r.width / 2)) * strength;
      const y = (e.clientY - (r.top + r.height / 2)) * strength;

      gsap.to(el, { x, y, duration: 0.6, ease: "power3.out" });
      // Ichidagi matn biroz kamroq siljiydi — chuqurlik hissi beradi
      if (label) gsap.to(label, { x: x * 0.35, y: y * 0.35, duration: 0.6, ease: "power3.out" });
    };

    const reset = () => {
      gsap.to(el, { x: 0, y: 0, duration: 0.9, ease: "elastic.out(1, 0.4)" });
      if (label) gsap.to(label, { x: 0, y: 0, duration: 0.9, ease: "elastic.out(1, 0.4)" });
    };

    el.addEventListener("pointermove", move);
    el.addEventListener("pointerleave", reset);
  });
}
/* ── Footer pastdan ochiladi ───────────────────────────────────────────── */

function footerReveal(gsap) {
  const inner = document.querySelector("[data-footer-inner]");
  if (!inner) return;

  // Footer kontenti o'z konteyneri ichida yuqoriga suriladi — natijada
  // sahifa oxiri "parda ko'tarilgandek" ochiladi.
  gsap.fromTo(inner,
    { yPercent: -55 },
    {
      yPercent: 0,
      ease: "none",
      scrollTrigger: {
        trigger: inner.parentElement,
        start: "top bottom",
        end: "bottom bottom",
        scrub: true,
      },
    },
  );
}

/* -- Project cards -------------------------------------------------------
   Three layers, each with one job:
     1. Entrance     - the image opens from the bottom edge, then the text
                       follows line by line.
     2. Scroll depth - the image drifts slower than the card (parallax).
     3. Pointer      - a soft light and a glowing edge follow the cursor,
                       the image leans a few pixels toward it.
   Nothing rotates or skews, so text always stays level.

   Overscan math: the image rests at scale 1.12 (6% spare on each side).
   Parallax (2.5%) + pointer offset (~4px) + hover scale 1.08 (4% spare)
   never exceed that, so no empty edge ever shows.

   Layers 2 and 3 live in gsap.matchMedia: they only run on wide screens
   with a mouse and are reverted automatically if the breakpoint changes. */

function projectCards(gsap) {
  const cards = gsap.utils.toArray(".card");
  if (!cards.length) return;

  const REST = 1;
  const HOVER = 1.03;

  // 1. Entrance
  cards.forEach((card) => {
    const box = card.querySelector(".card__img");
    const img = box && box.querySelector(".card__img-main");
    const text = card.querySelectorAll(".card__meta, .card__title, .card__tagline, .card__foot");

    const tl = gsap.timeline({
      scrollTrigger: { trigger: card, start: "top 85%", once: true },
    });

    if (box) {
      tl.fromTo(box,
        { clipPath: "inset(100% 0% 0% 0%)" },
        {
          clipPath: "inset(0% 0% 0% 0%)",
          duration: 1.2,
          ease: "power4.out",
          onComplete: () => gsap.set(box, { clearProps: "clipPath" }),
        }, 0);
    }
    if (img) {
      tl.fromTo(img, { scale: 1.4 }, { scale: REST, duration: 1.6, ease: "power3.out" }, 0);
    }
    if (text.length) {
      tl.from(text, { y: 18, opacity: 0, duration: 0.8, ease: "power3.out", stagger: 0.07 }, 0.35);
    }
  });

  // 2 + 3. Depth and pointer, desktop only
  const mm = gsap.matchMedia();
  mm.add("(min-width: 900px) and (pointer: fine)", () => {
    const cleanups = [];

    cards.forEach((card) => {
      const img = card.querySelector(".card__img-main");


      const moveX = img ? gsap.quickTo(img, "x", { duration: 0.8, ease: "power3.out" }) : null;
      const moveY = img ? gsap.quickTo(img, "y", { duration: 0.8, ease: "power3.out" }) : null;
      const zoom = img ? gsap.quickTo(img, "scale", { duration: 0.9, ease: "power3.out" }) : null;

      const onMove = (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        card.style.setProperty("--mx", `${(px * 100).toFixed(1)}%`);
        card.style.setProperty("--my", `${(py * 100).toFixed(1)}%`);
        if (img) {
          moveX((px - 0.5) * 6);
          moveY((py - 0.5) * 4);
        }
      };
      const onEnter = () => { if (zoom) zoom(HOVER); };
      const onLeave = () => {
        if (!img) return;
        moveX(0);
        moveY(0);
        zoom(REST);
      };

      card.addEventListener("pointermove", onMove);
      card.addEventListener("pointerenter", onEnter);
      card.addEventListener("pointerleave", onLeave);

      cleanups.push(() => {
        card.removeEventListener("pointermove", onMove);
        card.removeEventListener("pointerenter", onEnter);
        card.removeEventListener("pointerleave", onLeave);
        card.style.removeProperty("--mx");
        card.style.removeProperty("--my");
      });
    });

    return () => cleanups.forEach((fn) => fn());
  });
}

/* -- Hero portrait: opens upward, image settles from a slight zoom ------ */

function heroPortrait(gsap) {
  const frame = document.querySelector("[data-hero-portrait]");
  if (!frame) return;
  const img = frame.querySelector("img");

  gsap.fromTo(frame,
    { clipPath: "inset(100% 0% 0% 0%)" },
    {
      clipPath: "inset(0% 0% 0% 0%)",
      duration: 1.4,
      ease: "power4.inOut",
      delay: 0.25,
      onComplete: () => gsap.set(frame, { clearProps: "clipPath" }),
    },
  );
  if (img) gsap.fromTo(img, { scale: 1.3 }, { scale: 1, duration: 1.8, ease: "power3.out", delay: 0.25 });
}

/* -- Timeline draws itself while scrolling ------------------------------ */

function timelineDraw(gsap) {
  gsap.utils.toArray("[data-timeline]").forEach((timeline) => {
    const progress = timeline.querySelector(".timeline__progress");
    if (progress) {
      gsap.fromTo(progress, { scaleY: 0 }, {
        scaleY: 1,
        ease: "none",
        scrollTrigger: { trigger: timeline, start: "top 70%", end: "bottom 55%", scrub: 0.4 },
      });
    }
    timeline.querySelectorAll(".timeline__item").forEach((item) => {
      window.ScrollTrigger.create({
        trigger: item,
        start: "top 65%",
        toggleClass: { targets: item, className: "is-reached" },
      });
    });
  });
}
