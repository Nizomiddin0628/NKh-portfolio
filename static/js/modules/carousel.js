/**
 * Featured projects carousel. One markup, two modes:
 *
 *   swipe (< 900px)   Native CSS scroll-snap strip. Swiping, momentum and
 *                     snapping are the browser's own; neighbours peek in.
 *   stage (>= 900px)  Coverflow. The front card sits in the centre at full
 *                     size, its neighbours behind it, smaller and dimmed.
 *                     Positions rotate on a timer. Clicking a side card
 *                     brings it forward; clicking the front card opens it.
 *
 * Shared: autoplay with a filling dot, prev/next, dots, counter, arrow keys.
 * Autoplay pauses while a finger is down or the mouse rests on the front
 * card, while off-screen, in background tabs, and never runs with
 * prefers-reduced-motion.
 */

const MOBILE = "(max-width: 899px)";
const INTERVAL = { swipe: 3500, stage: 4000 };

export function initCarousel() {
  document.querySelectorAll("[data-carousel]").forEach(setup);
}

function setup(root) {
  const track = root.querySelector("[data-carousel-track]");
  const items = [...root.querySelectorAll("[data-carousel-item]")];
  if (!track || items.length < 2) return;

  const prevBtn = root.querySelector("[data-carousel-prev]");
  const nextBtn = root.querySelector("[data-carousel-next]");
  const dotsBox = root.querySelector("[data-carousel-dots]");
  const counter = root.querySelector("[data-carousel-counter]");

  const mq = window.matchMedia(MOBILE);
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const n = items.length;
  const wrap = (i) => ((i % n) + n) % n;
  const pad = (v) => String(v).padStart(2, "0");

  let mode = null;
  let index = 0;
  let visible = false;
  let holding = false;
  let timer = null;
  let itemObserver = null;

  /* -- Dots -- */
  const dots = items.map((_, i) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "carousel__dot";
    dot.setAttribute("aria-label", `${i + 1} / ${n}`);
    dot.addEventListener("click", () => goTo(i));
    dotsBox?.append(dot);
    return dot;
  });

  /* -- Autoplay -- */
  function stop() {
    clearTimeout(timer);
    timer = null;
    root.dataset.playing = "false";
  }

  function start() {
    stop();
    if (!mode || !visible || holding || reduced || document.hidden) return;
    root.style.setProperty("--autoplay", `${INTERVAL[mode]}ms`);
    void root.offsetWidth;                  // restart the dot fill
    root.dataset.playing = "true";
    timer = setTimeout(() => goTo(index + 1), INTERVAL[mode]);
  }

  const hold = () => { holding = true; stop(); };
  const release = () => { holding = false; start(); };

  /* -- Stage positions -- */
  function place() {
    items.forEach((item, i) => {
      let off = wrap(i - index);
      if (off > n / 2) off -= n;
      item.dataset.pos =
        off === 0 ? "center" :
        off === -1 ? "left" :
        off === 1 ? "right" :
        off < 0 ? "far-left" : "far-right";
      // Only the front card is reachable with Tab
      const link = item.querySelector("a");
      if (link) link.tabIndex = off === 0 ? 0 : -1;
    });
  }

  // Stage cards share one height: the tallest card's natural height.
  // The variable is cleared first so every card is measured unstretched.
  function fitHeight() {
    if (mode !== "stage") return;
    root.style.removeProperty("--stage-h");
    const tallest = Math.max(...items.map((item) => item.firstElementChild?.offsetHeight || 0));
    root.style.setProperty("--stage-h", `${tallest}px`);
    track.style.height = `${tallest + 48}px`;
  }

  /* -- Rendering -- */
  function paint() {
    items.forEach((item, i) => item.classList.toggle("is-active", i === index));
    dots.forEach((dot, i) => dot.setAttribute("aria-current", String(i === index)));
    if (counter) counter.textContent = `${pad(index + 1)} / ${pad(n)}`;
    if (mode === "stage") place();
    start();
  }

  function goTo(i) {
    index = wrap(i);
    if (mode === "swipe") {
      const item = items[index];
      track.scrollTo({
        left: item.offsetLeft - (track.clientWidth - item.clientWidth) / 2,
        behavior: reduced ? "auto" : "smooth",
      });
    }
    paint();
  }

  /* -- Swipe: which card is centred after a manual swipe -- */
  function observeItems() {
    itemObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const i = items.indexOf(entry.target);
        if (i >= 0 && i !== index) {
          index = i;
          paint();
        }
      });
    }, { root: track, threshold: 0.6 });
    items.forEach((item) => itemObserver.observe(item));
  }

  /* -- Mode switch -- */
  function setMode(target) {
    if (mode === target) return;
    mode = target;
    root.dataset.carouselMode = target;

    if (target === "swipe") {
      track.style.height = "";
      root.style.removeProperty("--stage-h");
      items.forEach((item) => {
        delete item.dataset.pos;
        const link = item.querySelector("a");
        if (link) link.tabIndex = 0;
      });
      if (!itemObserver) observeItems();
      requestAnimationFrame(() => goTo(index));
    } else {
      itemObserver?.disconnect();
      itemObserver = null;
      track.scrollLeft = 0;
      paint();
      fitHeight();
    }
  }

  /* -- Events -- */
  prevBtn?.addEventListener("click", () => goTo(index - 1));
  nextBtn?.addEventListener("click", () => goTo(index + 1));

  track.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") { e.preventDefault(); goTo(index + 1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); goTo(index - 1); }
  });

  // Stage: clicking a side card brings it forward instead of navigating.
  // Capture phase, so the page-transition click handler never sees it.
  track.addEventListener("click", (e) => {
    if (mode !== "stage") return;
    const item = e.target.closest("[data-carousel-item]");
    if (!item) return;
    const i = items.indexOf(item);
    if (i !== index) {
      e.preventDefault();
      e.stopPropagation();
      goTo(i);
    }
  }, true);

  // Touch: pause while the finger is down
  track.addEventListener("pointerdown", (e) => { if (e.pointerType !== "mouse") hold(); });
  track.addEventListener("pointerup", (e) => { if (e.pointerType !== "mouse") release(); });
  track.addEventListener("pointercancel", release);

  // Mouse: pause while resting on the front card (or anywhere on the strip)
  items.forEach((item) => {
    item.addEventListener("mouseenter", () => {
      if (mode === "swipe" || item.dataset.pos === "center") hold();
    });
    item.addEventListener("mouseleave", release);
  });

  root.addEventListener("focusin", hold);
  root.addEventListener("focusout", (e) => {
    if (!root.contains(e.relatedTarget)) release();
  });

  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    visible ? start() : stop();
  }, { threshold: 0.35 }).observe(root);

  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));

  // Re-measure when images or fonts load and when the window is resized
  root.querySelectorAll("img").forEach((img) => {
    if (!img.complete) img.addEventListener("load", fitHeight, { once: true });
  });
  if (document.fonts) document.fonts.ready.then(fitHeight);
  let resizeFrame = 0;
  window.addEventListener("resize", () => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(fitHeight);
  });

  setMode(mq.matches ? "swipe" : "stage");
  mq.addEventListener("change", (e) => setMode(e.matches ? "swipe" : "stage"));
}
