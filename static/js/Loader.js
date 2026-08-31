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
  let suppressBeforeUnloadOnce = false;

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

  function markSuppressBeforeUnloadOnce() {
    suppressBeforeUnloadOnce = true;
  }

  function clearSuppressBeforeUnload() {
    suppressBeforeUnloadOnce = false;
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

  function shouldSuppressBeforeUnloadForLink(link) {
    return !shouldShowForLink(link);
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
        clearSuppressBeforeUnload();
        if (shouldShowForForm(form)) showLoader();
      });
    });

    // Links → delegated click handles current + future links
    document.addEventListener('click', (event) => {
      const link = event.target.closest('a[href]');
      if (!link) return;

      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        markSuppressBeforeUnloadOnce();
        return;
      }

      if (shouldSuppressBeforeUnloadForLink(link)) {
        markSuppressBeforeUnloadOnce();
        return;
      }

      clearSuppressBeforeUnload();
      showLoader();
    });
  });

  // Leave page
  window.addEventListener('beforeunload', () => {
      if (suppressBeforeUnloadOnce) {
        clearSuppressBeforeUnload();
        return;
      }
      showLoader();
  });

  // On laod / back from bfcache
  window.addEventListener('load', hideLoader);
  window.addEventListener('pageshow', (e) => {
    clearSuppressBeforeUnload();
    if (e.persisted) hideLoader();
  });

  // Hide if back to page
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') return;
    clearSuppressBeforeUnload();
    if (document.visibilityState === 'visible') hideLoader();
  });

  window.AppLoader = {
    show: showLoader,
    hide: hideLoader
  };
})();
