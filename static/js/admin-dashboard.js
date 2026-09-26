/* Admin dashboard charts (Chart.js).
   Smooth line chart for traffic with a 7 / 14 / 30 day switch, doughnuts
   for sources and devices. Colours are read from the admin theme, and the
   charts are rebuilt when the admin switches between dark and light. */
(function () {
  "use strict";

  var TEAL = "#18b7be";
  var INDIGO = "#6f83ff";
  var PALETTE = [TEAL, INDIGO, "#d9a15b", "#a78bfa", "#f472b6", "#94a3b8"];
  var charts = [];
  var range = 14;

  function cssVar(name, fallback) {
    var value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
  }

  function tail(list, n) { return list.slice(list.length - n); }

  function render() {
    var source = document.getElementById("pf-data");
    if (!source || !window.Chart) return;
    var data = JSON.parse(source.textContent);

    charts.forEach(function (chart) { chart.destroy(); });
    charts = [];

    var text = cssVar("--body-quiet-color", "#888");
    var grid = cssVar("--hairline-color", "#ddd");
    var surface = cssVar("--body-bg", "#fff");
    Chart.defaults.color = text;
    Chart.defaults.borderColor = grid;
    Chart.defaults.font.family = cssVar("--font-family-primary", "sans-serif");

    var formatDay = new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric" });
    var labels = data.labels.map(function (d) { return formatDay.format(new Date(d + "T00:00:00")); });

    /* -- Traffic: smooth lines with a soft gradient fill -- */
    var canvas = document.getElementById("pf-traffic");
    if (canvas) {
      var ctx = canvas.getContext("2d");
      var fill = function (color) {
        var g = ctx.createLinearGradient(0, 0, 0, 290);
        g.addColorStop(0, color + "55");
        g.addColorStop(1, color + "00");
        return g;
      };
      var line = function (label, values, color, width) {
        return {
          label: label, data: tail(values, range),
          borderColor: color, backgroundColor: fill(color), fill: true,
          borderWidth: width, tension: 0.4, cubicInterpolationMode: "monotone",
          pointRadius: 0, pointHoverRadius: 5, pointHoverBackgroundColor: color,
          pointHoverBorderColor: surface, pointHoverBorderWidth: 2,
        };
      };
      var traffic = new Chart(canvas, {
        type: "line",
        data: {
          labels: tail(labels, range),
          datasets: [line("Visitors", data.people, TEAL, 2.5), line("Page views", data.views, INDIGO, 2)],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 8, padding: 18 } },
            tooltip: { padding: 10, boxPadding: 4, usePointStyle: true },
          },
          scales: {
            x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
            y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: grid } },
          },
        },
      });
      traffic._pfSource = data;
      charts.push(traffic);

      document.querySelectorAll("[data-range]").forEach(function (button) {
        button.onclick = function () {
          range = Number(button.dataset.range);
          traffic.data.labels = tail(labels, range);
          traffic.data.datasets[0].data = tail(data.people, range);
          traffic.data.datasets[1].data = tail(data.views, range);
          traffic.update();
          document.querySelectorAll("[data-range]").forEach(function (b) {
            b.classList.toggle("is-active", b === button);
          });
        };
      });
    }

    /* -- Doughnuts -- */
    function doughnut(id, items) {
      var el = document.getElementById(id);
      if (!el) return;
      if (!items.length) { el.parentNode.classList.add("is-empty"); return; }
      charts.push(new Chart(el, {
        type: "doughnut",
        data: {
          labels: items.map(function (i) { return i.label; }),
          datasets: [{
            data: items.map(function (i) { return i.n; }),
            backgroundColor: PALETTE, borderColor: surface, borderWidth: 3, hoverOffset: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "68%",
          plugins: { legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 8, padding: 14 } } },
        },
      }));
    }
    doughnut("pf-sources", data.sources);
    doughnut("pf-devices", data.devices);
  }

  function init() {
    render();
    // Rebuild with the new colours when the admin theme is switched
    document.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest(".theme-toggle")) setTimeout(render, 60);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else window.addEventListener("load", init);
})();
