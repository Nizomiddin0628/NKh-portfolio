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

  splitHeadings(gsap);
  revealBlocks(gsap);
  parallaxMedia(gsap);
  countUp(gsap);
  stickyStack(gsap);
  scrollProgress(gsap);
  magnetic(gsap);
  footerReveal(gsap);
  velocitySkew(gsap);

  // Rasmlar yuklangach ScrollTrigger o'lchovlarini qayta hisoblaydi
  window.addEventListener("load", () => window.ScrollTrigger.refresh());
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
      onComplete: () => el.classList.add("is-revealed"),
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

/* ── Prinsiplar ustma-ust yig'iladi ────────────────────────────────────── */

function stickyStack(gsap) {
  const stack = document.querySelector("[data-stack]");
  if (!stack || window.innerWidth < 900) return;

  const cards = gsap.utils.toArray("[data-stack-item]", stack);
  if (cards.length < 2) return;

  cards.forEach((card, i) => {
    if (i === cards.length - 1) return;

    // Har kartochka keyingisi ustiga chiqqanda ozgina kichrayadi va xiralashadi
    gsap.to(card, {
      scale: 1 - (cards.length - i) * 0.035,
      opacity: 0.45,
      ease: "none",
      scrollTrigger: {
        trigger: cards[i + 1],
        start: "top 80%",
        end: "top 30%",
        scrub: true,
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

/* ── Skroll tezligiga qarab yengil egilish ─────────────────────────────── */

function velocitySkew(gsap) {
  const targets = gsap.utils.toArray("[data-skew]");
  if (!targets.length) return;

  const setters = targets.map((el) =>
    gsap.quickSetter(el, "skewY", "deg"));
  const clamp = gsap.utils.clamp(-4, 4);

  window.ScrollTrigger.create({
    onUpdate: (self) => {
      // Tez skrollda elementlar ozgina egiladi, to'xtaganda tekislanadi.
      // 4 daraja — sezilib turadigan, lekin o'qishga xalaqit bermaydigan chegara.
      const skew = clamp(self.getVelocity() / -420);
      setters.forEach((set) => set(skew));
    },
  });

  // Skroll to'xtagach asta tekislanadi
  let idle;
  window.addEventListener("scroll", () => {
    clearTimeout(idle);
    idle = setTimeout(() => {
      gsap.to(targets, { skewY: 0, duration: 0.7, ease: "power3.out" });
    }, 120);
  }, { passive: true });
}