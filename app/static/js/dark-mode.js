/**
 * Dark mode toggle (same behaviour as the other kvarak projects).
 *
 * The <head> snippet in _skeleton.html applies the saved choice before paint;
 * this script wires up the navbar button, follows the system setting until the
 * user picks a mode, and keeps Chart.js text/grid colours in sync.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "htstatus-dark-mode";
  var root = document.documentElement;
  var toggle = document.getElementById("dark-mode-toggle");
  var icon = document.getElementById("dark-mode-icon");
  var systemQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function isDark() {
    return root.classList.contains("dark-mode");
  }

  function showIcon() {
    if (icon) {
      icon.textContent = isDark() ? "\u2600\uFE0F" : "\uD83C\uDF19";
    }
  }

  function applyChartTheme() {
    if (!window.Chart || !window.Chart.defaults) {
      return;
    }
    var dark = isDark();
    var text = dark ? "#ced4da" : "#666";
    var grid = dark ? "rgba(255, 255, 255, 0.12)" : "rgba(0, 0, 0, 0.1)";
    // New charts pick these up; existing charts cache resolved options, so set them too
    window.Chart.defaults.color = text;
    window.Chart.defaults.borderColor = grid;
    Object.values(window.Chart.instances || {}).forEach(function (chart) {
      var options = chart.options;
      Object.values(options.scales || {}).forEach(function (scale) {
        scale.ticks = Object.assign(scale.ticks || {}, { color: text });
        scale.grid = Object.assign(scale.grid || {}, { color: grid });
        if (scale.pointLabels) {
          scale.pointLabels.color = text;
        }
        if (scale.angleLines) {
          scale.angleLines.color = grid;
        }
      });
      if (options.plugins && options.plugins.legend && options.plugins.legend.labels) {
        options.plugins.legend.labels.color = text;
      }
      if (options.plugins && options.plugins.title) {
        options.plugins.title.color = text;
      }
      chart.update("none");
    });
  }

  function apply(dark) {
    root.classList.toggle("dark-mode", dark);
    showIcon();
    applyChartTheme();
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      var dark = !isDark();
      localStorage.setItem(STORAGE_KEY, String(dark));
      apply(dark);
    });
  }

  // Follow the system setting only until the visitor picks one.
  if (systemQuery) {
    var followSystem = function (event) {
      if (localStorage.getItem(STORAGE_KEY) === null) {
        apply(event.matches);
      }
    };
    if (systemQuery.addEventListener) {
      systemQuery.addEventListener("change", followSystem);
    } else if (systemQuery.addListener) {
      systemQuery.addListener(followSystem);
    }
  }

  showIcon();
  applyChartTheme();
  // Pages may load their own Chart.js copy after this script
  document.addEventListener("DOMContentLoaded", applyChartTheme);
})();
