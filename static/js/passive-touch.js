;(function () {
  let supportsPassive = false;
  try {
    const opts = Object.defineProperty({}, 'passive', {
      get() { supportsPassive = true; }
    });
    window.addEventListener('test', null, opts);
  } catch (e) {}
  if (supportsPassive) {
    const orig = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function (type, listener, options) {
      if ((type === 'touchstart' || type === 'touchmove') &&
          (options === undefined || typeof options === 'boolean')) {
        options = { passive: true, capture: !!options };
      }
      return orig.call(this, type, listener, options);
    };
  }
})();
