
'use strict';

// Run with: node --test tests/js/animations.test.js

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const MODULE = path.join(
  __dirname, '..', '..', 'static', 'js', 'Animations.js'
);

function makeEl({
  style = '',
  attrs = {},
  ancestorAnimated = false
} = {}) {
  const classes = new Set(['animate-on-load']);
  const props = {};

  if (style) props['--a-delay'] = style;

  return {
    dataset: {},

    classList: {
      add: c => classes.add(c),
      remove: c => classes.delete(c),
      contains: c => classes.has(c)
    },

    style: {
      getPropertyValue: k => props[k] || '',
      setProperty: (k, v) => {
        props[k] = v;
      }
    },

    hasAttribute: k =>
      Object.prototype.hasOwnProperty.call(attrs, k),

    getAttribute: k => attrs[k] ?? null,

    parentElement: {
      closest: () => (ancestorAnimated ? {} : null)
    },

    props
  };
}

function setup(items, { reduce = false, io = true } = {}) {
  const observers = [];
  const htmlClasses = new Set();
  const listeners = [];

  delete globalThis.IntersectionObserver;

  Object.assign(globalThis, {
    document: {
      readyState: 'complete',

      documentElement: {
        classList: {
          add: c => htmlClasses.add(c),
          remove: c => htmlClasses.delete(c),
          contains: c => htmlClasses.has(c)
        }
      },

      querySelectorAll: () => items
    },

    matchMedia: () => ({ matches: reduce }),

    requestAnimationFrame: cb => cb(),

    addEventListener: (type, fn) => {
      listeners.push([type, fn]);
    }
  });

  if (io) {
    globalThis.IntersectionObserver = function (cb) {
      this.cb = cb;
      this.targets = new Set();
      this.unobserved = [];
      this.disconnected = false;

      this.observe = el => {
        this.targets.add(el);
      };

      this.unobserve = el => {
        this.targets.delete(el);
        this.unobserved.push(el);
      };

      this.disconnect = () => {
        this.disconnected = true;
        this.targets.clear();
      };

      observers.push(this);
    };
  }

  delete require.cache[require.resolve(MODULE)];

  return {
    mod: require(MODULE),
    observers,
    htmlClasses,
    listeners
  };
}

function fire(observer, elements) {
  observer.cb(
    elements.map(target => ({
      isIntersecting: true,
      target
    })),
    observer
  );
}

test('explicit --a-delay is preserved and data-animate-delay applied', () => {
  const a = makeEl({ style: '120ms' });
  const b = makeEl({
    attrs: { 'data-animate-delay': '200' }
  });

  const { mod, observers } = setup([a, b]);

  mod.init();
  fire(observers[0], [a, b]);

  assert.equal(a.props['--a-delay'], '120ms');
  assert.equal(b.props['--a-delay'], '200ms');

  assert.ok(a.classList.contains('loaded'));
  assert.ok(b.classList.contains('loaded'));
});

test('inline delay takes precedence over data-animate-delay', () => {
  const el = makeEl({
    style: '125ms',
    attrs: { 'data-animate-delay': '600' }
  });

  const { mod, observers } = setup([el]);

  mod.init();
  fire(observers[0], [el]);

  assert.equal(el.props['--a-delay'], '125ms');
});

test('data-animate-delay is capped at 1000ms', () => {
  const el = makeEl({
    attrs: { 'data-animate-delay': '2500' }
  });

  const { mod, observers } = setup([el]);

  mod.init();
  fire(observers[0], [el]);

  assert.equal(el.props['--a-delay'], '1000ms');
});

test('invalid data-animate-delay becomes zero', () => {
  const el = makeEl({
    attrs: { 'data-animate-delay': 'invalid' }
  });

  const { mod, observers } = setup([el]);

  mod.init();
  fire(observers[0], [el]);

  assert.equal(el.props['--a-delay'], '0ms');
});

test('auto delay is staggered and capped', () => {
  const els = Array.from(
    { length: 12 },
    () => makeEl()
  );

  const { mod, observers } = setup(els);

  mod.init();
  fire(observers[0], els);

  assert.equal(els[0].props['--a-delay'], '0ms');
  assert.equal(els[1].props['--a-delay'], '70ms');
  assert.equal(els[2].props['--a-delay'], '140ms');
  assert.equal(els[5].props['--a-delay'], '350ms');
  assert.equal(els[11].props['--a-delay'], '350ms');

  assert.ok(
    els.every(el => el.classList.contains('loaded'))
  );
});

test('stagger follows DOM order, not observer entry order', () => {
  const a = makeEl();
  const b = makeEl();
  const c = makeEl();

  const { mod, observers } = setup([a, b, c]);

  mod.init();

  fire(observers[0], [c, a, b]);

  assert.equal(a.props['--a-delay'], '0ms');
  assert.equal(b.props['--a-delay'], '70ms');
  assert.equal(c.props['--a-delay'], '140ms');
});

