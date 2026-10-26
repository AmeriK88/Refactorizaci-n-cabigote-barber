(function (root) {
  'use strict';
  const SELECTOR = '.animate-on-load';
  const STAGGER_MS = 70;
  const MAX_AUTO_DELAY_MS = 350;
  const MAX_DATA_DELAY_MS = 1000;
  let initialized = false;
  let observer = null;
  let known = [];

  function revealNow(el) {
    el.classList.add('loaded');
  }

  function revealAll() {
    root.document.querySelectorAll(SELECTOR).forEach(revealNow);
  }

  function explicitDelay(el) {
    const inline = el.style && el.style.getPropertyValue('--a-delay').trim();
    if (inline) return true;

    if (!el.hasAttribute('data-animate-delay')) return false;

    const raw = el.getAttribute('data-animate-delay');

    const parsed = /^\s*\d+(?:\.\d+)?\s*$/.test(raw || '')
      ? Number(raw)
      : 0;

    el.style.setProperty(
      '--a-delay',
      `${Math.min(parsed, MAX_DATA_DELAY_MS)}ms`
    );

    return true;
  }

  function revealBatch(elements) {
    // Sort by the original DOM order, independent of observer callback ordering.
    elements.sort((a, b) => known.indexOf(a) - known.indexOf(b));
    let staggerIndex = 0;
    elements.forEach(el => {
      if (el.classList.contains('loaded') || el.dataset.animRevealed) return;
      el.dataset.animRevealed = '1';
      const explicit = explicitDelay(el);
      const nested = !!(el.parentElement && el.parentElement.closest(SELECTOR));
      if (!explicit) {
        const delay = (nested || el.hasAttribute('data-stagger-off'))
          ? 0 : Math.min(staggerIndex * STAGGER_MS, MAX_AUTO_DELAY_MS);
        el.style.setProperty('--a-delay', `${delay}ms`);
      }
      if (!explicit && !nested && !el.hasAttribute('data-stagger-off')) staggerIndex++;
      root.requestAnimationFrame(() => revealNow(el));
    });
  }

  function init() {
    if (initialized) return;
    initialized = true;
    const doc = root.document;
    known = Array.from(doc.querySelectorAll(SELECTOR));
    root.addEventListener('pageshow', e => { if (e.persisted) revealAll(); });
    if (!known.length) return;

    try {
      const reduce = root.matchMedia && root.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (reduce || typeof root.IntersectionObserver !== 'function') {
        revealAll();
        return;
      }
      observer = new root.IntersectionObserver((entries, obs) => {
        try {
          const batch = entries.filter(e => e.isIntersecting).map(e => e.target);
          batch.forEach(el => obs.unobserve(el));
          revealBatch(batch);
        } catch (_) {
          revealAll();
          obs.disconnect();
          doc.documentElement.classList.remove('anim-js');
        }
      }, { root: null, threshold: 0.12, rootMargin: '0px 0px -10% 0px' });

      // Register all targets while they remain visible. Only then enable hiding.
      known.forEach(el => {
        if (el.hasAttribute('data-instant')) revealNow(el);
        else observer.observe(el);
      });
      doc.documentElement.classList.add('anim-js');
    } catch (_) {
      if (observer) observer.disconnect();
      revealAll();
      doc.documentElement.classList.remove('anim-js');
    }
  }

  function start() {
    try { init(); }
    catch (_) {
      revealAll();
      root.document.documentElement.classList.remove('anim-js');
    }
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { init: start, _reset() { initialized = false; observer = null; known = []; } };
    return;
  }
  if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', start);
  else start();
})(typeof window !== 'undefined' ? window : globalThis);
