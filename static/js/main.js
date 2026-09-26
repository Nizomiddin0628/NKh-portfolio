import { initTheme } from "./modules/theme.js";
import { initHeader, initFilter } from "./modules/ui.js";
import { initGallery } from "./modules/gallery.js";
import { initCmdK } from "./modules/cmdk.js";
import { initField } from "./modules/field.js";
import { initCarousel } from "./modules/carousel.js";
import { initAnimations } from "./modules/anim.js";
import { initSmoothScroll, initPageTransitions } from "./modules/transitions.js";

const boot = () => {
  // Funksional qatlam — animatsiyadan mustaqil ishlaydi
  initTheme();
  initHeader();
  initGallery();
  initFilter();
  initCmdK();
  const hint = document.querySelector(".kbd-hint");
  if (hint && !/Mac|iPhone|iPad/.test(navigator.platform)) hint.textContent = "Ctrl K";
  initCarousel();
  // Harakat qatlami
  initAnimations();
  initPageTransitions();
  initField();
  initSmoothScroll();

  document.documentElement.classList.add("is-ready");
};

document.readyState === "loading"
  ? document.addEventListener("DOMContentLoaded", boot)
  : boot();