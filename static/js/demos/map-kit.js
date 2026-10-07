/* Shared pieces for the map scenes: a projection, roads with casings,
   Interstate shields, labels with halos, Leaflet-style controls, pins and
   heading markers. Colours come from the --map-* tokens in demos.css. */

/** Equirectangular projection, corrected for latitude, fitted to a box. */
export function projector({ lon0, lon1, lat1, latMid, x = 0, y = 0, w }) {
  const kx = w / (lon1 - lon0);
  const ky = kx / Math.cos((latMid * Math.PI) / 180);
  const p = ([lon, lat]) => [x + (lon - lon0) * kx, y + (lat1 - lat) * ky];
  p.kx = kx;
  p.ky = ky;
  return p;
}

export const pathOf = (pts, proj, close = false) =>
  pts.map((pt, i) => `${i ? "L" : "M"}${proj(pt).map((v) => v.toFixed(1)).join(" ")}`).join("") + (close ? "Z" : "");

/** A road: casing under a lighter fill, like every web map draws them. */
export function road(h, parent, d, kind = "road") {
  const w = { hwy: [4.2, 2.6], major: [3, 1.8], road: [2, 1.1], street: [1.3, 0.7] }[kind];
  const isHwy = kind === "hwy";
  h("path", { d, class: isHwy ? "m-hwyc" : "m-roadc", "stroke-width": w[0] }, parent);
  return h("path", { d, class: isHwy ? "m-hwy" : "m-road", "stroke-width": w[1] }, parent);
}

/** Interstate shield: red crown, blue body, white number. */
export function shield(h, parent, x, y, num, s = 1) {
  const g = h("g", { transform: `translate(${x} ${y}) scale(${s})` }, parent);
  const body = "M-7 -6.5 Q-3.5 -8 0 -6.5 Q3.5 -8 7 -6.5 V0 Q7 5 0 7.5 Q-7 5 -7 0 Z";
  h("path", { d: body, fill: "#1c4fa1", stroke: "#fff", "stroke-width": 0.9 }, g);
  h("path", { d: "M-7 -6.5 Q-3.5 -8 0 -6.5 Q3.5 -8 7 -6.5 V-3 H-7 Z", fill: "#c8102e" }, g);
  h("text", { x: 0, y: 3.3, "font-size": num.length > 2 ? 5.6 : 6.4, fill: "#fff", "text-anchor": "middle", class: "db", text: num }, g);
  return g;
}

/** US highway shield: white with a black outline. */
export function usShield(h, parent, x, y, num) {
  const g = h("g", { transform: `translate(${x} ${y})` }, parent);
  h("path", { d: "M-6.5 -6 H6.5 Q7 -2 5 0 Q7 3 4 6.5 H-4 Q-7 3 -5 0 Q-7 -2 -6.5 -6 Z", fill: "#fff", stroke: "#222", "stroke-width": 0.8 }, g);
  h("text", { x: 0, y: 2.6, "font-size": 5.8, fill: "#111", "text-anchor": "middle", class: "db", text: num }, g);
  return g;
}

export function label(h, parent, x, y, text, { size = 8.5, cls = "m-label", anchor = "middle", weight = 500, spacing = 0 } = {}) {
  return h("text", {
    x, y, "font-size": size, class: cls, "text-anchor": anchor, "font-weight": weight,
    "letter-spacing": spacing || undefined, text,
  }, parent);
}

export function city(h, parent, x, y, name, { big = false, dx = 5, dy = 3, anchor = "start" } = {}) {
  h("circle", { cx: x, cy: y, r: big ? 2.6 : 1.9, style: "fill: var(--map-label); stroke: var(--map-halo)", "stroke-width": 1 }, parent);
  return label(h, parent, x + dx, y + dy, name, { size: big ? 9.5 : 8, anchor, weight: big ? 600 : 500 });
}

