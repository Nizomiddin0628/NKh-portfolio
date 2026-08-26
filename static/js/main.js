import { initTheme } from "./modules/theme.js";
import { initReveal } from "./modules/reveal.js";
import { initGallery } from "./modules/gallery.js";
import { initCmdK } from "./modules/cmdk.js";
import { initHeader, initFilter } from "./modules/ui.js";

const boot = () => {
  initTheme();
  initHeader();
  initReveal();
  initGallery();
  initFilter();
  initCmdK();
};

document.readyState === "loading"
  ? document.addEventListener("DOMContentLoaded", boot)
  : boot();
