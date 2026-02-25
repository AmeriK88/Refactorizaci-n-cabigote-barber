(function () {
  // --- Elements ---
  const overlay = document.getElementById('overlay');
  const loader  = document.getElementById('loader');

  if (!overlay || !loader) {
    // Avoids errors if missing in HTML
    console.warn('[loader] overlay/loader no encontrado en el DOM.');
    return;
  }

  // --- Helpers ---
  const add = (el, cls) => el.classList.add(cls);
  const rm  = (el, cls) => el.classList.remove(cls);

  let showTimer = null;

  function showLoader() {
    // Soft delay - avaid “flash”
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

  // SHOW loader
  function shouldShowForLink(link) {
    const href = link.getAttribute('href');

    // Not withot href → DON´T SHOW
    if (!href || href.startsWith('#')) return false;

    // Opt-out manual
    if (link.hasAttribute('data-no-loader')) return false;

    // Download / new wind / external
    if (link.hasAttribute('download')) return false;
    if (link.target && link.target.toLowerCase() === '_blank') return false;

    // Special guidelines
    if (href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) return false;

    try {
      const url = new URL(href, window.location.href);
      const sameOrigin = url.origin === window.location.origin;
      return sameOrigin;
    } catch {
      // If URL not valid - DON´T SHOW
      return false;
    }
  }

  // Loader show o nforms
  function shouldShowForForm(form) {
    // Opt-out manual
    if (form.hasAttribute('data-no-loader')) return false;
    return true;
  }

  // --- Wireup ---
  document.addEventListener('DOMContentLoaded', () => {
    hideLoader();

    // FORMS → Show when shending
    document.querySelectorAll('form').forEach(form => {
      // Avoids double trigger
      if (form.dataset.loaderBound) return;
      form.dataset.loaderBound = '1';

      form.addEventListener('submit', () => {
        if (shouldShowForForm(form)) showLoader();
      });
    });

    // Links → show when accessing
    document.querySelectorAll('a[href]').forEach(link => {
      if (link.dataset.loaderBound) return;
      link.dataset.loaderBound = '1';

      link.addEventListener('click', () => {
        if (shouldShowForLink(link)) showLoader();
      });
    });
  });

  // Leave page
  window.addEventListener('beforeunload', () => {
    showLoader();
  });

  // On laod / back from bfcache
  window.addEventListener('load', hideLoader);
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) hideLoader();
  });

  // Hide if back to page
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') hideLoader();
  });

  window.AppLoader = {
    show: showLoader,
    hide: hideLoader
  };
})();
