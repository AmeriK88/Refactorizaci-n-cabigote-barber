// Animation.js
(function () {
  const SELECTOR = '.animate-on-load';

  function reveal(el, delayMs = 0) {
    // Aplica un pequeño escalonado vía CSS var
    el.style.setProperty('--a-delay', `${delayMs}ms`);
    // Forzamos un frame para asegurar que la var se aplica antes del cambio de clase
    requestAnimationFrame(() => el.classList.add('loaded'));
  }

  function init() {
    const items = Array.from(document.querySelectorAll(SELECTOR));
    if (!items.length) return;

    // Respeta accesibilidad: sin animaciones si el usuario no las quiere
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      items.forEach(el => el.classList.add('loaded'));
      return;
    }

    // IntersectionObserver para entrada suave al viewport
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;

        const el = entry.target;
        // Prioridad: data-animate-delay || data-stagger || índice incremental
        // Puedes poner en HTML: data-animate-delay="150" (ms)
        const explicit = el.getAttribute('data-animate-delay');
        const base = explicit ? parseInt(explicit, 10) || 0 : 0;

        // Stagger automático: si el contenedor es un grid/row, escalonamos por posición
        // usamos un índice relativo dentro de su padre
        const siblings = Array.from(el.parentElement?.querySelectorAll(SELECTOR) || []);
        const idx = Math.max(0, siblings.indexOf(el));
        const stagger = el.hasAttribute('data-stagger-off') ? 0 : (idx * 70); // 70ms por ítem

        reveal(el, base + stagger);
        obs.unobserve(el);
      });
    }, {
      root: null,
      threshold: 0.12,
      rootMargin: '0px 0px -10% 0px'
    });

    // Estado inicial (no inline styles: todo via CSS)
    items.forEach(el => {
      // Si quieres que algo esté ya visible sin animar, marca data-instant
      if (el.hasAttribute('data-instant')) {
        el.classList.add('loaded');
      } else {
        io.observe(el);
      }
    });

    // Safety: si vuelve del bfcache
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
