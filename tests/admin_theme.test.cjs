const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const adminThemeScript = fs.readFileSync(
  path.join(__dirname, "..", "static", "admin", "js", "admin-theme.js"),
  "utf8",
);
const chartScript = fs.readFileSync(
  path.join(__dirname, "..", "static", "admin", "js", "citas_dashboard_chart.js"),
  "utf8",
);

function createHarness(withChart = false) {
  const eventHandlers = new Map();
  const windowHandlers = new Map();
  const storage = new Map();
  const cssTokens = {
    light: {
      "--cb-chart-text": "#111",
      "--cb-chart-grid": "#ddd",
      "--cb-chart-bar": "#386",
      "--cb-chart-bar-border": "#275",
      "--cb-chart-tooltip": "#fff",
    },
    dark: {
      "--cb-chart-text": "#eee",
      "--cb-chart-grid": "#444",
      "--cb-chart-bar": "#77c",
      "--cb-chart-bar-border": "#88d",
      "--cb-chart-tooltip": "#222",
    },
  };
  let themeObserver;
  let systemThemeChanged;
  let domReady;
  let chart;

  const root = {
    _theme: "auto",
    data: {},
    addEventListener(name, handler) {
      eventHandlers.set(name, [...(eventHandlers.get(name) || []), handler]);
    },
    dispatchEvent(event) {
      for (const handler of eventHandlers.get(event.type) || []) handler(event);
    },
  };
  Object.defineProperty(root.data, "theme", {
    get: () => root._theme,
    set: (theme) => {
      root._theme = theme;
      if (themeObserver) themeObserver();
    },
  });
  Object.defineProperty(root, "dataset", { get: () => root.data });

  class HTMLSelectElement {}
  const select = Object.assign(Object.create(HTMLSelectElement.prototype), {
    value: "",
    addEventListener(_name, handler) {
      this.change = handler;
    },
  });
  class MutationObserver {
    constructor(callback) {
      themeObserver = callback;
    }
    observe() {}
  }
  class ThemeEvent {
    constructor(type) {
      this.type = type;
    }
  }
  class Chart {
    constructor(_context, config) {
      this.data = config.data;
      this.options = config.options;
      this.updates = [];
      chart = this;
    }
    update(mode) {
      this.updates.push(mode);
    }
    destroy() {}
  }

  const systemMedia = {
    addEventListener(_name, handler) {
      systemThemeChanged = handler;
    },
  };
  const window = {
    Chart: withChart ? Chart : null,
    matchMedia: () => systemMedia,
    addEventListener(name, handler) {
      windowHandlers.set(name, [...(windowHandlers.get(name) || []), handler]);
    },
  };
  const chartWrap = {
    classList: { add() {}, remove() {} },
    setAttribute() {},
  };
  const canvas = {
    dataset: { endpoint: "/admin/citas/data/" },
    hidden: false,
    getContext: () => ({}),
  };
  const elements = {
    "cb-admin-theme": select,
    "chart-citas": canvas,
    "chart-citas-wrap": chartWrap,
    "chart-citas-loading": { hidden: false },
    "chart-citas-error": { hidden: true },
  };
  const document = {
    documentElement: root,
    getElementById: (id) => elements[id] || null,
    addEventListener(name, handler) {
      if (name === "DOMContentLoaded") domReady = handler;
    },
    createElement() {
      throw new Error("Chart.js should already be available in this test.");
    },
    head: { appendChild() {} },
  };
  const context = {
    document,
    window,
    HTMLSelectElement,
    MutationObserver,
    Event: ThemeEvent,
    Chart,
    localStorage: {
      getItem: (key) => storage.get(key),
      setItem: (key, value) => storage.set(key, value),
    },
    fetch: async () => ({
      ok: true,
      json: async () => ({ labels: ["Oct"], counts: [4] }),
    }),
    getComputedStyle: () => {
      const tokens = cssTokens[root.dataset.theme === "dark" ? "dark" : "light"];
      return { getPropertyValue: (name) => tokens[name] };
    },
    console,
  };

  vm.runInNewContext(adminThemeScript, context);
  if (withChart) vm.runInNewContext(chartScript, context);

  return {
    chart: () => chart,
    root,
    select,
    storage,
    fireSystemChange: () => systemThemeChanged(),
    fireStorageChange(newValue) {
      for (const handler of windowHandlers.get("storage") || []) {
        handler({ key: "theme", newValue });
      }
    },
    async loadChart() {
      domReady();
      await new Promise(setImmediate);
    },
  };
}

test("theme preference persists and stays in sync with native and system changes", () => {
  const harness = createHarness();
  const { root, select, storage } = harness;

  select.value = "dark";
  select.change();
  assert.equal(storage.get("theme"), "dark");
  assert.equal(root.dataset.theme, "dark");

  root.dataset.theme = "light";
  assert.equal(select.value, "light");

  harness.fireStorageChange("dark");
  assert.equal(root.dataset.theme, "dark");
  assert.equal(select.value, "dark");

  select.value = "auto";
  select.change();
  harness.fireSystemChange();
  assert.equal(root.dataset.theme, "auto");
});

test("chart colors update for selector, native control, and system changes", async () => {
  const harness = createHarness(true);
  await harness.loadChart();
  const chart = harness.chart();

  harness.select.value = "dark";
  harness.select.change();
  assert.equal(chart.data.datasets[0].backgroundColor, "#77c");
  assert.equal(chart.data.datasets[0].borderColor, "#88d");
  assert.equal(chart.options.plugins.legend.labels.color, "#eee");
  assert.equal(chart.options.plugins.tooltip.backgroundColor, "#222");
  assert.equal(chart.options.scales.x.grid.color, "#444");
  assert.equal(chart.options.scales.y.ticks.color, "#eee");

  harness.root.dataset.theme = "light";
  assert.equal(chart.options.plugins.legend.labels.color, "#111");
  assert.equal(chart.options.plugins.tooltip.backgroundColor, "#fff");
  assert.equal(chart.options.scales.x.grid.color, "#ddd");

  harness.select.value = "auto";
  harness.select.change();
  harness.fireSystemChange();
  assert.equal(chart.data.datasets[0].backgroundColor, "#386");
  assert.equal(chart.options.plugins.legend.labels.color, "#111");
  assert.equal(chart.updates.length, 4);
});
