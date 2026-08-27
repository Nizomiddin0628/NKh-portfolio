/**
 * Motion (motion.dev) ustidagi qatlam.
 *
 * Kutubxona CDN'dan dinamik yuklanadi. Agar yuklanmasa — sayt baribir
 * ishlaydi, faqat animatsiyasiz. Animatsiya hech qachon kontentni
 * ushlab turmasligi kerak.
 */

export const reducedMotion = () =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let cached;

/** Motion'ni bir marta yuklaydi. Xato bo'lsa `false` qaytaradi. */
export async function getMotion() {
  if (cached !== undefined) return cached;
  if (reducedMotion()) return (cached = false);
  try {
    cached = await import("motion");
  } catch {
    cached = false;
  }
  return cached;
}

/** Barcha `[data-reveal]` elementlarini darhol ko'rsatadi (fallback). */
function showAll() {
  document.querySelectorAll("[data-reveal]").forEach((el) => {
    el.classList.add("is-visible");
    el.style.opacity = "";
    el.style.transform = "";
  });
}

/* ── Skroll bo'yicha paydo bo'lish ──────────────────────────────────────── */

export async function initReveal() {
  const items = document.querySelectorAll("[data-reveal]");
  if (!items.length) return;

  const m = await getMotion();
  if (!m) return showAll();

  const { animate, inView, stagger } = m;

  // Guruh: ichidagi bolalar navbat bilan chiqadi
  document.querySelectorAll("[data-reveal-group]").forEach((group) => {
    const children = group.querySelectorAll(":scope > *");
    if (!children.length) return;

    inView(group, () => {
      animate(
        children,
        { opacity: [0, 1], transform: ["translateY(28px)", "translateY(0px)"] },
        { duration: 0.7, delay: stagger(0.08), ease: [0.16, 1, 0.3, 1] },
      );
      group.classList.add("is-visible");
    }, { amount: 0.15 });
  });

  // Yakka elementlar
  items.forEach((el) => {
    if (el.closest("[data-reveal-group]")) return;
    inView(el, () => {
      animate(
        el,
        { opacity: [0, 1], transform: ["translateY(24px)", "translateY(0px)"] },
        {
          duration: 0.75,
          delay: Number(el.dataset.revealDelay || 0) / 1000,
          ease: [0.16, 1, 0.3, 1],
        },
      );
      el.classList.add("is-visible");
    }, { amount: 0.12 });
  });
}

/* ── Sarlavha: so'zma-so'z ko'tarilib chiqadi ───────────────────────────── */

export async function initSplitText() {
  const targets = document.querySelectorAll("[data-split]");
  if (!targets.length) return;

  const m = await getMotion();
  if (!m) return;

  const { animate, stagger } = m;

  targets.forEach((el) => {
    // Matnni so'zlarga bo'lamiz. Har so'z ikki qavatli: tashqi qism kesadi,
    // ichkisi pastdan ko'tariladi.
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = "";
    el.classList.add("split");

    const inners = words.map((word) => {
      const outer = document.createElement("span");
      outer.className = "split__word";
      const inner = document.createElement("span");
      inner.className = "split__inner";
      inner.textContent = word;
      outer.append(inner);
      el.append(outer, document.createTextNode(" "));
      return inner;
    });

    animate(
      inners,
      { transform: ["translateY(105%)", "translateY(0%)"], opacity: [0, 1] },
      { duration: 0.9, delay: stagger(0.045, { startDelay: 0.1 }), ease: [0.16, 1, 0.3, 1] },
    );
  });
}

/* ── Magnit tugmalar ────────────────────────────────────────────────────── */

export function initMagnetic() {
  if (reducedMotion() || !window.matchMedia("(pointer: fine)").matches) return;

  document.querySelectorAll("[data-magnetic]").forEach((el) => {
    const strength = Number(el.dataset.magnetic) || 0.28;
    let raf = null;
    let tx = 0, ty = 0, cx = 0, cy = 0;

    const tick = () => {
      cx += (tx - cx) * 0.18;
      cy += (ty - cy) * 0.18;
      el.style.transform = `translate3d(${cx}px, ${cy}px, 0)`;
      raf = Math.abs(tx - cx) > 0.1 || Math.abs(ty - cy) > 0.1
        ? requestAnimationFrame(tick)
        : (el.style.transform = `translate3d(${tx}px, ${ty}px, 0)`, null);
    };

    el.addEventListener("pointermove", (e) => {
      const r = el.getBoundingClientRect();
      tx = (e.clientX - (r.left + r.width / 2)) * strength;
      ty = (e.clientY - (r.top + r.height / 2)) * strength;
      if (!raf) raf = requestAnimationFrame(tick);
    });

    el.addEventListener("pointerleave", () => {
      tx = 0; ty = 0;
      if (!raf) raf = requestAnimationFrame(tick);
    });
  });
}

/* ── Kartochka: 3D egilish + rasm parallaksi ────────────────────────────── */

export function initTilt() {
  if (reducedMotion() || !window.matchMedia("(pointer: fine)").matches) return;

  document.querySelectorAll("[data-tilt]").forEach((card) => {
    const media = card.querySelector("[data-tilt-media]");
    let raf = null;
    let target = { rx: 0, ry: 0, mx: 0, my: 0 };
    const current = { rx: 0, ry: 0, mx: 0, my: 0 };

    const tick = () => {
      let moving = false;
      for (const key of ["rx", "ry", "mx", "my"]) {
        current[key] += (target[key] - current[key]) * 0.12;
        if (Math.abs(target[key] - current[key]) > 0.01) moving = true;
      }
      card.style.transform =
        `perspective(1100px) rotateX(${current.rx}deg) rotateY(${current.ry}deg)`;
      if (media) {
        media.style.transform =
          `scale(1.06) translate3d(${current.mx}px, ${current.my}px, 0)`;
      }
      raf = moving ? requestAnimationFrame(tick) : null;
    };

    card.addEventListener("pointermove", (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      target = { rx: -py * 5, ry: px * 6, mx: px * 16, my: py * 12 };
      if (!raf) raf = requestAnimationFrame(tick);
    });

    card.addEventListener("pointerleave", () => {
      target = { rx: 0, ry: 0, mx: 0, my: 0 };
      if (!raf) raf = requestAnimationFrame(tick);
    });
  });
}

/* ── Case study: o'qish progressi ───────────────────────────────────────── */

export function initProgress() {
  const bar = document.querySelector("[data-progress]");
  const article = document.querySelector("[data-progress-target]");
  if (!bar || !article) return;

  const update = () => {
    const start = article.offsetTop;
    const total = article.offsetHeight - window.innerHeight;
    const done = Math.min(Math.max((window.scrollY - start) / total, 0), 1);
    bar.style.transform = `scaleX(${done})`;
  };

  update();
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update, { passive: true });
}