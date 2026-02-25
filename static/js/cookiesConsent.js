(function () {
  const KEY = 'ck-consent-v1';
  const isOfflinePage = location.pathname.endsWith('/offline.html');

  // Helpers / guards
  const hasBootstrap = !!window.bootstrap;
  const q  = (sel) => document.querySelector(sel);
  const qa = (sel) => Array.from(document.querySelectorAll(sel));
  const getVersion = () =>
    document.querySelector('meta[name="application-version"]')?.content || '1.0';

  // 1ª layer & banner
  const firstLayerEl = document.getElementById('ck-modal');
  const firstLayer   = () =>
    (hasBootstrap && firstLayerEl)
      ? bootstrap.Modal.getOrCreateInstance(firstLayerEl, { backdrop: 'static', keyboard: false })
      : null;

  const banner = document.getElementById('ck-banner');

  // 2ª layer (panel)
  const panelEl = document.getElementById('ck-panel');
  const panel   = () =>
    (hasBootstrap && panelEl)
      ? bootstrap.Modal.getOrCreateInstance(panelEl)
      : null;

  // ====== CONSENT ======
  const defaultConsent = () => ({
    necessary:   true,
    preferences: false,
    analytics:   false,
    marketing:   false,
    thirdparty:  false,
    ts:          new Date().toISOString(),
    version:     getVersion(),
  });

  const readConsent = () => {
    try { return JSON.parse(localStorage.getItem(KEY)) || null; }
    catch { return null; }
  };

  const saveConsent = (obj) => {
    const data = { ...defaultConsent(), ...obj, ts: new Date().toISOString(), version: getVersion() };
    localStorage.setItem(KEY, JSON.stringify(data));
    applyConsent(data);
    return data;
  };

  // 1ª layer if no consent
  const showFirstLayerIfNeeded = () => {
    if (isOfflinePage) return;
    if (readConsent()) return;
    if (firstLayerEl) firstLayer()?.show();
    else if (banner) banner.removeAttribute('hidden');
  };

  // ====== APPLY CONSENT TO PAGE ======
  const applyConsent = (c) => {
    handleMap(c.thirdparty);

    // (Opcional) Instagram embed
    if (c.thirdparty) loadInstagram();
    else removeInstagram();

    // TODO: load analytics/pixel
  };

  // ====== MAPS LOADER ======
  const handleMap = (allow) => {
    const ph = document.getElementById('gmaps-placeholder');
    if (!ph) return;

    const iframeExists = ph.querySelector('iframe');
    if (allow && !iframeExists) {
      const src = ph.getAttribute('data-embed-src');
      if (!src) return;
      const iframe = document.createElement('iframe');
      iframe.src = src;
      iframe.title = 'Mapa de la ubicación';
      iframe.loading = 'lazy';
      iframe.referrerPolicy = 'strict-origin-when-cross-origin';
      iframe.allowFullscreen = true;
      iframe.style.width = '100%';
      iframe.style.height = '260px';
      iframe.className = 'rounded shadow-sm';
      ph.innerHTML = '';
      ph.appendChild(iframe);
    }
    if (!allow && iframeExists) {
      ph.innerHTML = `
        <div>
          <p class="mb-2"><strong>Mapa bloqueado por preferencias de cookies.</strong></p>
          <p class="mb-3">Activa “Mapas y terceros” para cargar Google Maps.</p>
          <button type="button" class="btn btn-info btn-sm" id="enable-maps">Permitir y cargar mapa</button>
        </div>`;
    }
  };

  // ====== Instagram embed (optional) ======
  const loadInstagram = () => {
    if (document.getElementById('ig-embed-js')) return;
    const s = document.createElement('script');
    s.id = 'ig-embed-js';
    s.async = true;
    s.src = 'https://www.instagram.com/embed.js';
    document.body.appendChild(s);
  };
  const removeInstagram = () => {
    const s = document.getElementById('ig-embed-js');
    if (s) s.remove();
  };

  // ====== ACCESIBILITY ======
  let lastTrigger = null;
  const defocusToSafePlace = () => (lastTrigger || document.body).focus();

  // TRIGGER MEMORY
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-bs-toggle="modal"], [data-ck-open]');
    if (t) lastTrigger = t;
  });

  firstLayerEl?.addEventListener('hidden.bs.modal', defocusToSafePlace);
  panelEl?.addEventListener('hidden.bs.modal', defocusToSafePlace);

  // ====== UI: OPEN PANEL (2ª LAYER ) ======
  const openPanel = (e) => {
    e?.preventDefault?.();

    // SYNC switches with consent
    const c = readConsent() || defaultConsent();
    const map = {
      '#ck-pref':       !!c.preferences,
      '#ck-analytics':  !!c.analytics,
      '#ck-marketing':  !!c.marketing,
      '#ck-thirdparty': !!c.thirdparty,
    };
    Object.entries(map).forEach(([sel, val]) => {
      const el = q(sel);
      if (el) el.checked = val;
    });

    // If 1ª layer visible - modal hidden
    if (firstLayerEl && firstLayerEl.classList.contains('show')) {
      firstLayerEl.addEventListener('hidden.bs.modal', () => panel()?.show(), { once: true });
      firstLayer()?.hide();
    } else {
      panel()?.show();
    }
  };

  // DELEGATE CLICKS
  document.addEventListener('click', (e) => {
    const openBtn = e.target.closest('[data-ck-open]');
    if (openBtn) openPanel(e);
  });

  // ====== ACCEPT / REJECT (1ª layer) ======
  const onAccept = (e) => {
    saveConsent({ preferences: true, analytics: true, marketing: true, thirdparty: true });
    e?.target?.blur();
    firstLayer()?.hide();
    banner?.setAttribute('hidden', '');
  };
  const onReject = (e) => {
    saveConsent({ preferences: false, analytics: false, marketing: false, thirdparty: false });
    e?.target?.blur();
    firstLayer()?.hide();
    banner?.setAttribute('hidden', '');
  };
  q('#ck-accept')?.addEventListener('click', onAccept);
  q('#ck-reject')?.addEventListener('click', onReject);

  // ====== SAVE from - 2ª layer ======
  q('#ck-save')?.addEventListener('click', () => {
    const newC = {
      preferences: q('#ck-pref')?.checked || false,
      analytics:   q('#ck-analytics')?.checked || false,
      marketing:   q('#ck-marketing')?.checked || false,
      thirdparty:  q('#ck-thirdparty')?.checked || false,
    };
    saveConsent(newC);
    panel()?.hide();
  });

  // BTN “Allow Map” directo
  document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'enable-maps') {
      e.preventDefault();
      const c = readConsent() || defaultConsent();
      c.thirdparty = true;
      saveConsent(c);
    }
  });

  // ====== INIT ======
  document.addEventListener('DOMContentLoaded', () => {
    const c = readConsent();
    if (c) applyConsent(c);
    showFirstLayerIfNeeded();
  });
})();
