/**
 * Live project demos.
 *
 * Every project with a demo gets a small SVG "product in motion" instead of
 * a static cover: the camera reads the plate, the receipt is paid and six
 * modules update, the map refreshes. Markup:
 *
 *   <div class="demo" data-demo="smart-yard-gate-automation"></div>
 *   <ol data-demo-steps></ol>      (optional, next to the stage)
 *
 * Rules that keep it cheap on phones:
 *   - a scene module is imported only when its stage is near the viewport;
 *   - it plays only while on screen, the tab is visible and, inside the
 *     carousel, only on the active card; otherwise it pauses or shows a
 *     still "poster" frame;
 *   - prefers-reduced-motion shows the poster frame and never animates;
 *   - each loop builds a fresh scene, so nothing accumulates over time.
 *
 * A scene module exports { duration, i18n, build(svg, kit, t), play(api, scene, t) }.
 * play() is a plain async story: `await api.wait(600)`, `await api.tween(...)`.
 * In poster mode every wait and tween resolves instantly and the story stops
 * at `api.poster()`, which leaves the most telling frame on screen.
 */

const NS = "http://www.w3.org/2000/svg";
const ABORT = Symbol("abort");
const POSTER = Symbol("poster");
const reducedMQ = window.matchMedia("(prefers-reduced-motion: reduce)");

/* ── Small SVG kit, shared by all scenes ─────────────────────────────────── */

export function h(tag, attrs = {}, parent = null) {
  const el = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "text") el.textContent = v;
    else el.setAttribute(k, v);
  }
  if (parent) parent.append(el);
  return el;
}

/** Wrap text into <tspan> lines of at most `max` characters. Returns line count. */
export function wrapText(textEl, str, max, lineHeight) {
  textEl.textContent = "";
  const x = textEl.getAttribute("x") || 0;
  const lines = [];
  let line = "";
  for (const word of String(str).split(/\s+/)) {
    if (!word) continue;
    if (line && (line + " " + word).length > max) { lines.push(line); line = word; }
    else line = line ? line + " " + word : word;
  }
  if (line) lines.push(line);
  lines.forEach((l, i) => h("tspan", { x, dy: i ? lineHeight : 0, text: l }, textEl));
  return lines.length;
}

/** Deterministic random numbers, so a scene looks the same every loop. */
export function rng(seed = 7) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const ease = {
  out: "cubic-bezier(0.16, 1, 0.3, 1)",
  inOut: "cubic-bezier(0.65, 0, 0.35, 1)",
  back: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  lin: "linear",
};

const easeFn = {
  lin: (t) => t,
  out: (t) => 1 - Math.pow(1 - t, 3),
  inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
};

/* ── One run of a scene: waits, tweens and ticks that can pause ─────────── */

class Run {
  constructor({ instant, onStep }) {
    this.instant = instant;
    this.onStep = onStep;
    this.alive = true;
    this.paused = false;
    this.pending = new Set();   // timers waiting to fire
    this.anims = new Set();     // running Web Animations
    this.ticks = new Set();     // running rAF ticks
  }

  _guard() {
    if (!this.alive) throw ABORT;
  }

