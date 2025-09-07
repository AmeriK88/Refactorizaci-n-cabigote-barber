/* cookiesConsent.js — Ca'Bigote (modal 1ª capa + panel 2ª capa) */
(function () {
  const KEY = 'ck-consent-v1';

  // 1ª capa (modal centrado). Si no existe, usaremos banner como fallback (no lo estás usando ya).
  const firstLayerEl = document.getElementById('ck-modal');
  const firstLayer   = () => firstLayerEl ? bootstrap.Modal.getOrCreateInstance(firstLayerEl, { backdrop: 'static', keyboard: false }) : null;
  const banner       = document.getElementById('ck-banner'); // por si lo dejas en alguna página

  // Panel 2ª capa
  const panelEl = document.getElementById('ck-panel');
  const panel   = () => bootstrap.Modal.getOrCreateInstance(panelEl);

  const q = sel => document.querySelector(sel);
  const getVersion = () =>
    document.querySelector('meta[name="application-version"]')?.content || '1.0';

  const defaultConsent = () => ({
    necessary: true,
    preferences: false,
    analytics: false,
    marketing: false,
    thirdparty: false,
    ts: new Date().toISOString(),
    version: getVersion()
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

  // Mostrar 1ª capa si no hay consentimiento previo
  const showFirstLayerIfNeeded = () => {
    if (readConsent()) return;
    if (firstLayerEl) firstLayer()?.show();
    else if (banner) banner.removeAttribute('hidden');
  };

  const openPanel = (e) => {
    e?.preventDefault?.();
    // si el modal de 1ª capa está abierto, ciérralo antes de abrir 2ª capa
    if (firstLayerEl && firstLayerEl.classList.contains('show')) {
      firstLayer()?.hide();
    } else if (banner && !banner.hasAttribute('hidden')) {
      banner.setAttribute('hidden', '');
    }

    const c = readConsent() || defaultConsent();
    // sincroniza switches
    q('#ck-pref').checked       = !!c.preferences;
    q('#ck-analytics').checked  = !!c.analytics;
    q('#ck-marketing').checked  = !!c.marketing;
    q('#ck-thirdparty').checked = !!c.thirdparty;
    panel().show();
  };

  // ====== APLICAR CONSENTIMIENTO EN LA PÁGINA ======
  const applyConsent = (c) => {
    handleMap(c.thirdparty);

    // (Opcional) gatear Instagram embed
    if (c.thirdparty) loadInstagram();
    else removeInstagram();

    // TODO futuro: cargar analytics/pixel sólo si c.analytics / c.marketing
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

  // ====== Instagram embed (opcional) ======
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

  // ====== EVENTOS UI ======
  document.addEventListener('click', (e) => {
    const openBtn = e.target.closest('[data-ck-open]');
    if (openBtn) openPanel(e);
  });

  // aceptar/rechazar (IDs compartidos en modal o banner)
  const onAccept = () => {
    saveConsent({ preferences: true, analytics: true, marketing: true, thirdparty: true });
    firstLayer()?.hide();
    banner?.setAttribute('hidden', '');
  };
  const onReject = () => {
    saveConsent({ preferences: false, analytics: false, marketing: false, thirdparty: false });
    firstLayer()?.hide();
    banner?.setAttribute('hidden', '');
  };

  q('#ck-accept')?.addEventListener('click', onAccept);
  q('#ck-reject')?.addEventListener('click', onReject);

  // Guardar desde 2ª capa
  q('#ck-save')?.addEventListener('click', () => {
    const newC = {
      preferences: q('#ck-pref')?.checked || false,
      analytics:  q('#ck-analytics')?.checked || false,
      marketing:  q('#ck-marketing')?.checked || false,
      thirdparty: q('#ck-thirdparty')?.checked || false
    };
    saveConsent(newC);
    panel().hide();
    firstLayer()?.hide();
    banner?.setAttribute('hidden', '');
  });

  // botón “Permitir y cargar mapa” directo
  document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'enable-maps') {
      e.preventDefault();
      const c = readConsent() || defaultConsent();
      c.thirdparty = true;
      saveConsent(c);
    }
  });

  // Init
  document.addEventListener('DOMContentLoaded', () => {
    const c = readConsent();
    if (c) applyConsent(c);
    showFirstLayerIfNeeded();
  });
})();
