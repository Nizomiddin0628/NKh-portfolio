/* Admin: show the per-language fieldsets ("Content - English", ...) as tabs.
   Each tab carries a dot: filled when that language has text, hollow when
   empty (the site then shows English). Opens on the first tab that has a
   validation error, otherwise on English. */
(function () {
  "use strict";

  function headingOf(fs) {
    var h = fs.querySelector(".fieldset-heading, h2");
    return h ? h.textContent.trim() : "";
  }

  function hasText(fs) {
    return Array.prototype.some.call(
      fs.querySelectorAll("input[type=text], input[type=url], textarea"),
      function (el) { return el.value.trim() !== ""; });
  }

  function init() {
    var sets = Array.prototype.filter.call(
      document.querySelectorAll("fieldset.module"),
      function (fs) { return /^Content\b/.test(headingOf(fs)); });
    if (sets.length < 2) return;

    var bar = document.createElement("div");
    bar.className = "lang-tabs";
    bar.setAttribute("role", "tablist");
    sets[0].parentNode.insertBefore(bar, sets[0]);

    var tabs = sets.map(function (fs, i) {
      var label = headingOf(fs).replace(/^Content\s*\S\s*/, "").replace(/\s*\(optional\)\s*$/, "");
      var tab = document.createElement("button");
      tab.type = "button";
      tab.className = "lang-tabs__tab";
      tab.setAttribute("role", "tab");
      tab.textContent = label;

      var dot = document.createElement("span");
      dot.className = "lang-tabs__state";
      tab.appendChild(dot);

      function refresh() {
        var filled = hasText(fs);
        tab.classList.toggle("is-empty", !filled);
        dot.title = filled ? "Has content" : (i === 0 ? "Required" : "Empty - English is shown instead");
      }
      refresh();
      fs.addEventListener("input", refresh);

      var details = fs.querySelector("details");
      if (details) details.open = true;
      fs.classList.add("lang-pane");

      tab.addEventListener("click", function () { select(i); });
      bar.appendChild(tab);
      return tab;
    });

    var hint = document.createElement("span");
    hint.className = "lang-tabs__hint";
    hint.textContent = "Empty languages fall back to English";
    bar.appendChild(hint);

    function select(index) {
      sets.forEach(function (fs, j) { fs.hidden = j !== index; });
      tabs.forEach(function (tab, j) {
        tab.classList.toggle("is-active", j === index);
        tab.setAttribute("aria-selected", String(j === index));
      });
    }

    var withError = sets.findIndex(function (fs) { return fs.querySelector(".errorlist"); });
    select(withError >= 0 ? withError : 0);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