  /** Sleep that only counts time while the demo is actually visible. */
  wait(ms) {
    this._guard();
    if (this.instant || ms <= 0) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const job = { left: ms, t0: 0, id: 0 };
      job.start = () => {
        job.t0 = performance.now();
        job.id = setTimeout(() => { this.pending.delete(job); resolve(); }, job.left);
      };
      job.stop = () => {
        clearTimeout(job.id);
        job.left -= performance.now() - job.t0;
      };
      job.kill = () => { clearTimeout(job.id); reject(ABORT); };
      this.pending.add(job);
      if (!this.paused) job.start();
    });
  }

  /** Web Animation on an element; the end state stays applied. */
  tween(el, keyframes, { dur = 600, ease: e = ease.out, delay = 0 } = {}) {
    this._guard();
    if (!el) return Promise.resolve();
    const last = Array.isArray(keyframes) ? keyframes[keyframes.length - 1] : keyframes;
    if (this.instant) {
      Object.assign(el.style, toStyle(last));
      return Promise.resolve();
    }
    const anim = el.animate(keyframes, { duration: dur, easing: e, delay, fill: "forwards" });
    this.anims.add(anim);
    if (this.paused) anim.pause();
    return anim.finished.then(
      () => {
        this.anims.delete(anim);
        if (!this.alive) throw ABORT;
        try { anim.commitStyles(); anim.cancel(); } catch { Object.assign(el.style, toStyle(last)); }
      },
      () => { throw ABORT; },
    );
  }

  /** Endless ambient animation (blinking dot, pulsing ring). */
  loop(el, keyframes, opts = {}) {
    if (this.instant || !el) return;
    const anim = el.animate(keyframes, { iterations: Infinity, easing: "ease-in-out", ...opts });
    this.anims.add(anim);
    if (this.paused) anim.pause();
    return anim;
  }

  /** Stop an ambient animation started with loop(). */
  unloop(anim) {
    if (!anim) return;
    anim.cancel();
    this.anims.delete(anim);
  }

  /** Drive anything per frame: fn(progress 0..1). dur = Infinity for ambient ticks. */
  tick(dur, fn, curve = "lin") {
    this._guard();
    const f = easeFn[curve] || easeFn.lin;
    if (this.instant) {
      if (Number.isFinite(dur)) fn(1);
      return Promise.resolve();
    }
    return new Promise((resolve, reject) => {
      const t = { elapsed: 0, last: performance.now() };
      t.frame = (now) => {
        if (!this.alive) { this.ticks.delete(t); return reject(ABORT); }
        if (!this.paused) t.elapsed += Math.min(250, now - t.last);
        t.last = now;
        const p = Number.isFinite(dur) ? Math.min(1, t.elapsed / dur) : t.elapsed;
        try { fn(Number.isFinite(dur) ? f(p) : p); } catch (err) { this.ticks.delete(t); return reject(err); }
        if (Number.isFinite(dur) && p >= 1) { this.ticks.delete(t); return resolve(); }
        t.id = requestAnimationFrame(t.frame);
      };
      t.kill = () => { cancelAnimationFrame(t.id); reject(ABORT); };
      this.ticks.add(t);
      t.id = requestAnimationFrame(t.frame);
    });
  }

  /** Background task that dies with the run (never runs in poster mode). */
  spawn(fn) {
    if (this.instant) return;
    Promise.resolve().then(fn).catch((err) => { if (err !== ABORT) console.error(err); });
  }

  /** Type text into an SVG <text>/<tspan>. */
  type(el, str, cps = 28) {
    const s = String(str);
    return this.tick((s.length / cps) * 1000, (p) => { el.textContent = s.slice(0, Math.round(p * s.length)); });
  }

  /** Count a number up inside an element. */
  count(el, from, to, dur = 900, fmt = (v) => Math.round(v).toLocaleString("ru-RU")) {
    return this.tick(dur, (p) => { el.textContent = fmt(from + (to - from) * p); }, "out");
  }

  /** Draw a stroke from nothing. */
  draw(el, dur = 800, e = ease.inOut) {
    const len = el.getTotalLength ? el.getTotalLength() : 300;
    el.style.strokeDasharray = `${len}`;
    el.style.strokeDashoffset = `${len}`;
    return this.tween(el, [{ strokeDashoffset: len }, { strokeDashoffset: 0 }], { dur, ease: e });
  }

  show(el, dur = 450, from = "translateY(6px)") {
    return this.tween(el, [{ opacity: 0, transform: from }, { opacity: 1, transform: "none" }], { dur });
  }

  hide(el, dur = 300) {
    return this.tween(el, [{ opacity: 1 }, { opacity: 0 }], { dur, ease: ease.inOut });
  }

  step(i) {
    this.onStep?.(i);
  }

  poster() {
    if (this.instant) throw POSTER;
  }

  pause() {
    if (this.paused) return;
    this.paused = true;
    this.pending.forEach((j) => j.stop());
    this.anims.forEach((a) => a.pause());
  }

  resume() {
    if (!this.paused || !this.alive) return;
    this.paused = false;
    this.pending.forEach((j) => j.start());
    this.anims.forEach((a) => a.play());
  }

  kill() {
    this.alive = false;
    this.pending.forEach((j) => j.kill());
    this.pending.clear();
    this.anims.forEach((a) => a.cancel());
    this.anims.clear();
    this.ticks.forEach((t) => t.kill());
    this.ticks.clear();
  }
}

function toStyle(frame) {
  const out = {};
  for (const [k, v] of Object.entries(frame || {})) {
    if (k === "offset" || k === "easing" || k === "composite") continue;
    out[k] = v;
  }
  return out;
}

/* ── A stage on the page ─────────────────────────────────────────────────── */

const LANG = (document.documentElement.lang || "en").slice(0, 2);
const VIEW = "0 0 400 250";

class Stage {
  constructor(el) {
    this.el = el;
    this.slug = el.dataset.demo;
    this.mod = null;
    this.run = null;
    this.loading = null;
    this.onScreen = false;
    this.item = el.closest("[data-carousel-item]");
    this.panel = el.closest("[data-demo-panel]");
    this.stepsList = this.panel?.querySelector("[data-demo-steps]") || null;
    this.caption = this.panel?.querySelector("[data-demo-caption]") || null;
    this.loopId = 0;
  }

  t() {
    const i18n = this.mod?.i18n || {};
    return i18n[LANG] || i18n.en || {};
  }

