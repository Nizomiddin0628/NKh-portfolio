/**
 * AI assistant widget. Loaded on demand by templates/ai/widget.html.
 *
 *   init(root)        wires the DOM once
 *   open(question)    opens the panel, optionally sends a question
 *
 * Streaming: POST /ai/ask/ answers with NDJSON lines
 *   {"start":true} {"t":"..."} ... {"reset":true} ... {"done":true, ok, answer, actions, sources}
 */
let root, cfg, ui, els, state;

const $ = (sel) => root.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const cookie = (name) => document.cookie.split("; ").find((r) => r.startsWith(name + "="))?.split("=")[1] || "";
const storeKey = () => `ai:chat:${cfg.lang}`;

function loadState() {
  let history = [];
  try { history = JSON.parse(sessionStorage.getItem(storeKey()) || "[]"); } catch (e) { history = []; }
  let session = "";
  try {
    session = sessionStorage.getItem("ai:session") || "";
    if (!session) { session = Math.random().toString(36).slice(2) + Date.now().toString(36); sessionStorage.setItem("ai:session", session); }
  } catch (e) { session = String(Date.now()); }
  return { history: Array.isArray(history) ? history.slice(-30) : [], session, mode: "local", busy: false,
           controller: null, file: null, rec: null, status: null, opened: false };
}

function saveHistory() {
  try { sessionStorage.setItem(storeKey(), JSON.stringify(state.history.slice(-30))); } catch (e) { /* private mode */ }
}

// ── Rendering ──────────────────────────────────────────────────────────────

function scrollDown() { els.log.scrollTop = els.log.scrollHeight; }

