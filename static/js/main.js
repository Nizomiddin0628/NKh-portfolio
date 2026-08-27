import { initTheme } from "./modules/theme.js";
import { initHeader, initFilter } from "./modules/ui.js";
import { initGallery } from "./modules/gallery.js";
import { initCmdK } from "./modules/cmdk.js";
import { initCursor } from "./modules/cursor.js";
import { initField } from "./modules/field.js";
import { initSmoothScroll, initPageTransitions } from "./modules/transitions.js";
import {
  initReveal, initSplitText, initMagnetic, initTilt, initProgress,
} from "./modules/motion.js";

const boot = () => {
  // Darhol kerak bo'ladiganlar
  initTheme();
  initHeader();
  initGallery();
  initFilter();
  initCmdK();
  initPageTransitions();

  // Bezak qatlami — sahifa allaqachon ishlayotgan bo'ladi
  initField();
  initCursor();
  initMagnetic();
  initTilt();
  initProgress();
  initSmoothScroll();
  initSplitText();
  initReveal();

  document.documentElement.classList.add("is-ready");
};

document.readyState === "loading"
  ? document.addEventListener("DOMContentLoaded", boot)
  : boot();