  load() {
    if (!this.loading) {
      this.loading = import(`./${this.slug}.js`)
        .then((m) => {
          this.mod = m.default;
          this.el.dataset.demoMs = String(this.mod.duration || 9000);
          this.renderSteps();
          this.showPoster();
        })
        .catch((err) => {
          console.warn("demo", this.slug, err);
          this.el.classList.add("demo--failed");
        });
    }
    return this.loading;
  }

  active() {
    return !this.item || this.item.classList.contains("is-active");
  }

  playable() {
    return this.onScreen && !document.hidden && this.active() && !reducedMQ.matches;
  }

  /** Fresh <svg>, cross-faded over the previous one. */
  mount() {
    const svg = h("svg", { viewBox: VIEW, class: "demo__svg", "aria-hidden": "true", focusable: "false" });
    const old = [...this.el.querySelectorAll(".demo__svg")];
    this.el.append(svg);
    const scene = this.mod.build(svg, { h, wrapText, rng }, this.t()) || {};
    old.forEach((o) => {
      o.classList.add("is-leaving");
      setTimeout(() => o.remove(), 450);
    });
    return { svg, scene };
  }

  renderSteps() {
    const steps = this.t().steps || [];
    if (this.stepsList && steps.length) {
      this.stepsList.innerHTML = "";
      steps.forEach((s, i) => {
        const li = document.createElement("li");
        li.className = "demo-steps__item";
        li.innerHTML = `<span class="demo-steps__n">${String(i + 1).padStart(2, "0")}</span><span class="demo-steps__text"></span>`;
        li.lastElementChild.textContent = s;
        this.stepsList.append(li);
      });
    }
  }

  setStep(i) {
    const steps = this.t().steps || [];
    if (this.stepsList) {
      [...this.stepsList.children].forEach((li, k) => {
        li.classList.toggle("is-current", k === i);
        li.classList.toggle("is-done", k < i);
      });
    }
    if (this.caption && steps[i]) {
      this.caption.textContent = steps[i];
      this.caption.dataset.step = `${String(i + 1).padStart(2, "0")} / ${String(steps.length).padStart(2, "0")}`;
    }
  }

  async showPoster() {
    this.stop();
    const { scene } = this.mount();
    const run = new Run({ instant: true, onStep: (i) => this.setStep(i) });
    try {
      await this.mod.play(run, scene, this.t());
    } catch (err) {
      if (err !== POSTER && err !== ABORT) console.warn("demo poster", this.slug, err);
    }
    run.kill();
    this.el.classList.add("is-ready");
    this.update();
  }

  stop() {
    this.loopId++;
    if (this.run) { this.run.kill(); this.run = null; }
    this.el.classList.remove("is-playing");
  }

  async loop() {
    const id = ++this.loopId;
    this.el.classList.add("is-playing");
    while (id === this.loopId) {
      const run = new Run({ instant: false, onStep: (i) => this.setStep(i) });
      this.run = run;
      if (!this.playable()) run.pause();
      const { scene } = this.mount();
      try {
        await this.mod.play(run, scene, this.t());
        this.el.dispatchEvent(new CustomEvent("demo:end", { bubbles: true }));
        await run.wait(this.mod.rest ?? 1400);
      } catch (err) {
        if (err !== ABORT) { console.warn("demo", this.slug, err); this.stop(); return; }
      }
      run.kill();
      if (id !== this.loopId) return;
    }
  }

  /** Called whenever visibility, tab state or carousel position changes. */
  update() {
    if (!this.mod) return;
    if (reducedMQ.matches) return;
    if (!this.active()) {
      // Left the front of the carousel: back to the still frame,
      // so it starts from the beginning next time it is shown.
      if (this.run) this.showPoster();
      return;
    }
    if (this.playable()) {
      if (this.run) this.run.resume();
      else this.loop();
    } else if (this.run) {
      this.run.pause();
    }
  }
}

/* ── Wiring ──────────────────────────────────────────────────────────────── */

export function initDemos() {
  const nodes = [...document.querySelectorAll("[data-demo]")];
  if (!nodes.length || !("IntersectionObserver" in window)) return;
  const stages = new Map(nodes.map((el) => [el, new Stage(el)]));

  // Import the scene a little before it scrolls into view
  const near = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      near.unobserve(e.target);
      stages.get(e.target).load();
    });
  }, { rootMargin: "300px 0px" });

  // Play only while a good part of it is on screen
  const seen = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      const st = stages.get(e.target);
      st.onScreen = e.isIntersecting;
      st.update();
    });
  }, { threshold: 0.35 });

  stages.forEach((st, el) => {
    near.observe(el);
    seen.observe(el);
    if (st.item) {
      new MutationObserver(() => st.update()).observe(st.item, { attributes: true, attributeFilter: ["class"] });
    }
  });

  document.addEventListener("visibilitychange", () => stages.forEach((st) => st.update()));
  reducedMQ.addEventListener?.("change", () => stages.forEach((st) => (st.mod ? st.showPoster() : null)));
}