test('nested elements receive zero automatic delay', () => {
  const el = makeEl({
    ancestorAnimated: true
  });

  const { mod, observers } = setup([el]);

  mod.init();
  fire(observers[0], [el]);

  assert.equal(el.props['--a-delay'], '0ms');
  assert.ok(el.classList.contains('loaded'));
});

test('data-stagger-off disables automatic delay', () => {
  const a = makeEl();
  const b = makeEl({
    attrs: { 'data-stagger-off': '' }
  });
  const c = makeEl();

  const { mod, observers } = setup([a, b, c]);

  mod.init();
  fire(observers[0], [a, b, c]);

  assert.equal(a.props['--a-delay'], '0ms');
  assert.equal(b.props['--a-delay'], '0ms');
  assert.equal(c.props['--a-delay'], '70ms');
});

test('an element is only revealed once', () => {
  const el = makeEl();

  const { mod, observers } = setup([el]);

  mod.init();

  fire(observers[0], [el]);

  const firstDelay = el.props['--a-delay'];

  fire(observers[0], [el]);

  assert.equal(el.props['--a-delay'], firstDelay);
  assert.ok(el.classList.contains('loaded'));
});

test('data-instant elements are revealed immediately', () => {
  const el = makeEl({
    attrs: { 'data-instant': '' }
  });

  const { mod, observers } = setup([el]);

  mod.init();

  assert.ok(el.classList.contains('loaded'));
  assert.equal(observers[0].targets.has(el), false);
});

test('fallback without IntersectionObserver reveals everything', () => {
  const el = makeEl();

  const { mod, htmlClasses } = setup(
    [el],
    { io: false }
  );

  mod.init();

  assert.ok(el.classList.contains('loaded'));
  assert.equal(htmlClasses.has('anim-js'), false);
});

test('reduced motion reveals everything without staggering', () => {
  const el = makeEl();

  const { mod, observers, htmlClasses } = setup(
    [el],
    { reduce: true }
  );

  mod.init();

  assert.ok(el.classList.contains('loaded'));
  assert.equal(observers.length, 0);
  assert.equal(el.props['--a-delay'], undefined);
  assert.equal(htmlClasses.has('anim-js'), false);
});

test('observer constructor failure never leaves content hidden', () => {
  const el = makeEl();

  const { mod, htmlClasses } = setup([el]);

  globalThis.IntersectionObserver = function () {
    throw new Error('Observer constructor failure');
  };

  mod.init();

  assert.ok(el.classList.contains('loaded'));
  assert.equal(htmlClasses.has('anim-js'), false);
});

test('observer registration failure reveals everything', () => {
  const a = makeEl();
  const b = makeEl();

  const { mod, htmlClasses } = setup([a, b]);

  globalThis.IntersectionObserver = function () {
    this.observe = () => {
      throw new Error('Observer registration failure');
    };

    this.disconnect = () => {};
  };

  mod.init();

  assert.ok(a.classList.contains('loaded'));
  assert.ok(b.classList.contains('loaded'));
  assert.equal(htmlClasses.has('anim-js'), false);
});

test('observer callback failure reveals everything', () => {
  const a = makeEl();
  const b = makeEl();

  const { mod, observers, htmlClasses } = setup([a, b]);

  mod.init();

  assert.ok(htmlClasses.has('anim-js'));

  observers[0].unobserve = () => {
    throw new Error('Observer callback failure');
  };

  fire(observers[0], [a]);

  assert.ok(a.classList.contains('loaded'));
  assert.ok(b.classList.contains('loaded'));
  assert.equal(htmlClasses.has('anim-js'), false);
  assert.equal(observers[0].disconnected, true);
});

test('repeated init creates one observer and one pageshow handler', () => {
  const el = makeEl();

  const {
    mod,
    observers,
    listeners,
    htmlClasses
  } = setup([el]);

  mod.init();
  mod.init();

  assert.equal(observers.length, 1);

  assert.equal(
    listeners.filter(([type]) => type === 'pageshow').length,
    1
  );

  assert.ok(htmlClasses.has('anim-js'));
});

test('bfcache restoration reveals all elements', () => {
  const a = makeEl();
  const b = makeEl();

  const { mod, listeners } = setup([a, b]);

  mod.init();

  const pageshow = listeners.find(
    ([type]) => type === 'pageshow'
  );

  assert.ok(pageshow);

  pageshow[1]({ persisted: true });

  assert.ok(a.classList.contains('loaded'));
  assert.ok(b.classList.contains('loaded'));
});

test('normal pageshow does not force reveal', () => {
  const el = makeEl();

  const { mod, listeners } = setup([el]);

  mod.init();

  const pageshow = listeners.find(
    ([type]) => type === 'pageshow'
  );

  assert.ok(pageshow);

  pageshow[1]({ persisted: false });

  assert.equal(el.classList.contains('loaded'), false);
});
