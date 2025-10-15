/* cookies-banner logic (legacy, safe mode) */
document.addEventListener('DOMContentLoaded', () => {
  // Si el sistema nuevo está presente, NO hacer nada
  if (document.getElementById('ck-modal')) return;

  const modalEl = document.getElementById('cookiesModal');
  if (!modalEl || !window.bootstrap) return;  

  const cookiesModal = bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static' });

  // Usa su propia clave (legacy) pero no interfieras con ck-consent-v1
  const KEY = 'cookiesPreference';

  const setPref = (pref) => {
    localStorage.setItem(KEY, pref);
    cookiesModal.hide();
  };

  modalEl.querySelector('.btn-primary')
         ?.addEventListener('click', () => setPref('accepted'));

  modalEl.querySelector('.btn-outline-secondary')
         ?.addEventListener('click', () => setPref('rejected'));

  const openIfNeeded = () => {
    if (!localStorage.getItem(KEY)) {
      modalEl.removeAttribute('inert'); 
      cookiesModal.show();
    }
  };

  ('requestIdleCallback' in window)
    ? requestIdleCallback(openIfNeeded, { timeout: 500 })
    : window.addEventListener('load', openIfNeeded);

  document.getElementById('privacyPolicyLink')
          ?.addEventListener('click', e => {
            e.preventDefault();
            const target = document.getElementById('privacyPolicyModal');
            if (target) bootstrap.Modal.getOrCreateInstance(target).show();
          });
});