function addMsg(role, html, extra = {}) {
  const div = document.createElement("div");
  div.className = `ai-msg ai-msg--${role === "user" ? "user" : "bot"}${extra.error ? " ai-msg--error" : ""}`;
  if (extra.fileUrl) {
    const img = document.createElement("img");
    img.className = "ai-msg__file"; img.src = extra.fileUrl; img.alt = "";
    div.appendChild(img);
  }
  const body = document.createElement("div");
  body.className = "ai-msg__body";
  body.innerHTML = html;
  div.appendChild(body);
  if (extra.sources?.length) {
    const ul = document.createElement("ul");
    ul.className = "ai-sources";
    ul.innerHTML = `<li class="ai-sources__label">${esc(ui.sources)}</li>` +
      extra.sources.map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a></li>`).join("");
    div.appendChild(ul);
  }
  els.log.appendChild(div);
  scrollDown();
  return div;
}

function renderHistory() {
  els.log.innerHTML = "";
  for (const m of state.history) addMsg(m.role, m.role === "user" ? esc(m.text) : m.text, { sources: m.sources });
  if (!state.history.length && state.status) addMsg("model", esc(state.status.greeting));
  renderChips();
}

function renderChips() {
  els.chips.innerHTML = "";
  if (state.history.length || !state.status?.chips) return;
  for (const c of state.status.chips) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "ai-chip"; b.textContent = c;
    b.addEventListener("click", () => ask(c));
    els.chips.appendChild(b);
  }
}

function renderActions(list) {
  if (!cfg.owner) return;
  for (const a of list || []) {
    if (els.actions.querySelector(`[data-action-id="${a.id}"]`)) continue;
    const card = document.createElement("div");
    card.className = "ai-action"; card.dataset.actionId = a.id;
    card.innerHTML = `<div class="ai-action__label">${esc(ui.pending)}</div>
      <div class="ai-action__text">${esc(a.summary)}</div>
      <div class="ai-action__btns"><button type="button" class="is-ok" data-ok>${esc(ui.confirm)}</button>
      <button type="button" data-no>${esc(ui.cancel)}</button></div>`;
    card.querySelector("[data-ok]").addEventListener("click", () => decide(a.id, "confirm", card));
    card.querySelector("[data-no]").addEventListener("click", () => decide(a.id, "cancel", card));
    els.actions.appendChild(card);
  }
  updateBadge();
}

function updateBadge() {
  const n = els.actions.querySelectorAll(".ai-action:not(.is-done):not(.is-failed):not(.is-cancelled)").length;
  els.badge.hidden = !n;
  els.badge.textContent = n;
}

async function decide(id, verb, card) {
  card.querySelectorAll("button").forEach((b) => (b.disabled = true));
  try {
    const r = await fetch(`${cfg.urls.actions}${id}/${verb}/`, { method: "POST", headers: { "X-CSRFToken": cookie("csrftoken") } });
    const data = await r.json();
    const st = data.action?.status || (data.ok ? "done" : "failed");
    card.classList.add(`is-${st}`);
    const label = st === "done" ? ui.done : st === "cancelled" ? ui.cancelled : ui.failed;
    card.querySelector(".ai-action__btns").innerHTML = `<span>${esc(label)}${data.action?.result ? " · " + esc(data.action.result) : ""}${data.error ? " · " + esc(data.error) : ""}</span>`;
  } catch (e) {
    card.querySelectorAll("button").forEach((b) => (b.disabled = false));
  }
  updateBadge();
}

function setBusy(on) {
  state.busy = on;
  root.dataset.busy = on ? "true" : "false";
  els.input.disabled = false;
  els.send.disabled = false;
  if (!on) autosize();
}

function autosize() {
  els.input.style.height = "auto";
  const h = els.input.scrollHeight;
  els.input.style.height = Math.min(h, 140) + "px";
  els.input.style.overflowY = h > 140 ? "auto" : "hidden";   // no scrollbar arrows on a one-line field
}

// ── Talking to the server ──────────────────────────────────────────────────

async function fetchStatus() {
  try {
    const r = await fetch(`${cfg.urls.status}?lang=${cfg.lang}`, { credentials: "same-origin" });
    state.status = await r.json();
  } catch (e) {
    state.status = { enabled: false, greeting: ui.offline, chips: [] };
  }
  if (state.status.features) {
    els.attach.hidden = !state.status.features.attach;
    els.mic.hidden = !(state.status.features.voice && navigator.mediaDevices?.getUserMedia);
    els.mode.hidden = !state.status.features.web;
  }
  if (state.status.actions) renderActions(state.status.actions);
}

async function ask(text, file) {
  text = (text || "").trim();
  if (state.busy || (!text && !file)) return;
  if (state.status && !state.status.enabled) {
    addMsg("model", `${esc(ui.disabled)} <a href="${esc(cfg.contact)}">${esc(ui.contact)}</a>`, { error: true });
    return;
  }
  const history = state.history.slice(-8).map((m) => ({ role: m.role, text: m.text }));
  const fileUrl = file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null;
  addMsg("user", esc(text || (file ? file.name : "")), { fileUrl });
  state.history.push({ role: "user", text: text || (file ? `[${file.name}]` : "") });
  saveHistory();
  els.chips.innerHTML = "";
  els.input.value = ""; autosize();
  clearFile();

  const bot = addMsg("model", `<span class="ai-thinking" aria-label="${esc(ui.thinking)}"><i></i><i></i><i></i></span>`);
  const body = bot.querySelector(".ai-msg__body");
  setBusy(true);
  const controller = new AbortController();
  state.controller = controller;

  const fd = new FormData();
  fd.append("q", text); fd.append("lang", cfg.lang); fd.append("mode", state.mode);
  fd.append("session", state.session); fd.append("page", location.pathname);
  fd.append("history", JSON.stringify(history));
  if (file) fd.append("file", file, file.name);

  let draft = "", done = null, stopped = false;
  try {
    const r = await fetch(cfg.urls.ask, { method: "POST", body: fd, signal: controller.signal,
      headers: { "X-CSRFToken": cookie("csrftoken") }, credentials: "same-origin" });
    if (!r.ok && !r.headers.get("content-type")?.includes("event-stream")) {
      let data = {};
      try { data = await r.json(); } catch (e) { /* ignore */ }
      done = { ok: false, error: data.error || ui.offline };
    } else {
      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done: end } = await reader.read();
        if (end) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split("\n"); buf = lines.pop();
        for (const line of lines) {
          if (!line.trim()) continue;
          let ev; try { ev = JSON.parse(line); } catch (e) { continue; }
          if (ev.t !== undefined) {
            draft += ev.t; body.textContent = draft; bot.classList.add("is-typing"); scrollDown();
          } else if (ev.reset) {
            draft = ""; bot.classList.remove("is-typing");
            body.innerHTML = `<span class="ai-thinking"><i></i><i></i><i></i></span>`;
          } else if (ev.done) { done = ev; }
        }
      }
    }
  } catch (e) {
    if (e.name === "AbortError") stopped = true; else done = { ok: false, error: ui.offline };
  }
  bot.classList.remove("is-typing");
  state.controller = null;
  setBusy(false);

  if (stopped) {
    bot.remove();
    state.history.pop(); saveHistory();
    els.input.value = text; autosize(); els.input.focus();
    return;
  }
  if (!done) done = { ok: false, error: ui.offline };
  if (done.ok) {
    body.innerHTML = done.answer;
    if (done.sources?.length) {
      const ul = document.createElement("ul"); ul.className = "ai-sources";
      ul.innerHTML = `<li class="ai-sources__label">${esc(ui.sources)}</li>` +
        done.sources.map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a></li>`).join("");
      bot.appendChild(ul);
    }
    state.history.push({ role: "model", text: done.answer, sources: done.sources || [] });
    renderActions(done.actions);
  } else {
    bot.classList.add("ai-msg--error");
    const retry = `<div class="ai-msg__meta"><a href="#" data-retry>${esc(ui.retry)}</a> · <a href="${esc(cfg.contact)}">${esc(ui.contact)}</a></div>`;
    body.innerHTML = esc(done.error || ui.offline) + retry;
    body.querySelector("[data-retry]").addEventListener("click", (e) => { e.preventDefault(); bot.remove(); state.history.pop(); saveHistory(); ask(text); });
    state.history.pop();
  }
  saveHistory();
  scrollDown();
}