/** Leaflet-style zoom control and attribution. */
export function controls(h, parent, x, y) {
  const g = h("g", {}, parent);
  h("rect", { x, y, width: 18, height: 36, rx: 3, class: "m-ui", "stroke-width": 1 }, g);
  h("line", { x1: x, x2: x + 18, y1: y + 18, y2: y + 18, class: "m-ui", "stroke-width": 1 }, g);
  h("path", { d: `M${x + 5} ${y + 9}h8M${x + 9} ${y + 5}v8M${x + 5} ${y + 27}h8`, class: "s-tx3", "stroke-width": 1.4, "stroke-linecap": "round", style: "stroke: var(--text-soft)" }, g);
  return g;
}

export function attribution(h, parent, xRight, yBottom, text = "Leaflet | © OpenStreetMap") {
  const w = text.length * 3.6 + 8;
  const g = h("g", {}, parent);
  h("rect", { x: xRight - w, y: yBottom - 10, width: w, height: 10, style: "fill: var(--map-halo)" }, g);
  h("text", { x: xRight - 4, y: yBottom - 3, "font-size": 6, "text-anchor": "end", style: "fill: var(--map-label)", text }, g);
  return g;
}

export function scaleBar(h, parent, x, y, px, text) {
  const g = h("g", {}, parent);
  h("path", { d: `M${x} ${y - 4}V${y}H${x + px}V${y - 4}`, fill: "none", style: "stroke: var(--map-label)", "stroke-width": 1.2 }, g);
  h("text", { x: x + 3, y: y - 6, "font-size": 6.5, class: "m-label", text }, g);
  return g;
}

/** Google-style place pin; tip at (x, y). */
export function pin(h, parent, x, y, { color = "#ea4335", edge = "#b31412", text = "" } = {}) {
  const g = h("g", { transform: `translate(${x} ${y})` }, parent);
  h("ellipse", { cx: 0, cy: 0.5, rx: 3.6, ry: 1.3, fill: "#000", opacity: 0.22 }, g);
  h("path", { d: "M0 0C-1.4-3.6-7-7.4-7-12.6a7 7 0 0 1 14 0C7-7.4 1.4-3.6 0 0Z", fill: color, stroke: edge, "stroke-width": 0.8 }, g);
  const dot = h("circle", { cx: 0, cy: -12.6, r: 2.6, fill: "#fff", opacity: text ? 0 : 0.95 }, g);
  const num = h("text", { x: 0, y: -10.2, "font-size": 7, fill: "#fff", "text-anchor": "middle", class: "db", text }, g);
  return { g, dot, num };
}

/** Fleet marker: a dot with a heading chevron, rotated by `deg`. */
export function vehicle(h, parent, color) {
  const g = h("g", {}, parent);
  const halo = h("circle", { r: 5.6, fill: color, opacity: 0.22 }, g);
  h("circle", { r: 3.9, fill: color, stroke: "#fff", "stroke-width": 1.2 }, g);
  const arrow = h("path", { d: "M0 -2.3 L1.8 1.6 L0 0.7 L-1.8 1.6 Z", fill: "#fff" }, g);
  return { g, halo, arrow };
}

/** Leaflet.markercluster bubble. */
export function cluster(h, parent, x, y, n) {
  const big = n >= 40, mid = n >= 20;
  const outer = big ? "rgba(253,156,115,0.65)" : mid ? "rgba(241,211,87,0.65)" : "rgba(181,226,140,0.65)";
  const inner = big ? "rgba(241,128,23,0.85)" : mid ? "rgba(240,194,12,0.85)" : "rgba(110,204,57,0.85)";
  const g = h("g", { transform: `translate(${x} ${y})` }, parent);
  h("circle", { r: 11, fill: outer }, g);
  h("circle", { r: 8, fill: inner }, g);
  const t = h("text", { x: 0, y: 3, "font-size": 8, fill: "#1b1b1b", "text-anchor": "middle", class: "db", text: String(n) }, g);
  return { g, t };
}
