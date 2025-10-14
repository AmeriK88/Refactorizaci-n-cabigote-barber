// loader.js
(function () {
  // --- Elements ---
  const overlay = document.getElementById('overlay');
  const loader  = document.getElementById('loader');

  if (!overlay || !loader) {
    // Evita errores si falta el HTML
    console.warn('[loader] overlay/loader no encontrado en el DOM.');
    return;
  }

  // --- Helpers ---
  const add = (el, cls) => el.classList.add(cls);
  const rm  = (el, cls) => el.classList.remove(cls);

  let showTimer = null;

  function showLoader() {
    // Pequeño delay para evitar “flash” en navegaciones ultrarrápidas
    clearTimeout(showTimer);
    showTimer = setTimeout(() => {
      add(overlay, 'is-visible');
      add(loader, 'visible');
      overlay.setAttribute('aria-hidden', 'false');
    }, 50);
  }

  function hideLoader() {
    clearTimeout(showTimer);
    rm(overlay, 'is-visible');
    rm(loader, 'visible');
    overlay.setAttribute('aria-hidden', 'true');
  }

  // Decide si mostrar loader para un enlace concreto
  function shouldShowForLink(link) {
    const href = link.getAttribute('href');

    // Sin href o anclas internas → no mostramos
    if (!href || href.startsWith('#')) return false;

    // Opt-out manual
    if (link.hasAttribute('data-no-loader')) return false;

    // Descargas / nueva pestaña / externo
    if (link.hasAttribute('download')) return false;
    if (link.target && link.target.toLowerCase() === '_blank') return false;

    // Protocolos especiales
    if (href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) return false;

    // Si es navegación interna o misma SPA, mostramos
    try {
      const url = new URL(href, window.location.href);
      const sameOrigin = url.origin === window.location.origin;
      return sameOrigin; // para externos puedes decidir false si no quieres cubrirlos
    } catch {
      // Si no es URL válida, mejor no mostrar
      return false;
    }
  }

  // Decide si mostrar loader para un form
  function shouldShowForForm(form) {
    // Opt-out manual
    if (form.hasAttribute('data-no-loader')) return false;
    return true;
  }

  // --- Wireup ---
  document.addEventListener('DOMContentLoaded', () => {
    // Oculta por si viene del bfcache con clases enganchadas
    hideLoader();

    // Formularios → mostrar al enviar
    document.querySelectorAll('form').forEach(form => {
      // Evita doble disparo
      if (form.dataset.loaderBound) return;
      form.dataset.loaderBound = '1';

      form.addEventListener('submit', () => {
        if (shouldShowForForm(form)) showLoader();
      });
    });

    // Enlaces → mostrar al navegar
    document.querySelectorAll('a[href]').forEach(link => {
      if (link.dataset.loaderBound) return;
      link.dataset.loaderBound = '1';

      link.addEventListener('click', () => {
        if (shouldShowForLink(link)) showLoader();
      });
    });
  });

  // Mostramos al abandonar la página (navegación tradicional)
  window.addEventListener('beforeunload', () => {
    showLoader();
  });

  // Al cargar / volver del bfcache aseguramos ocultar
  window.addEventListener('load', hideLoader);
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) hideLoader();
  });

  // Si el usuario vuelve a la pestaña, oculta por si quedó enganchado
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') hideLoader();
  });

  // API pública por si necesitas dispararlo manualmente
  window.AppLoader = {
    show: showLoader,
    hide: hideLoader
  };
})();