function stop() {
  state.controller?.abort();
}

// ── Files and voice (owner) ────────────────────────────────────────────────

function setFile(file) {
  if (!file) return;
  const maxMb = state.status?.features?.max_file_mb || 8;
  if (file.size > maxMb * 1024 * 1024) { addMsg("model", esc(ui.file_big.replace(/\d+ ?(MB|МБ)/, maxMb + " MB")), { error: true }); return; }
  state.file = file;
  els.preview.hidden = false;
  els.preview.innerHTML = "";
  if (file.type.startsWith("image/")) {
    const img = document.createElement("img"); img.src = URL.createObjectURL(file); els.preview.appendChild(img);
  }
  const name = document.createElement("span"); name.textContent = file.name; els.preview.appendChild(name);
  const x = document.createElement("button"); x.type = "button"; x.textContent = "✕"; x.setAttribute("aria-label", ui.cancel);
  x.addEventListener("click", clearFile); els.preview.appendChild(x);
  els.input.focus();
}

function clearFile() {
  state.file = null; els.file.value = "";
  els.preview.hidden = true; els.preview.innerHTML = "";
}

async function toggleRecording() {
  if (state.rec) { state.rec.stop(); return; }
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch (e) { addMsg("model", esc(ui.mic_denied), { error: true }); return; }
  const mime = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg"].find((m) => MediaRecorder.isTypeSupported(m)) || "";
  const rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
  const chunks = [];
  let cancelled = false;
  const started = Date.now();
  const row = document.createElement("div");
  row.className = "ai-rec";
  row.innerHTML = `<b>0:00</b><span>${esc(ui.recording)}</span><button type="button" class="ai-icon" data-cancel-rec aria-label="${esc(ui.cancel_rec)}">✕</button>`;
  els.input.hidden = true; els.input.after(row);
  const tick = setInterval(() => { const s = Math.floor((Date.now() - started) / 1000); row.querySelector("b").textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; if (s >= 120) rec.stop(); }, 500);
  row.querySelector("[data-cancel-rec]").addEventListener("click", () => { cancelled = true; rec.stop(); });
  rec.ondataavailable = (e) => chunks.push(e.data);
  rec.onstop = async () => {
    clearInterval(tick); row.remove(); els.input.hidden = false;
    els.mic.classList.remove("is-rec"); els.mic.setAttribute("aria-pressed", "false");
    stream.getTracks().forEach((t) => t.stop());
    state.rec = null;
    if (cancelled || !chunks.length) return;
    const blob = new Blob(chunks, { type: rec.mimeType || "audio/webm" });
    const fd = new FormData(); fd.append("file", blob, "voice.webm"); fd.append("lang", cfg.lang);
    setBusy(true);
    try {
      const r = await fetch(cfg.urls.transcribe, { method: "POST", body: fd, headers: { "X-CSRFToken": cookie("csrftoken") } });
      const data = await r.json();
      setBusy(false);
      if (data.ok && data.text) ask(data.text); else addMsg("model", esc(data.error || ui.offline), { error: true });
    } catch (e) { setBusy(false); addMsg("model", esc(ui.offline), { error: true }); }
  };
  state.rec = rec;
  els.mic.classList.add("is-rec"); els.mic.setAttribute("aria-pressed", "true");
  rec.start();
}

