const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const navScript = fs.readFileSync(
  path.join(__dirname, "..", "static", "admin", "js", "admin-nav.js"),
  "utf8",
);

class FakeElement {
  constructor(name) {
    this.name = name;
    this.attrs = new Map();
    this.listeners = new Map();
    this.children = [];
    this.parentElement = null;
    this.hidden = false;
    this.offsetParent = {};
    this.classes = new Set();
    this.classList = {
      add: (c) => this.classes.add(c),
      remove: (c) => this.classes.delete(c),
      contains: (c) => this.classes.has(c),
    };
  }
  setAttribute(key, value) { this.attrs.set(key, String(value)); }
  removeAttribute(key) { this.attrs.delete(key); }
  addEventListener(type, handler) {
    this.listeners.set(type, [...(this.listeners.get(type) || []), handler]);
  }
  prepend(...nodes) { this.adopt(nodes, true); }
  append(...nodes) { this.adopt(nodes, false); }
  adopt(nodes, atStart) {
    for (const node of nodes) {
      if (node.parentElement) node.parentElement.children = node.parentElement.children.filter((n) => n !== node);
      node.parentElement = this;
      this.children[atStart ? "unshift" : "push"](node);
    }
  }
  insertBefore(node, ref) {
    this.adopt([node], false);
    this.children.splice(this.children.indexOf(ref), 0, this.children.pop());
  }
  focus() { this.ownerDocument.activeElement = this; }
  querySelectorAll() { return this.focusables || []; }
  closest(selector) { return selector === "#toggle-nav-sidebar" && this.name === "toggle" ? this : null; }
}

function createHarness(initialNarrow) {
  const documentListeners = new Map();
  let mediaChange;
  const media = {
    matches: initialNarrow,
    addEventListener: (_type, handler) => { mediaChange = handler; },
  };
  const els = Object.fromEntries(
    ["toggle", "sidebar", "main", "branding", "container", "header", "content-start"].map((n) => [n, new FakeElement(n)]),
  );
  els.container.children = [els.header, els.main];
  els.main.children = [els.toggle, els.sidebar];
  els.toggle.parentElement = els.main;
  els.sidebar.parentElement = els.main;
  const ids = {
    "toggle-nav-sidebar": els.toggle,
    "nav-sidebar": els.sidebar,
    main: els.main,
    branding: els.branding,
    container: els.container,
    header: els.header,
    "content-start": els["content-start"],
  };
  const classes = new Set();
  const document = {
    activeElement: null,
    body: new FakeElement("body"),
    documentElement: { classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c), contains: (c) => classes.has(c) } },
    getElementById: (id) => ids[id] || null,
    querySelector: () => null,
    createElement: (tag) => Object.assign(new FakeElement(tag), { ownerDocument: document }),
    addEventListener(type, handler) {
      documentListeners.set(type, [...(documentListeners.get(type) || []), handler]);
    },
  };
  for (const el of [...Object.values(els), document.body]) el.ownerDocument = document;
  const context = {
    document,
    window: { matchMedia: () => media },
    Element: FakeElement,
  };
  vm.runInNewContext(navScript, context);

  const fire = (type, event) => (documentListeners.get(type) || []).forEach((h) => h(event));
  const closeButton = () => els.sidebar.children[0].children[1];
  return {
    els,
    document,
    classes,
    closeButton,
    clickToggle() {
      let stopped = false;
      fire("click", { target: els.toggle, stopPropagation: () => { stopped = true; } });
      return stopped;
    },
    key(key, extra = {}) { fire("keydown", { key, preventDefault() {}, ...extra }); },
    resize(narrow) { media.matches = narrow; mediaChange(); },
  };
}

test("narrow viewport: native toggle moves to the header and opens a modal drawer", () => {
  const h = createHarness(true);
  assert.equal(h.els.toggle.parentElement, h.els.branding);
  assert.equal(h.els.toggle.attrs.get("aria-controls"), "nav-sidebar");
  assert.equal(h.els.toggle.attrs.get("aria-expanded"), "false");

  assert.equal(h.clickToggle(), true, "native handler must not run on narrow screens");
  assert.ok(h.els.main.classes.has("cb-nav-open"));
  assert.equal(h.els.toggle.attrs.get("aria-expanded"), "true");
  assert.ok(h.classes.has("cb-nav-lock"));
  assert.equal(h.els.header.attrs.has("inert"), true);
  assert.equal(h.els["content-start"].attrs.has("inert"), true);
  assert.equal(h.els.main.attrs.has("inert"), false);
  assert.equal(h.document.activeElement, h.closeButton());
});

test("Escape and the visible close button close the drawer and restore focus", () => {
  const h = createHarness(true);
  h.clickToggle();
  h.key("Escape");
  assert.equal(h.els.main.classes.has("cb-nav-open"), false);
  assert.equal(h.els.header.attrs.has("inert"), false);
  assert.equal(h.document.activeElement, h.els.toggle);

  h.clickToggle();
  h.closeButton().listeners.get("click")[0]();
  assert.equal(h.els.main.classes.has("cb-nav-open"), false);
  assert.equal(h.classes.has("cb-nav-lock"), false);
});

test("Tab wraps inside the open drawer", () => {
  const h = createHarness(true);
  const first = new FakeElement("first");
  const last = new FakeElement("last");
  first.ownerDocument = last.ownerDocument = h.document;
  h.els.sidebar.focusables = [first, last];
  h.clickToggle();

  last.focus();
  let prevented = false;
  h.key("Tab", { shiftKey: false, preventDefault: () => { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(h.document.activeElement, first);

  h.key("Tab", { shiftKey: true });
  assert.equal(h.document.activeElement, last);
});

test("wide viewport leaves the native sidebar untouched and restores the toggle", () => {
  const h = createHarness(false);
  assert.equal(h.els.toggle.parentElement, h.els.main);
  assert.equal(h.clickToggle(), false);
  assert.equal(h.els.main.classes.has("cb-nav-open"), false);

  h.resize(true);
  h.clickToggle();
  h.resize(false);
  assert.equal(h.els.main.classes.has("cb-nav-open"), false);
  assert.equal(h.els.toggle.parentElement, h.els.main);
  assert.equal(h.els.toggle.attrs.has("aria-expanded"), false);
  assert.equal(h.els.header.attrs.has("inert"), false);
});
