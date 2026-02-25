(function () {
  const SELECTOR = '.animate-on-load';

  function reveal(el, delayMs = 0) {
    // Apply delay
    el.style.setProperty('--a-delay', `${delayMs}ms`);
    // Force frame
    requestAnimationFrame(() => el.classList.add('loaded'));
  }

  function init() {
    const items = Array.from(document.querySelectorAll(SELECTOR));
    if (!items.length) return;

    // Accesibility - reduce animation if needed
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      items.forEach(el => el.classList.add('loaded'));
      return;
    }

    // IntersectionObserver - smooth VP
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;

        const el = entry.target;
        const explicit = el.getAttribute('data-animate-delay');
        const base = explicit ? parseInt(explicit, 10) || 0 : 0;

        // Automatic stagger - 70ms * item
        const siblings = Array.from(el.parentElement?.querySelectorAll(SELECTOR) || []);
        const idx = Math.max(0, siblings.indexOf(el));
        const stagger = el.hasAttribute('data-stagger-off') ? 0 : (idx * 70); 

        reveal(el, base + stagger);
        obs.unobserve(el);
      });
    }, {
      root: null,
      threshold: 0.12,
      rootMargin: '0px 0px -10% 0px'
    });

    // Initial state
    items.forEach(el => {
      if (el.hasAttribute('data-instant')) {
        el.classList.add('loaded');
      } else {
        io.observe(el);
      }
    });

    // Safety: bfcache
    window.addEventListener('pageshow', e => {
      if (e.persisted) items.forEach(el => el.classList.add('loaded'));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