// ── Open / close ───────────────────────────────────────────────────────────

let lastFocus = null;

export async function open(question) {
  if (!state.opened) { await fetchStatus(); renderHistory(); state.opened = true; }
  lastFocus = document.activeElement;
  root.dataset.open = "true";
  els.panel.hidden = false;
  els.fab.setAttribute("aria-expanded", "true");
  if (matchMedia("(max-width: 640px)").matches) window.scrollLock?.(true);
  scrollDown();
  if (question) { els.input.value = question; autosize(); ask(question); }
  else setTimeout(() => els.input.focus({ preventScroll: true }), 50);
}

export function close() {
  root.dataset.open = "false";
  els.panel.hidden = true;
  els.fab.setAttribute("aria-expanded", "false");
  window.scrollLock?.(false);
  if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true }); else els.fab.focus();
}

export function init(r) {
  if (r.dataset.ready) return;
  root = r;
  cfg = JSON.parse(root.dataset.config || "{}");
  ui = cfg.ui || {};
  state = loadState();
  els = {
    fab: $("[data-ai-open]"), panel: $("[data-ai-panel]"), log: $("[data-ai-log]"), chips: $("[data-ai-chips]"),
    actions: $("[data-ai-actions]"), form: $("[data-ai-form]"), input: $("[data-ai-input]"), send: $("[data-ai-send]"),
    attach: $("[data-ai-attach]"), file: $("[data-ai-file]"), mic: $("[data-ai-mic]"), preview: $("[data-ai-preview]"),
    mode: $("[data-ai-mode]"), badge: $("[data-ai-badge]"), status: $("[data-ai-status]"),
  };
  root.dataset.ready = "1";
  els.input.style.overflowY = "hidden";

  els.fab.addEventListener("click", () => (els.panel.hidden ? open() : close()));
  $("[data-ai-close]").addEventListener("click", close);
  $("[data-ai-new]").addEventListener("click", () => {
    stop(); state.history = []; saveHistory(); els.actions.innerHTML = ""; updateBadge(); renderHistory(); els.input.focus();
  });
  els.form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (state.busy) { stop(); return; }
    ask(els.input.value, state.file);
  });
  els.input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); els.form.requestSubmit(); }
  });
  els.input.addEventListener("input", autosize);
  els.input.addEventListener("paste", (e) => {
    const item = [...(e.clipboardData?.items || [])].find((i) => i.type.startsWith("image/"));
    if (item) { e.preventDefault(); setFile(item.getAsFile()); }
  });
  els.attach.addEventListener("click", () => els.file.click());
  els.file.addEventListener("change", () => setFile(els.file.files[0]));
  els.mic.addEventListener("click", toggleRecording);
  els.mode.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
    state.mode = b.dataset.mode;
    els.mode.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    els.status.textContent = state.mode === "web" ? `${ui.owner} · ${ui.mode_web}` : ui.owner;
  }));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !els.panel.hidden) { e.stopPropagation(); close(); }
  });
  window.__aiWidget = { open, close, ask };
}
